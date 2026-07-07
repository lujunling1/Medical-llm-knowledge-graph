from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .common import normalize_key, read_table


@dataclass(frozen=True)
class DedupResult:
    data: pd.DataFrame
    log: pd.DataFrame
    removed_rows: pd.DataFrame


def deduplicate_dataframe(df: pd.DataFrame, columns: list[str]) -> DedupResult:
    current = df.copy()
    logs: list[dict] = []
    removed_frames: list[pd.DataFrame] = []

    for column in columns:
        if column not in current.columns:
            raise KeyError(f"Column not found: {column}")
        before = len(current)
        norm_col = f"__norm_{column}"
        current[norm_col] = current[column].map(normalize_key)

        duplicated = current.duplicated(subset=[norm_col], keep="first")
        empty = current[norm_col].astype(str).str.strip().eq("")
        remove_mask = duplicated | empty

        removed = current.loc[remove_mask].copy()
        if not removed.empty:
            removed.insert(0, "source_column", column)
            removed.insert(1, "remove_reason", ["duplicate" if d else "empty" for d in duplicated.loc[remove_mask]])
            removed_frames.append(removed.drop(columns=[norm_col], errors="ignore"))

        current = current.loc[~remove_mask].drop(columns=[norm_col], errors="ignore").copy()
        logs.append(
            {
                "column": column,
                "rows_before": before,
                "duplicates_removed": int(duplicated.sum()),
                "empty_removed": int((empty & ~duplicated).sum()),
                "rows_after": len(current),
            }
        )

    removed_rows = pd.concat(removed_frames, ignore_index=True) if removed_frames else pd.DataFrame()
    return DedupResult(data=current, log=pd.DataFrame(logs), removed_rows=removed_rows)


def deduplicate_file(input_path: str, output_path: str, columns: list[str]) -> DedupResult:
    result = deduplicate_dataframe(read_table(input_path), columns)
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        result.data.to_excel(writer, index=False, sheet_name="deduplicated")
        result.log.to_excel(writer, index=False, sheet_name="log")
        result.removed_rows.to_excel(writer, index=False, sheet_name="removed_rows")
    return result
