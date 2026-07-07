"""Input loading utilities."""

from __future__ import annotations

import json
from pathlib import Path

from .normalize import normalize_doi

DOCUMENT_BOUNDARY = "===== DOCUMENT BOUNDARY ====="


def load_text_documents(path: str | Path, doi_map_path: str | Path | None = None) -> list[dict[str, str]]:
    text = Path(path).read_text(encoding="utf-8")
    parts = [part.strip() for part in text.split(DOCUMENT_BOUNDARY) if part.strip()]
    doi_map = _load_doi_map(doi_map_path)
    return [
        {"text": part, "doi": doi_map.get(str(idx), "NA"), "source_id": str(idx)}
        for idx, part in enumerate(parts, start=1)
    ]


def load_excel_documents(
    path: str | Path,
    *,
    sheet: str | int = 0,
    text_column: str = "AB",
    doi_column: str = "DI",
) -> list[dict[str, str]]:
    try:
        import pandas as pd
    except ImportError as exc:
        raise RuntimeError("Excel input requires: pip install '.[excel]'") from exc

    df = pd.read_excel(path, sheet_name=sheet)
    if text_column not in df.columns:
        raise ValueError(f"Missing text column: {text_column}")

    has_doi = doi_column in df.columns
    docs: list[dict[str, str]] = []
    for row_idx, row in df.iterrows():
        text = "" if row[text_column] is None else str(row[text_column]).strip()
        if not text or text.lower() == "nan":
            continue
        doi = normalize_doi(row[doi_column]) if has_doi else "NA"
        docs.append({"text": text, "doi": doi, "source_id": str(row_idx + 1)})
    return docs


def _load_doi_map(path: str | Path | None) -> dict[str, str]:
    if path is None:
        return {}
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(raw, list):
        return {str(i + 1): normalize_doi(value) for i, value in enumerate(raw)}
    if isinstance(raw, dict):
        return {str(key): normalize_doi(value) for key, value in raw.items()}
    raise ValueError("DOI map must be a JSON object or array.")
