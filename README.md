# medical-llm-knowledge-graph

Medical LLM literature workflow codebase.

Python version:

```text
Python 3.13.11
```

## Modules

- `ai-knowledge-graph/`: knowledge graph extraction and JSON storage.
- `literature-tools/`: literature deduplication, metadata enrichment, journal metrics, validation, and plotting utilities.

## Project Structure

```text
medical-llm-knowledge-graph/
  ai-knowledge-graph/
  literature-tools/
  README.md
```

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
lit-tools validate-llm --manual manual.xlsx --model model.xlsx --output outputs/validation.xlsx
lit-tools plot-summary --input input.xlsx --output-dir outputs/figures
```
