"""Prompt file loading."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PromptTemplate:
    system: str
    user: str

    def render_user(self, **values: object) -> str:
        rendered = self.user
        for key, value in values.items():
            rendered = rendered.replace("{" + key + "}", str(value))
        return rendered


def load_prompt(path: str | Path) -> PromptTemplate:
    prompt_path = Path(path)
    content = prompt_path.read_text(encoding="utf-8")
    sections = _parse_sections(content)
    try:
        system = _strip_template_comments(sections["system"])
        user = _strip_template_comments(sections["user"])
    except KeyError as exc:
        raise ValueError(f"Prompt file must contain [system] and [user] sections: {prompt_path}") from exc
    if not system or not user:
        raise ValueError(
            f"Prompt file is empty: {prompt_path}. Fill in both [system] and [user] sections before running."
        )
    if "{text}" not in user:
        raise ValueError(f"Prompt user section must include the {{text}} placeholder: {prompt_path}")
    return PromptTemplate(system=system, user=user)


def _parse_sections(content: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in content.splitlines():
        stripped = line.strip().lower()
        if stripped in {"[system]", "[user]"}:
            current = stripped.strip("[]")
            sections.setdefault(current, [])
            continue
        if current:
            sections[current].append(line)
    return {key: "\n".join(lines) for key, lines in sections.items()}


def _strip_template_comments(value: str) -> str:
    lines = []
    for line in value.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        lines.append(line)
    return "\n".join(lines).strip()
