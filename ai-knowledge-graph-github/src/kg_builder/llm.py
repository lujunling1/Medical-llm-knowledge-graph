"""Small OpenAI-compatible chat client and JSON extraction helpers."""

from __future__ import annotations

import json
import re
import time
from typing import Any

import requests


def call_llm(
    *,
    model: str,
    base_url: str,
    api_key: str,
    system_prompt: str,
    user_prompt: str,
    max_tokens: int,
    temperature: float,
    retries: int = 3,
    retry_delay: int = 5,
) -> str:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            response = requests.post(base_url, headers=headers, json=payload, timeout=90)
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            if not isinstance(content, str) or not content.strip():
                raise RuntimeError("LLM returned empty content.")
            return content.strip()
        except Exception as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(retry_delay)
    raise RuntimeError(f"LLM request failed after {retries} attempts: {last_error}") from last_error


def extract_json(text: str) -> Any:
    """Parse JSON from a raw LLM response."""
    text = text.strip()
    fenced = re.search(r"```(?:json)?\s*([\s\S]*?)```", text, flags=re.IGNORECASE)
    candidates = [fenced.group(1).strip()] if fenced else []
    candidates.append(text)

    fragment = _balanced_json_fragment(text)
    if fragment:
        candidates.append(fragment)

    for candidate in candidates:
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            continue
    raise ValueError("No valid JSON object or array found in LLM response.")


def _balanced_json_fragment(text: str) -> str | None:
    starts = [idx for idx in (text.find("{"), text.find("[")) if idx != -1]
    if not starts:
        return None
    start = min(starts)
    opening = text[start]
    closing = "}" if opening == "{" else "]"
    depth = 0
    in_string = False
    escape = False

    for idx in range(start, len(text)):
        char = text[idx]
        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == opening:
            depth += 1
        elif char == closing:
            depth -= 1
            if depth == 0:
                return text[start : idx + 1]
    return None
