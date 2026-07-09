from __future__ import annotations

import re
from typing import Iterable

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


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
