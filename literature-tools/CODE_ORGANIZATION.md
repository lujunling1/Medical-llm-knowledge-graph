# Code Organization

The original working directory contained many one-off scripts, duplicated versions, and generated artifacts.
This module consolidates the reusable code into a smaller set of maintained functions.

## Consolidated Functions

| Source script group | Consolidated module | Main command |
| --- | --- | --- |
| Deduplication and quality control scripts | `deduplication.py` | `lit-tools dedup` |
| DOI normalization and PMID/DOI recovery scripts | `openalex.py` | `lit-tools doi-map` |
| OpenAlex citation/date/id enrichment scripts | `openalex.py` | `lit-tools enrich-openalex` |
| Journal impact factor matching scripts | `journal_metrics.py` | `lit-tools journal-if` |
| Manual vs model LLM validation scripts | `validation.py` | `lit-tools validate-llm` |
| Repeated summary plotting scripts | `plotting.py` | `lit-tools plot-summary` |

## Not Included

- Generated charts, HTML files, PDFs, and spreadsheets.
- Exact duplicate scripts and files marked as copies.
- Hard-coded local paths and one-off desktop paths.
- Local API emails and personal configuration values.

## Design Notes

- All commands take input and output paths as arguments.
- Shared normalization helpers live in `common.py`.
- OpenAlex access is optional and only runs when a command requiring it is used.
- Journal matching uses `rapidfuzz` when installed and falls back to Python's standard library otherwise.
