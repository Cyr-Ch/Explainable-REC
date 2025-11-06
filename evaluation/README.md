# Evaluation Framework

This directory contains the evaluation framework for Chat-SGP, providing metrics, benchmark runners, and result comparison tools.

## Structure

- `metrics.py` - Evaluation metrics (cost accuracy, parsing accuracy, success rate, etc.)
- `benchmark.py` - Benchmark runner for running evaluations on question sets
- `compare_results.py` - Tools for comparing results from different runs
- `datasets/` - Test question datasets for evaluation

## Usage

### Running Benchmarks

```python
from evaluation.benchmark import run_benchmark

results = run_benchmark(
    questions_file='evaluation/datasets/test_questions.jsonl',
    output_file='results.jsonl',
    solver='pulp'
)

print(f"Success rate: {results['evaluation']['success_rate']:.1f}%")
```

### Calculating Metrics

```python
from evaluation.metrics import generate_evaluation_report

# Load results from file
results = load_results('results.jsonl')

# Generate report
report = generate_evaluation_report(results)
print(f"Success rate: {report['success_rate']:.1f}%")
print(f"Average cost: EUR {report['average_cost']:.2f}")
```

### Comparing Results

```python
from evaluation.compare_results import compare_result_files

comparison = compare_result_files(
    'results1.jsonl',
    'results2.jsonl',
    label1='Baseline',
    label2='Modified'
)

print(f"Cost difference: EUR {comparison['difference']['cost_difference']:.2f}")
```

## Metrics

The evaluation framework provides the following metrics:

- **Success Rate**: Percentage of successful optimizations
- **Parsing Accuracy**: Distribution of LLM vs rule-based parsing
- **Average Cost**: Average cost across successful optimizations
- **Cost Accuracy**: Accuracy of cost predictions (if ground truth available)

## Datasets

Test question datasets should be placed in `evaluation/datasets/` directory. Questions should be in JSONL format:

```json
{"question": "What happens if PV generation increases by 20%?"}
{"question": "What if we shift 25% of the load from hour 13 to hour 14?"}
```

## Future Enhancements

- Ground truth comparison
- Statistical significance testing
- Visualization of evaluation results
- Automated evaluation reports

