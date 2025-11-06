# Pipelines

This directory contains test scripts organized by task type, following the LLMFP repository structure.

## Structure

- `energy_optimization/` - Energy optimization test scripts
  - `test_residential.py` - Residential energy community scenarios
  - `test_commercial.py` - Commercial building scenarios
  - `test_grid_analysis.py` - Grid impact analysis scenarios
- `batch_evaluation/` - Batch evaluation scripts
  - `run_batch.py` - Run pipeline on multiple questions from a file
- `dataset_generation/` - Dataset generation scripts
  - `build_dataset.py` - Generate test questions for evaluation

## Usage

### Energy Optimization Tests

```bash
# Test residential scenarios
python scripts/pipelines/energy_optimization/test_residential.py

# Test commercial scenarios
python scripts/pipelines/energy_optimization/test_commercial.py

# Test grid analysis scenarios
python scripts/pipelines/energy_optimization/test_grid_analysis.py
```

### Batch Evaluation

```bash
# Run batch evaluation on questions
python scripts/pipelines/batch_evaluation/run_batch.py \
    --input questions.jsonl \
    --output results.jsonl \
    --solver pulp
```

### Dataset Generation

```bash
# Generate test questions
python scripts/pipelines/dataset_generation/build_dataset.py \
    --out questions.jsonl \
    --n 60
```

## Organization

This structure follows the LLMFP repository pattern of organizing test scripts by task type, making it easier to:
- Find task-specific scripts
- Run specific test suites
- Add new task types
- Maintain clear separation of concerns

