"""Command line interface."""

from __future__ import annotations

import argparse
from pathlib import Path

from .config import load_config
from .extraction import extract_triples_from_text, split_text
from .inputs import load_excel_documents, load_text_documents
from .models import KnowledgeGraph
from .storage import save_graph


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build and save a knowledge graph as JSON.")
    parser.add_argument("--config", default="config.toml", help="Path to TOML config.")
    parser.add_argument("--input", help="UTF-8 text file. Use document boundary lines for multiple documents.")
    parser.add_argument("--doi-map", help="Optional JSON DOI map for text input.")
    parser.add_argument("--excel", help="Excel file input.")
    parser.add_argument("--excel-sheet", default=0, help="Excel sheet name or index. Default: 0.")
    parser.add_argument("--text-column", default="AB", help="Excel text column. Default: AB.")
    parser.add_argument("--doi-column", default="DI", help="Excel DOI column. Default: DI.")
    parser.add_argument("--schema", choices=["med-llm", "generic"], help="Override extraction schema.")
    parser.add_argument("--output-dir", default="outputs", help="Output directory.")
    parser.add_argument("--name", default="knowledge_graph", help="Output file prefix.")
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    config = load_config(args.config)

    if bool(args.input) == bool(args.excel):
        raise SystemExit("Provide exactly one of --input or --excel.")

    if args.excel:
        sheet = int(args.excel_sheet) if str(args.excel_sheet).isdigit() else args.excel_sheet
        documents = load_excel_documents(
            args.excel,
            sheet=sheet,
            text_column=args.text_column,
            doi_column=args.doi_column,
        )
    else:
        documents = load_text_documents(args.input, args.doi_map)

    graph = KnowledgeGraph()
    for doc in documents:
        chunks = split_text(doc["text"], config.chunk_size, config.overlap)
        for chunk_idx, chunk in enumerate(chunks, start=1):
            source_id = f'{doc["source_id"]}.{chunk_idx}' if len(chunks) > 1 else doc["source_id"]
            triples = extract_triples_from_text(
                chunk,
                config,
                schema=args.schema,
                doi=doc["doi"],
                source_id=source_id,
            )
            graph.add_many(triples)

    if config.deduplicate:
        graph.deduplicate()

    paths = save_graph(graph, Path(args.output_dir), name=args.name)
    print(f"Saved graph: {paths['graph']}")
    print(f"Saved node DOI report: {paths['node_dois']}")
    print(f"Saved metadata: {paths['metadata']}")
    print(f"Triples: {len(graph.triples)}")


if __name__ == "__main__":
    main()
