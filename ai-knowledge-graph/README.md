# Medical LLM Knowledge Graph Builder

This module builds knowledge graph JSON artifacts from medical LLM literature text.
The workflow covers:

1. Load text documents or Excel abstracts.
2. Call an OpenAI-compatible chat API.
3. Convert extracted entities into knowledge graph triples.
4. Save JSON graph artifacts.

## Features

- Generic Subject-Predicate-Object extraction.
- Medical LLM evaluation schema extraction:
  - LLM models
  - task types
  - benchmarks or datasets
  - evaluation metrics
  - safety issues
  - evaluation methods
- DOI tracking at triple and node level.
- Text input with multi-document boundaries.
- Optional Excel input for abstract and DOI columns.
- Prompt files are loaded from `prompts/`; the generic SPO prompt is provided, and task-specific prompts can be filled by the user.
- API keys are read from local environment variables.

## Install

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .
```

For Excel input:

```bash
pip install -e ".[excel]"
```

## Configure

Copy the example config and set your API key through an environment variable.

```bash
copy config.example.toml config.toml
set OPENAI_API_KEY=your_api_key_here
```

`config.toml` is a local runtime configuration file for environment-specific settings.

Prompt files are configured in `config.toml`:

```toml
[extraction]
med_llm_prompt = "prompts/med_llm.txt"
generic_prompt = "prompts/generic.txt"
```

Each prompt file contains two sections:

```text
[system]
Write your system prompt here.

[user]
Write your user prompt here. Use {text} where the document text should be inserted.
```

`prompts/generic.txt` contains a reusable generic SPO extraction prompt. Task-specific templates such as `prompts/med_llm.txt` are customizable; fill in both sections according to your own task before using that schema. The program will stop with a clear error if either section is blank or if `{text}` is missing.

## Run With Text

The simplest input is a UTF-8 `.txt` file. Put one document in plain text:

```text
Document title: Your title here.
Document abstract: Your abstract or source text here.
```

For multiple documents, use this exact boundary line:

```text
===== DOCUMENT BOUNDARY =====
```

Example:

```text
Document 1 title: First paper title.
Document 1 abstract: First paper abstract.

===== DOCUMENT BOUNDARY =====

Document 2 title: Second paper title.
Document 2 abstract: Second paper abstract.
```

If you have DOI values, create a JSON map using 1-based document numbers:

```json
{
  "1": "10.xxxx/first-doi",
  "2": "10.xxxx/second-doi"
}
```

See [examples/input_format.txt](examples/input_format.txt) for a copyable format.

```bash
kg-build --config config.toml --input examples\sample_input.txt --doi-map examples\sample_doi_map.json --schema generic --output-dir outputs --name sample
```

## Run With Excel

By default, Excel mode reads abstracts from column `AB` and DOIs from column `DI`.

Use [examples/kg_input_template.xlsx](examples/kg_input_template.xlsx) as the simplest Excel template. The `Input` sheet has these columns:

- `source_id`: optional row/document identifier
- `title`: optional title
- `AB`: required text column read by default
- `DI`: optional DOI column read by default
- `notes`: optional notes for the user

```bash
kg-build --config config.toml --excel papers.xlsx --text-column AB --doi-column DI --output-dir outputs --name papers
```

## Outputs

Each run writes:

- `<name>_graph.json`: graph metadata and triples.
- `<name>_node_dois.json`: DOI list for each node.
- `<name>_metadata.json`: run metadata and output file names.

The graph JSON uses this triple shape:

```json
{
  "subject": "GPT-4 [LLM]",
  "predicate": "performs",
  "object": "clinical question answering [Task]",
  "s_type": "LLM",
  "o_type": "Task",
  "doi": "10.0000/example",
  "source_id": "1",
  "provenance": "extracted"
}
```

## Repository Layout

```text
src/kg_builder/
  cli.py          command line entry point
  config.py       TOML and environment configuration
  extraction.py   LLM extraction and schema conversion
  inputs.py       text and Excel loading
  llm.py          OpenAI-compatible API client
  models.py       graph data models
  normalize.py    DOI and text normalization
  prompt_loader.py prompt file reader
  storage.py      JSON output writers
prompts/
  med_llm.txt     customizable template for task-specific medical LLM extraction prompts
  generic.txt     reusable generic SPO extraction prompt
```
