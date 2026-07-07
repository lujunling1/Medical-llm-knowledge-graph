from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

from .common import choose_column, split_values


def set_style() -> None:
    plt.rcParams.update(
        {
            "figure.dpi": 300,
            "savefig.dpi": 300,
            "font.family": "sans-serif",
            "axes.linewidth": 1.0,
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )


def plot_top_categories(
    df: pd.DataFrame,
    column: str,
    output_path: str | Path,
    *,
    top_n: int = 10,
    title: str | None = None,
) -> pd.Series:
    set_style()
    counts = df[column].dropna().astype(str).value_counts().head(top_n)
    fig, ax = plt.subplots(figsize=(8, max(4, top_n * 0.35)))
    counts.sort_values().plot(kind="barh", ax=ax, color="#4C78A8")
    ax.set_xlabel("Count")
    ax.set_ylabel("")
    ax.set_title(title or f"Top {top_n} {column}")
    fig.tight_layout()
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path)
    plt.close(fig)
    return counts


def plot_quarterly_trend(
    df: pd.DataFrame,
    date_col: str,
    output_path: str | Path,
    *,
    value_col: str | None = None,
    title: str = "Quarterly trend",
) -> pd.DataFrame:
    set_style()
    data = df.copy()
    data[date_col] = pd.to_datetime(data[date_col], errors="coerce")
    data = data.dropna(subset=[date_col])
    data["quarter"] = data[date_col].dt.to_period("Q").astype(str)
    if value_col and value_col in data.columns:
        trend = data.groupby("quarter")[value_col].sum().reset_index(name="value")
    else:
        trend = data.groupby("quarter").size().reset_index(name="value")
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(trend["quarter"], trend["value"], marker="o", color="#4C78A8")
    ax.set_title(title)
    ax.set_xlabel("")
    ax.set_ylabel(value_col or "Count")
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path)
    plt.close(fig)
    return trend


def make_summary_plots(df: pd.DataFrame, output_dir: str | Path) -> None:
    output_dir = Path(output_dir)
    for candidates, filename in [
        (["task", "task type", "task_types"], "top_tasks.png"),
        (["country", "countries"], "top_countries.png"),
        (["source title", "journal"], "top_journals.png"),
    ]:
        column = choose_column(df, candidates, required=False)
        if column:
            plot_top_categories(df, column, output_dir / filename)

    date_col = choose_column(df, ["publication_month", "publication_date", "date", "year"], required=False)
    if date_col:
        plot_quarterly_trend(df, date_col, output_dir / "quarterly_trend.png")
