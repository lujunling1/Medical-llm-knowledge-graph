from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Iterable

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


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


def parse_entities(value: object) -> list[str]:
    if value is None or pd.isna(value):
        return []
    text = str(value).strip()
    if not text:
        return []
    parts = re.split(r";|\||\n|,", text)
    return sorted({normalize_entity(part) for part in parts if normalize_entity(part)})


def normalize_entity(value: object) -> str:
    text = "" if value is None else str(value).lower().strip()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"^[\-\*\d\.\)\s]+", "", text)
    return text.strip()


def exact_prf1(manual: list[str], model: list[str]) -> dict[str, float]:
    manual_set = set(manual)
    model_set = set(model)
    true_positive = len(manual_set & model_set)
    precision = true_positive / len(model_set) if model_set else 0.0
    recall = true_positive / len(manual_set) if manual_set else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"precision": precision, "recall": recall, "f1": f1}


def semantic_match_count(manual: list[str], model: list[str], threshold: float = 0.75) -> int:
    if not manual or not model:
        return 0
    corpus = manual + model
    matrix = TfidfVectorizer().fit_transform(corpus)
    similarity = cosine_similarity(matrix[: len(manual)], matrix[len(manual) :])
    matched_manual: set[int] = set()
    matched_model: set[int] = set()
    pairs = np.argwhere(similarity >= threshold)
    pairs = sorted(pairs, key=lambda pair: similarity[pair[0], pair[1]], reverse=True)
    for manual_idx, model_idx in pairs:
        if int(manual_idx) not in matched_manual and int(model_idx) not in matched_model:
            matched_manual.add(int(manual_idx))
            matched_model.add(int(model_idx))
    return len(matched_manual)


def semantic_prf1(manual: list[str], model: list[str], threshold: float = 0.75) -> dict[str, float]:
    true_positive = semantic_match_count(manual, model, threshold)
    precision = true_positive / len(model) if model else 0.0
    recall = true_positive / len(manual) if manual else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"precision": precision, "recall": recall, "f1": f1}


def evaluate_columns(
    manual_df: pd.DataFrame,
    model_df: pd.DataFrame,
    columns: Iterable[str] | None = None,
    threshold: float = 0.75,
) -> pd.DataFrame:
    selected_columns = list(columns) if columns else [col for col in manual_df.columns if col in model_df.columns]
    rows = []
    for column in selected_columns:
        manual_entities: list[str] = []
        model_entities: list[str] = []
        for value in manual_df[column]:
            manual_entities.extend(parse_entities(value))
        for value in model_df[column]:
            model_entities.extend(parse_entities(value))
        exact = exact_prf1(manual_entities, model_entities)
        semantic = semantic_prf1(manual_entities, model_entities, threshold)
        rows.append(
            {
                "field": column,
                "manual_count": len(manual_entities),
                "model_count": len(model_entities),
                "exact_precision": exact["precision"],
                "exact_recall": exact["recall"],
                "exact_f1": exact["f1"],
                "semantic_precision": semantic["precision"],
                "semantic_recall": semantic["recall"],
                "semantic_f1": semantic["f1"],
            }
        )
    return pd.DataFrame(rows)


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
    paths = [
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
    return paths


def _plot_metric_group(df: pd.DataFrame, columns: list[str], output_path: Path, title: str) -> Path:
    data = df[["field", *columns]].copy()
    data = data.set_index("field")
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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Knowledge graph validation utilities.")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("validate-llm", help="Evaluate model extraction output against manual annotations.")
    p.add_argument("--manual", required=True)
    p.add_argument("--model", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--columns", nargs="*")
    p.add_argument("--threshold", type=float, default=0.75)
    p.add_argument("--plot-dir", help="Optional folder for validation metric charts.")

    p = sub.add_parser("plot-validation", help="Create charts from a validation result table.")
    p.add_argument("--input", required=True)
    p.add_argument("--output-dir", required=True)

    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)

    if args.command == "validate-llm":
        manual_df = read_table(args.manual)
        model_df = read_table(args.model)
        result = evaluate_columns(manual_df, model_df, args.columns, args.threshold)
        write_table(result, args.output)
        if args.plot_dir:
            plot_validation_scores(result, args.plot_dir)
    elif args.command == "plot-validation":
        plot_validation_scores(read_table(args.input), args.output_dir)


if __name__ == "__main__":
    main()
