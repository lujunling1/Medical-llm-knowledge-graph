from __future__ import annotations

import argparse
import json
from pathlib import Path

from .common import read_table, write_table
from .deduplication import deduplicate_file
from .journal_metrics import journal_stats, load_reference_df, match_journals
from .openalex import OpenAlexClient, add_doi_from_openalex, enrich_with_openalex


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Literature deduplication and metadata utilities.")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("dedup", help="Deduplicate and remove empty rows by normalized columns.")
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--columns", nargs="+", default=["TI", "DI", "AB"])

    p = sub.add_parser("doi-map", help="Recover DOI values through OpenAlex by PMID and DOI.")
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--pmid-col", default="PMID")
    p.add_argument("--doi-col", default="DI")
    p.add_argument("--email")

    p = sub.add_parser("enrich-openalex", help="Add OpenAlex id, citation count, and publication month.")
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--title-col", default="TI")
    p.add_argument("--doi-col", default="DI")
    p.add_argument("--pmid-col", default="PMID")
    p.add_argument("--email")
    p.add_argument("--workers", type=int, default=8)

    p = sub.add_parser("journal-if", help="Match journal names to JCR impact factor data.")
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--reference", required=True, help="JCR/reference table path or URL.")
    p.add_argument("--cutoff", type=int, default=90)

    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)

    if args.command == "dedup":
        deduplicate_file(args.input, args.output, args.columns)
    elif args.command == "doi-map":
        df = read_table(args.input, dtype={args.pmid_col: str, args.doi_col: str})
        out = add_doi_from_openalex(df, OpenAlexClient(email=args.email), args.pmid_col, args.doi_col)
        write_table(out, args.output)
    elif args.command == "enrich-openalex":
        df = read_table(args.input, dtype={args.title_col: str, args.doi_col: str, args.pmid_col: str})
        out = enrich_with_openalex(
            df,
            OpenAlexClient(email=args.email),
            title_col=args.title_col,
            doi_col=args.doi_col,
            pmid_col=args.pmid_col,
            max_workers=args.workers,
        )
        write_table(out, args.output)
    elif args.command == "journal-if":
        user_df = read_table(args.input)
        ref_df = load_reference_df(args.reference)
        out = match_journals(user_df, ref_df, args.cutoff)
        write_table(out, args.output)
        stats_path = Path(args.output).with_suffix(".stats.json")
        stats_path.write_text(json.dumps(journal_stats(out), ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
