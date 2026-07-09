# Code Organization

This module provides literature deduplication, metadata enrichment, and journal metric matching functions.

## Functions

| Function area | Module | Main command |
| --- | --- | --- |
| Deduplication and quality control scripts | `deduplication.py` | `lit-tools dedup` |
| DOI normalization and PMID/DOI recovery scripts | `openalex.py` | `lit-tools doi-map` |
| OpenAlex citation/date/id enrichment scripts | `openalex.py` | `lit-tools enrich-openalex` |
| Journal impact factor matching scripts | `journal_metrics.py` | `lit-tools journal-if` |
