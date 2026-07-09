# medical-llm-knowledge-graph

Medical LLM literature workflow codebase.

Python version:

```text
Python 3.13.11
```

## Modules

- `ai-knowledge-graph/`: knowledge graph extraction and JSON storage.
- `literature-tools/`: literature deduplication, metadata enrichment, and journal metrics utilities.
- `knowledge-graph-validation-plots/`: knowledge graph validation and related plotting utilities.

## Project Structure

```text
medical-llm-knowledge-graph/
  ai-knowledge-graph/
  knowledge-graph-validation-plots/
  literature-tools/
  README.md
```

## Code File Overview

| Module | Code file | Main function |
| --- | --- | --- |
| `ai-knowledge-graph` | `src/kg_builder/cli.py` | Command line entry point for `kg-build`; reads arguments, loads input documents, runs extraction, deduplicates triples, and saves JSON graph files. |
| `ai-knowledge-graph` | `src/kg_builder/config.py` | Loads TOML configuration, reads the API key from an environment variable, and builds runtime configuration objects. |
| `ai-knowledge-graph` | `src/kg_builder/extraction.py` | Splits text into chunks, calls the LLM extraction flow, supports `generic` SPO extraction and `med-llm` schema conversion. |
| `ai-knowledge-graph` | `src/kg_builder/inputs.py` | Loads UTF-8 text files, multi-document text boundaries, DOI maps, and optional Excel input columns. |
| `ai-knowledge-graph` | `src/kg_builder/llm.py` | Minimal OpenAI-compatible chat API client with retry logic and JSON extraction from LLM responses. |
| `ai-knowledge-graph` | `src/kg_builder/models.py` | Defines `Triple` and `KnowledgeGraph`, including triple serialization, deduplication, node counts, and node-to-DOI mapping. |
| `ai-knowledge-graph` | `src/kg_builder/normalize.py` | Normalizes DOI values, entity type suffixes, predicates, and triple text before saving. |
| `ai-knowledge-graph` | `src/kg_builder/prompt_loader.py` | Reads external prompt files with `[system]` and `[user]` sections and checks that `{text}` is present. |
| `ai-knowledge-graph` | `src/kg_builder/storage.py` | Writes graph JSON, node DOI JSON, and run metadata JSON to the selected output folder. |
| `ai-knowledge-graph` | `src/kg_builder/__init__.py` | Package marker for the knowledge graph builder Python package. |
| `ai-knowledge-graph` | `config.example.toml` | Example runtime configuration for model, API endpoint, prompt paths, chunking, and deduplication settings. |
| `ai-knowledge-graph` | `prompts/generic.txt` | Ready-to-use generic Subject-Predicate-Object extraction prompt. |
| `ai-knowledge-graph` | `prompts/med_llm.txt` | Customizable medical LLM prompt template for user-defined extraction tasks. |
| `ai-knowledge-graph` | `pyproject.toml` | Package metadata, dependencies, optional Excel dependencies, and `kg-build` command registration. |
| `literature-tools` | `src/lit_review_tools/cli.py` | Command line entry point for `lit-tools`; dispatches deduplication, DOI mapping, OpenAlex enrichment, and journal matching commands. |
| `literature-tools` | `src/lit_review_tools/common.py` | Shared table I/O, text normalization, DOI/PMID normalization, column selection, value splitting, and number parsing helpers. |
| `literature-tools` | `src/lit_review_tools/deduplication.py` | Removes duplicates and empty rows by normalized columns and writes deduplicated data, logs, and removed rows. |
| `literature-tools` | `src/lit_review_tools/openalex.py` | Queries OpenAlex by DOI, PMID, or title; recovers DOI values and enriches records with citation count, publication month, and OpenAlex ID. |
| `literature-tools` | `src/lit_review_tools/journal_metrics.py` | Standardizes journal names, matches them to a JCR/reference table, adds impact factor and quartile fields, and outputs match statistics. |
| `literature-tools` | `src/lit_review_tools/__init__.py` | Package marker for the literature tools Python package. |
| `literature-tools` | `pyproject.toml` | Package metadata, dependencies, and `lit-tools` command registration. |
| `knowledge-graph-validation-plots` | `src/kg_validation_plots/main.py` | Knowledge graph validation code: reads tables, compares manual annotations with model extraction output, calculates exact and semantic precision/recall/F1, and draws validation-result charts. |
| `knowledge-graph-validation-plots` | `src/kg_validation_plots/__init__.py` | Package marker for the validation and plotting Python package. |
| `knowledge-graph-validation-plots` | `pyproject.toml` | Package metadata, dependencies, and `kg-validation` command registration. |

## ai-knowledge-graph

Install:

```bash
cd ai-knowledge-graph
pip install -e .
```

Run with text input:

```bash
copy config.example.toml config.toml
kg-build --config config.toml --input examples/sample_input.txt --schema generic --output-dir outputs --name sample
```

Excel input template:

```text
ai-knowledge-graph/examples/kg_input_template.xlsx
```

Prompt files:

```text
ai-knowledge-graph/prompts/generic.txt
ai-knowledge-graph/prompts/med_llm.txt
```

## literature-tools

Install:

```bash
cd literature-tools
pip install -e .
```

Commands:

```bash
lit-tools dedup --input input.xlsx --output outputs/deduped.xlsx --columns TI DI AB
lit-tools doi-map --input input.xlsx --output outputs/doi_mapped.xlsx --pmid-col PMID --doi-col DI
lit-tools enrich-openalex --input input.xlsx --output outputs/enriched.xlsx --title-col TI --doi-col DI --pmid-col PMID
lit-tools journal-if --input input.xlsx --reference reference/jcr.xlsx --output outputs/journal_if.xlsx
```

## 知识图谱的验证与有关绘图

Install:

```bash
cd knowledge-graph-validation-plots
pip install -e .
```

Commands:

```bash
kg-validation validate-llm --manual manual.xlsx --model model.xlsx --output outputs/validation.xlsx
kg-validation plot-validation --input outputs/validation.xlsx --output-dir outputs/validation_figures
```
