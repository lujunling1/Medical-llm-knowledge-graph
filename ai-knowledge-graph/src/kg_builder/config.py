"""Configuration loading."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11 fallback
    import tomli as tomllib  # type: ignore


@dataclass(frozen=True)
class LLMConfig:
    model: str
    base_url: str
    api_key: str
    max_tokens: int = 4096
    temperature: float = 0.2


@dataclass(frozen=True)
class AppConfig:
    llm: LLMConfig
    schema: str = "med-llm"
    chunk_size: int = 1200
    overlap: int = 100
    med_llm_prompt: str = "prompts/med_llm.txt"
    generic_prompt: str = "prompts/generic.txt"
    lowercase_generic_triples: bool = False
    deduplicate: bool = True


def _read_toml(path: Path) -> dict[str, Any]:
    with path.open("rb") as f:
        return tomllib.load(f)


def load_config(path: str | Path = "config.toml") -> AppConfig:
    raw = _read_toml(Path(path))
    llm_raw = raw.get("llm", {})
    extraction = raw.get("extraction", {})
    normalization = raw.get("normalization", {})

    api_key = str(llm_raw.get("api_key", "")).strip()
    api_key_env = str(llm_raw.get("api_key_env", "")).strip()
    if not api_key and api_key_env:
        api_key = os.getenv(api_key_env, "").strip()

    if not api_key:
        raise ValueError("Missing API key. Set llm.api_key_env in config and export the environment variable.")

    return AppConfig(
        llm=LLMConfig(
            model=str(llm_raw["model"]),
            base_url=str(llm_raw["base_url"]),
            api_key=api_key,
            max_tokens=int(llm_raw.get("max_tokens", 4096)),
            temperature=float(llm_raw.get("temperature", 0.2)),
        ),
        schema=str(extraction.get("schema", "med-llm")),
        chunk_size=int(extraction.get("chunk_size", 1200)),
        overlap=int(extraction.get("overlap", 100)),
        med_llm_prompt=str(extraction.get("med_llm_prompt", "prompts/med_llm.txt")),
        generic_prompt=str(extraction.get("generic_prompt", "prompts/generic.txt")),
        lowercase_generic_triples=bool(normalization.get("lowercase_generic_triples", False)),
        deduplicate=bool(normalization.get("deduplicate", True)),
    )
