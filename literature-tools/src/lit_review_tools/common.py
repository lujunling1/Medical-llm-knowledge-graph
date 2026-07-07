from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from typing import Iterable

import pandas as pd

DOI_RE = re.compile(r"(10\.\d{4,9}/[^\s\"<>]+)", re.IGNORECASE)


def read_table(path: str | Path, **kwargs) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)
    suffix = path.suffix.lower()
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(path, **kwargs)
    if suffix == ".csv":
        return pd.read_csv(path, **kwargs)
    raise ValueError(f"Unsupported input format: {path.suffix}")


def write_table(df: pd.DataFrame, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    suffix = path.suffix.lower()
    if suffix in {".xlsx", ".xls"}:
        df.to_excel(path, index=False)
    elif suffix == ".csv":
        df.to_csv(path, index=False, encoding="utf-8-sig")
    else:
        raise ValueError(f"Unsupported output format: {path.suffix}")


def remove_unicode_punctuation(value: object) -> str:
    if not isinstance(value, str):
        return ""
    return "".join(ch for ch in value if unicodedata.category(ch)[0] != "P")


def normalize_key(value: object) -> str:
    text = remove_unicode_punctuation(value).strip()
    return re.sub(r"\s+", " ", text).upper()


def normalize_doi(value: object) -> str | None:
    text = "" if value is None or pd.isna(value) else str(value).strip()
    if not text:
        return None
    text = re.sub(r"^https?://(dx\.)?doi\.org/", "", text, flags=re.IGNORECASE)
    match = DOI_RE.search(text)
    doi = match.group(1) if match else text
    doi = doi.strip().rstrip(").,;:]").lower()
    return doi or None


def normalize_pmid(value: object) -> str | None:
    if value is None or pd.isna(value):
        return None
    text = str(value).strip()
    if not text:
        return None
    match = re.search(r"(\d+)$", text)
    return match.group(1) if match else text


def choose_column(df: pd.DataFrame, candidates: Iterable[str], required: bool = True) -> str | None:
    lower_map = {str(col).lower(): col for col in df.columns}
    for candidate in candidates:
        candidate = candidate.lower()
        for lower_name, original in lower_map.items():
            if candidate in lower_name:
                return str(original)
    if required:
        raise KeyError(f"Could not find a column matching: {list(candidates)}")
    return None


def split_values(value: object, separators: str = r";|\||,") -> list[str]:
    if value is None or pd.isna(value):
        return []
    parts = re.split(separators, str(value))
    return [part.strip() for part in parts if part.strip()]


def safe_number(value: object) -> float | None:
    if value is None or pd.isna(value):
        return None
    match = re.search(r"\d+(?:\.\d+)?", str(value))
    return float(match.group()) if match else None
