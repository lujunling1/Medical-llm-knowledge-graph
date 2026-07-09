# Knowledge Graph Validation

Python version:

```text
Python 3.13.11
```

This folder contains a combined code file for knowledge graph extraction validation.
The plotting functions draw validation-result charts.

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

Evaluate and create validation charts in the same run:

```bash
kg-validation validate-llm --manual manual.xlsx --model model.xlsx --output outputs/validation.xlsx --plot-dir outputs/validation_figures
```

Create validation charts from an existing validation result table:

```bash
kg-validation plot-validation --input outputs/validation.xlsx --output-dir outputs/validation_figures
```

The chart command writes:

```text
exact_validation_scores.png
semantic_validation_scores.png
validation_entity_counts.png
```

## Organization

```text
src/kg_validation_plots/
  main.py        validation, validation-result plotting, table I/O, and command line interface
```
