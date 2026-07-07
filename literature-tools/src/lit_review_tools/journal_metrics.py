from __future__ import annotations

from io import BytesIO
from pathlib import Path

import numpy as np
import pandas as pd
import requests
from tqdm import tqdm

from .common import choose_column, safe_number

try:
    from rapidfuzz import fuzz, process
except ImportError:  # pragma: no cover - exercised when optional speedup is unavailable
    fuzz = None
    process = None

JOURNAL_REPLACEMENTS = {
    "intl": "international",
    "int": "international",
    "natl": "national",
    "nat": "national",
    "sci": "science",
    "med": "medical",
    "res": "research",
    "tech": "technology",
    "eng": "engineering",
    "phys": "physics",
    "chem": "chemistry",
    "bio": "biology",
    "env": "environmental",
    "mgmt": "management",
    "dev": "development",
    "edu": "education",
    "univ": "university",
    "j.": "journal",
    "jr.": "journal",
    "jrnl.": "journal",
    "proc.": "proceedings",
    "rev.": "review",
}


def standardize_journal_name(value: object) -> str:
    import re

    if not isinstance(value, str):
        return ""
    text = value.lower().strip().replace("&", "and")
    text = re.sub(r"[-:]", " ", text)
    text = re.sub(r"\([^)]*?(print|online|www|web|issn|doi).*?\)", "", text, flags=re.IGNORECASE)
    for abbr, full in JOURNAL_REPLACEMENTS.items():
        text = re.sub(rf"\b{re.escape(abbr)}\b", full, text, flags=re.IGNORECASE)
    text = re.sub(r"[^\w\s]", " ", text)
    return " ".join(text.split())


def load_reference_df(source: str) -> pd.DataFrame:
    if source.startswith(("http://", "https://")):
        response = requests.get(source, timeout=30)
        response.raise_for_status()
        return pd.read_excel(BytesIO(response.content), engine="openpyxl")
    return pd.read_excel(Path(source), engine="openpyxl")


def build_reference_index(ref_df: pd.DataFrame) -> tuple[dict[str, list[dict]], list[str]]:
    name_col = choose_column(ref_df, ["journal name", "title", "source", "journal"])
    jif_col = choose_column(ref_df, ["jif 2024", "impact factor", "jif"])
    quartile_col = choose_column(ref_df, ["quartile", "jif quartile", "q"])

    ref_df = ref_df.copy()
    ref_df["__std_name"] = ref_df[name_col].map(standardize_journal_name)
    index: dict[str, list[dict]] = {}
    for _, row in ref_df.iterrows():
        key = row["__std_name"]
        if not key:
            continue
        index.setdefault(key, []).append(
            {
                "raw_name": row[name_col],
                "jif": row[jif_col],
                "quartile": row[quartile_col],
            }
        )
    return index, list(index)


def match_journals(user_df: pd.DataFrame, ref_df: pd.DataFrame, score_cutoff: int = 90) -> pd.DataFrame:
    ref_index, ref_names = build_reference_index(ref_df)
    user_title_col = choose_column(user_df, ["source title", "source_title", "source", "journal", "journal title"])

    rows = []
    for journal in tqdm(user_df[user_title_col].map(standardize_journal_name), desc="Journal matching"):
        if not journal:
            rows.append(("", "No match found", 0, "", ""))
            continue
        if journal in ref_index:
            info = ref_index[journal][0]
            rows.append((journal, info["raw_name"], 100, info["jif"], info["quartile"]))
            continue
        match = _best_match(journal, ref_names, score_cutoff)
        if match:
            info = ref_index[match[0]][0]
            rows.append((journal, info["raw_name"], int(match[1]), info["jif"], info["quartile"]))
        else:
            rows.append((journal, "No match found", 0, "", ""))

    result_cols = ["processed_journal_name", "best_match", "match_score", "jif_2024", "jif_quartile"]
    return pd.concat([user_df.reset_index(drop=True), pd.DataFrame(rows, columns=result_cols)], axis=1)


def _best_match(query: str, choices: list[str], score_cutoff: int) -> tuple[str, float] | None:
    if process is not None and fuzz is not None:
        return process.extractOne(query, choices, scorer=fuzz.ratio, score_cutoff=score_cutoff)

    import difflib

    best_choice = None
    best_score = 0.0
    for choice in choices:
        score = difflib.SequenceMatcher(None, query, choice).ratio() * 100
        if score > best_score:
            best_choice = choice
            best_score = score
    if best_choice is None or best_score < score_cutoff:
        return None
    return best_choice, best_score


def journal_stats(df: pd.DataFrame) -> dict:
    matched = df[df["match_score"] > 0]
    values = [safe_number(value) for value in matched["jif_2024"]]
    values = [value for value in values if value is not None]
    quartiles = matched["jif_quartile"].dropna().astype(str).str.strip()
    return {
        "total_journals": int(len(df)),
        "matched_journals": int(len(matched)),
        "match_rate": float(len(matched) / len(df) * 100) if len(df) else 0.0,
        "perfect_matches": int((df["match_score"] == 100).sum()),
        "jif_count": len(values),
        "jif_mean": float(np.mean(values)) if values else 0.0,
        "jif_median": float(np.median(values)) if values else 0.0,
        "quartile_distribution": quartiles.value_counts().to_dict(),
    }
