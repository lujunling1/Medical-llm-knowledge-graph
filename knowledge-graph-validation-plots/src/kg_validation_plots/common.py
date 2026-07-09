from __future__ import annotations

from pathlib import Path

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
