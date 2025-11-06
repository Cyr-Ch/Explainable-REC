# Evaluation Datasets

This directory contains test question datasets for evaluation.

## Format

Questions should be in JSONL format (one JSON object per line):

```json
{"question": "What happens if PV generation increases by 20%?"}
{"question": "What if we shift 25% of the load from hour 13 to hour 14?"}
{"question": "Reduce exports by 15%. What is the new cost?"}
```

## Generating Datasets

Use the dataset generation script:

```bash
python scripts/pipelines/dataset_generation/build_dataset.py \
    --out evaluation/datasets/test_questions.jsonl \
    --n 60
```

## Categories

The dataset generation script creates questions across three categories:

- **QPimpPexp**: Import/export percentage changes
- **QPconsPprod**: Consumption/production changes
- **QPshift**: Load shifting scenarios

