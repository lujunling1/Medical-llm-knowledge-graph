"""Data models for graph serialization."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass(frozen=True)
class Triple:
    subject: str
    predicate: str
    object: str
    subject_type: str = "Unknown"
    object_type: str = "Unknown"
    doi: str = "NA"
    source_id: str = "NA"
    provenance: str = "extracted"

    def to_dict(self) -> dict:
        data = asdict(self)
        data["s_type"] = data.pop("subject_type")
        data["o_type"] = data.pop("object_type")
        return data


@dataclass
class KnowledgeGraph:
    triples: list[Triple] = field(default_factory=list)

    def add_many(self, triples: list[Triple]) -> None:
        self.triples.extend(triples)

    def deduplicate(self) -> None:
        seen: set[tuple[str, str, str, str]] = set()
        unique: list[Triple] = []
        for triple in self.triples:
            key = (
                triple.subject.casefold(),
                triple.predicate.casefold(),
                triple.object.casefold(),
                triple.doi.casefold(),
            )
            if key in seen:
                continue
            seen.add(key)
            unique.append(triple)
        self.triples = unique

    def node_dois(self) -> dict[str, list[str]]:
        mapping: dict[str, set[str]] = {}
        for triple in self.triples:
            if triple.doi == "NA":
                continue
            mapping.setdefault(triple.subject, set()).add(triple.doi)
            mapping.setdefault(triple.object, set()).add(triple.doi)
        return {node: sorted(dois) for node, dois in sorted(mapping.items())}

    def to_dict(self) -> dict:
        nodes = sorted({t.subject for t in self.triples} | {t.object for t in self.triples})
        return {
            "metadata": {
                "node_count": len(nodes),
                "triple_count": len(self.triples),
            },
            "triples": [triple.to_dict() for triple in self.triples],
        }
