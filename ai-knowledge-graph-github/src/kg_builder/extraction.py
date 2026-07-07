"""Extraction and schema conversion."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from .config import AppConfig
from .llm import call_llm, extract_json
from .models import Triple
from .normalize import clean_predicate, normalize_triple_text, typed_id
from .prompt_loader import load_prompt

PREDICATE_SCHEMA = {
    "performs": ("LLM", "Task"),
    "evaluated_on": ("Task", "Dataset"),
    "measured_by": ("Task", "Metric"),
    "exhibits_risk": ("Task", "Risk"),
    "assessed_by": ("Task", "EvalMethod"),
}


def split_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    words = text.split()
    if len(words) <= chunk_size:
        return [text]
    chunks: list[str] = []
    start = 0
    step = max(1, chunk_size - overlap)
    while start < len(words):
        chunks.append(" ".join(words[start : start + chunk_size]))
        start += step
    return chunks


def extract_triples_from_text(
    text: str,
    config: AppConfig,
    *,
    schema: str | None = None,
    doi: str = "NA",
    source_id: str = "NA",
) -> list[Triple]:
    selected_schema = schema or config.schema
    if selected_schema == "med-llm":
        return _extract_med_llm(text, config, doi=doi, source_id=source_id)
    if selected_schema == "generic":
        return _extract_generic(text, config, doi=doi, source_id=source_id)
    raise ValueError(f"Unsupported schema: {selected_schema}")


def _extract_med_llm(text: str, config: AppConfig, *, doi: str, source_id: str) -> list[Triple]:
    prompt = load_prompt(config.med_llm_prompt)
    response = call_llm(
        model=config.llm.model,
        base_url=config.llm.base_url,
        api_key=config.llm.api_key,
        system_prompt=prompt.system,
        user_prompt=prompt.render_user(text=text),
        max_tokens=config.llm.max_tokens,
        temperature=config.llm.temperature,
    )
    data = extract_json(response)
    if not isinstance(data, dict):
        raise ValueError("med-llm schema expects one JSON object.")
    triples = med_llm_json_to_triples(data, doi=doi, source_id=source_id)
    return [normalize_triple_text(t) for t in triples]


def _extract_generic(text: str, config: AppConfig, *, doi: str, source_id: str) -> list[Triple]:
    prompt = load_prompt(config.generic_prompt)
    response = call_llm(
        model=config.llm.model,
        base_url=config.llm.base_url,
        api_key=config.llm.api_key,
        system_prompt=prompt.system,
        user_prompt=prompt.render_user(text=text),
        max_tokens=config.llm.max_tokens,
        temperature=config.llm.temperature,
    )
    data = extract_json(response)
    if not isinstance(data, list):
        raise ValueError("generic schema expects a JSON array.")

    triples: list[Triple] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        if not {"subject", "predicate", "object"} <= set(item):
            continue
        triples.append(
            Triple(
                subject=str(item["subject"]),
                predicate=clean_predicate(str(item["predicate"])),
                object=str(item["object"]),
                doi=doi,
                source_id=source_id,
            )
        )
    return [normalize_triple_text(t, lowercase=config.lowercase_generic_triples) for t in triples]


def med_llm_json_to_triples(data: dict[str, Any], *, doi: str, source_id: str) -> list[Triple]:
    llms = _as_values(data.get("llm_models"))
    tasks = _as_values(data.get("task_types"))
    datasets = _as_values(data.get("benchmarks_datasets"))
    metrics = _as_values(data.get("evaluation_metrics"))
    risks = _as_values(data.get("safety_issues"))
    methods = _as_values(data.get("evaluation_methods"))

    triples: list[Triple] = []
    triples.extend(_cross(llms, tasks, "performs", doi, source_id))
    triples.extend(_cross(tasks, datasets, "evaluated_on", doi, source_id))
    triples.extend(_cross(tasks, metrics, "measured_by", doi, source_id))
    triples.extend(_cross(tasks, risks, "exhibits_risk", doi, source_id))
    triples.extend(_cross(tasks, methods, "assessed_by", doi, source_id))
    return triples


def _as_values(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    cleaned = [str(item).strip() for item in value if str(item).strip()]
    return [item for item in cleaned if item.upper() != "NA"]


def _cross(subjects: Iterable[str], objects: Iterable[str], predicate: str, doi: str, source_id: str) -> list[Triple]:
    subject_type, object_type = PREDICATE_SCHEMA[predicate]
    triples: list[Triple] = []
    for subject in subjects:
        for obj in objects:
            triples.append(
                Triple(
                    subject=typed_id(subject, subject_type),
                    predicate=predicate,
                    object=typed_id(obj, object_type),
                    subject_type=subject_type,
                    object_type=object_type,
                    doi=doi,
                    source_id=source_id,
                )
            )
    return triples
