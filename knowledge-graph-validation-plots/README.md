# Knowledge Graph Validation and Plots

Python version:

```text
Python 3.13.11
```

This folder contains the knowledge graph validation and related plotting code.

## Install

```bash
cd knowledge-graph-validation-plots
pip install -e .
```

## Commands

Evaluate model extraction output against manual annotations:

```bash
kg-validation validate-llm --manual manual.xlsx --model model.xlsx --output outputs/validation.xlsx
```

Create basic descriptive plots from a cleaned knowledge graph or literature table:

```bash
kg-validation plot-summary --input input.xlsx --output-dir outputs/figures
```

## Organization

```text
src/kg_validation_plots/
  cli.py          command line interface
  common.py       shared table loading and column helpers
  validation.py   manual vs model extraction evaluation
  plotting.py     reusable summary chart functions
```
