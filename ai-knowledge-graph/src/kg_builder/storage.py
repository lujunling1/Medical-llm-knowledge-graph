"""Knowledge graph storage."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .models import KnowledgeGraph


def save_graph(graph: KnowledgeGraph, output_dir: str | Path, *, name: str = "knowledge_graph") -> dict[str, str]:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    graph_path = out_dir / f"{name}_graph.json"
    node_doi_path = out_dir / f"{name}_node_dois.json"
    metadata_path = out_dir / f"{name}_metadata.json"

    _write_json(graph_path, graph.to_dict())
    _write_json(node_doi_path, graph.node_dois())
    _write_json(
        metadata_path,
        {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "graph_file": graph_path.name,
            "node_doi_file": node_doi_path.name,
            "node_count": graph.to_dict()["metadata"]["node_count"],
            "triple_count": graph.to_dict()["metadata"]["triple_count"],
        },
    )

    return {
        "graph": str(graph_path),
        "node_dois": str(node_doi_path),
        "metadata": str(metadata_path),
    }


def _write_json(path: Path, payload: object) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
