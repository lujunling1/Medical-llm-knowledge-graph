# Code Organization

This module consolidates the reusable code into a smaller set of maintained functions.

## Consolidated Functions

| Source script group | Consolidated module | Main command |
| --- | --- | --- |
| Deduplication and quality control scripts | `deduplication.py` | `lit-tools dedup` |
| DOI normalization and PMID/DOI recovery scripts | `openalex.py` | `lit-tools doi-map` |
| OpenAlex citation/date/id enrichment scripts | `openalex.py` | `lit-tools enrich-openalex` |
| Journal impact factor matching scripts | `journal_metrics.py` | `lit-tools journal-if` |

## 知识图谱的验证与有关绘图

| Source script group | Consolidated module | Main command |
| --- | --- | --- |
| Manual vs model LLM validation scripts | `validation.py` | `lit-tools validate-llm` |
| Repeated summary plotting scripts | `plotting.py` | `lit-tools plot-summary` |
