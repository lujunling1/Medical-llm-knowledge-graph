from __future__ import annotations

import argparse

from .common import read_table, write_table
from .plotting import make_summary_plots
from .validation import evaluate_columns


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Knowledge graph validation and plotting utilities.")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("validate-llm", help="Evaluate model extraction output against manual annotations.")
    p.add_argument("--manual", required=True)
    p.add_argument("--model", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--columns", nargs="*")
    p.add_argument("--threshold", type=float, default=0.75)

    p = sub.add_parser("plot-summary", help="Create basic summary plots.")
    p.add_argument("--input", required=True)
    p.add_argument("--output-dir", required=True)

    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)

    if args.command == "validate-llm":
        manual_df = read_table(args.manual)
        model_df = read_table(args.model)
        out = evaluate_columns(manual_df, model_df, args.columns, args.threshold)
        write_table(out, args.output)
    elif args.command == "plot-summary":
        make_summary_plots(read_table(args.input), args.output_dir)


if __name__ == "__main__":
    main()
