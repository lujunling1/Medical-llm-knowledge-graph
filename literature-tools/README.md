# Literature Tools

Python version:

```text
Python 3.13.11
```

## Install

```bash
cd literature-tools
pip install -e .
```

## Commands

Deduplicate records by normalized title, DOI, and abstract columns:

```bash
lit-tools dedup --input input.xlsx --output outputs/deduped.xlsx --columns TI DI AB
```

Normalize or recover DOI values through OpenAlex by PMID and DOI:

```bash
lit-tools doi-map --input input.xlsx --output outputs/doi_mapped.xlsx --pmid-col PMID --doi-col DI
```

Enrich records with OpenAlex citation count, publication month, and OpenAlex id:

```bash
lit-tools enrich-openalex --input input.xlsx --output outputs/enriched.xlsx --title-col TI --doi-col DI --pmid-col PMID
```

Match journal names to JCR impact factor data:

```bash
lit-tools journal-if --input input.xlsx --reference reference/jcr.xlsx --output outputs/journal_if.xlsx
```

## Organization

```text
src/lit_review_tools/
  cli.py              unified command line interface
  common.py           shared table loading, text cleaning, DOI helpers
  deduplication.py    duplicate and empty-value quality control
  openalex.py         DOI, citation, date, and id enrichment
  journal_metrics.py  journal impact factor matching
```
