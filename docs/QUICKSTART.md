# Quick Start Guide

This guide will help you get started with Chat-SGP in just a few minutes.

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd Explainable-REC
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Linux/Mac:
   source venv/bin/activate
   ```

3. **Install the package**:
   ```bash
   pip install -e .
   ```

4. **Set up your API key** (optional but recommended):
   ```bash
   cp .env_example .env
   # Edit .env and add your OpenAI API key
   ```

## Basic Usage

### Run a Simple Question

```bash
python scripts/run_pipeline.py --question "What happens if PV generation increases by 20%?"
```

### With Debug Output

```bash
python scripts/run_pipeline.py --question "What happens if PV generation increases by 20%?" --debug
```

### Using Gurobi Solver

```bash
python scripts/run_pipeline.py --question "What happens if imports increase by 10%?" --solver gurobi
```

## Using Configuration Files

1. **Create a configuration file**:
   ```bash
   cp config.yaml.example config.yaml
   ```

2. **Edit `config.yaml`** to customize:
   - Battery parameters (capacity, efficiency, power limits)
   - Energy prices (import/export)
   - LLM settings
   - Default solver

3. **The system will automatically use your config** when you run:
   ```bash
   python scripts/run_pipeline.py --question "Your question here"
   ```

## Example Questions

The system can handle various types of questions:

- **PV Generation**: "What happens if PV generation increases by 20%?"
- **Imports**: "What happens if imports increase by 10%?"
- **Exports**: "Reduce exports by 15%"
- **Load Shifting**: "What if we shift 25% of load from hour 13 to hour 14?"
- **Consumption**: "Increase consumption by 10%"

## Running Examples

### Quick Start Example

```bash
python examples/quickstart.py
```

This will run several example scenarios and show you how the system works.

### Configuration Example

```bash
python examples/example_with_config.py
```

This shows how to use custom configuration files.

## Understanding the Output

The system returns a JSON object with:

- **`ops`**: The operations extracted from your question
  - `ops`: List of operations (scale_series, shift_load, etc.)
  - `explanation`: Method used ("llm-with-icl" or "rule-based")
  
- **`result`**: Optimization results
  - `status`: "optimal", "infeasible", etc.
  - `objective`: Total cost in EUR
  
- **`answer`**: Human-readable interpretation

## Troubleshooting

### "LLM client is NOT available"

This means no API key is configured. The system will still work using rule-based parsing, but LLM features won't be available.

**Solution**: Add your OpenAI API key to `.env` file:
```
OPENAI_API_KEY=your_api_key_here
```

### "Invalid question" error

Make sure your question includes:
- A percentage (e.g., "10%", "20%")
- A valid keyword (import, export, PV, shift, consumption, load)

**Example**: "What happens if PV generation increases by 20%?" ✓

### Optimization fails

If you get "infeasible" status, the scenario might not be physically possible with the current constraints.

**Solution**: Try adjusting the parameters in `config.yaml` or use a different scenario.

## Next Steps

- Read the [README.md](../README.md) for detailed documentation
- Check [IMPROVEMENTS.md](../IMPROVEMENTS.md) for planned features
- Explore the code in `chatsgp/agents/` to understand the architecture
- Add your own ICL examples to improve LLM performance

## Getting Help

- Check the [README.md](../README.md) for detailed information
- Review example code in `examples/` directory
- Open an issue on GitHub if you encounter problems

