from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd


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
