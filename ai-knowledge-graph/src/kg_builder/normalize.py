"""Normalization helpers."""

from __future__ import annotations

import re

from .models import Triple

DOI_RE = re.compile(r"(10\.\d{4,9}/[^\s\"<>]+)", re.IGNORECASE)
TYPE_SUFFIX_RE = re.compile(r"\s*\[[^\]]+\]$")


def normalize_doi(value: object) -> str:
    text = "" if value is None else str(value).strip()
    if not text or text.lower() in {"na", "none", "nan", "null"}:
        return "NA"
    match = DOI_RE.search(text)
    if not match:
        return "NA"
    return match.group(1).rstrip(").,;:]")


def strip_type_suffix(name: str) -> str:
    return TYPE_SUFFIX_RE.sub("", str(name or "").strip())


def typed_id(name: str, entity_type: str) -> str:
    base = strip_type_suffix(name)
    return f"{base} [{entity_type}]" if base else f"NA [{entity_type}]"


def clean_predicate(predicate: str, max_words: int = 3) -> str:
    words = str(predicate or "related_to").strip().split()
    if not words:
        return "related_to"
    return " ".join(words[:max_words])


def normalize_triple_text(triple: Triple, lowercase: bool = False) -> Triple:
    subject = strip_type_suffix(triple.subject)
    obj = strip_type_suffix(triple.object)
    if lowercase:
        subject = subject.lower()
        obj = obj.lower()
    return Triple(
        subject=typed_id(subject, triple.subject_type),
        predicate=clean_predicate(triple.predicate),
        object=typed_id(obj, triple.object_type),
        subject_type=triple.subject_type,
        object_type=triple.object_type,
        doi=normalize_doi(triple.doi),
        source_id=triple.source_id,
        provenance=triple.provenance,
    )
