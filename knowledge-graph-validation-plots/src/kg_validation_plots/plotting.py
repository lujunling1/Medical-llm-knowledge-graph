from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd


def set_plot_style() -> None:
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


def plot_validation_scores(validation_df: pd.DataFrame, output_dir: str | Path) -> list[Path]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    set_plot_style()
    return [
        _plot_metric_group(
            validation_df,
            ["exact_precision", "exact_recall", "exact_f1"],
            output_dir / "exact_validation_scores.png",
            "Exact validation scores",
        ),
        _plot_metric_group(
            validation_df,
            ["semantic_precision", "semantic_recall", "semantic_f1"],
            output_dir / "semantic_validation_scores.png",
            "Semantic validation scores",
        ),
        _plot_entity_counts(validation_df, output_dir / "validation_entity_counts.png"),
    ]


def _plot_metric_group(df: pd.DataFrame, columns: list[str], output_path: Path, title: str) -> Path:
    data = df[["field", *columns]].copy().set_index("field")
    fig, ax = plt.subplots(figsize=(10, max(4, len(data) * 0.45)))
    data.plot(kind="barh", ax=ax)
    ax.set_xlim(0, 1)
    ax.set_xlabel("Score")
    ax.set_ylabel("")
    ax.set_title(title)
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)
    return output_path


def _plot_entity_counts(df: pd.DataFrame, output_path: Path) -> Path:
    data = df[["field", "manual_count", "model_count"]].copy().set_index("field")
    fig, ax = plt.subplots(figsize=(10, max(4, len(data) * 0.45)))
    data.plot(kind="barh", ax=ax)
    ax.set_xlabel("Entity count")
    ax.set_ylabel("")
    ax.set_title("Manual vs model entity counts")
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)
    return output_path
