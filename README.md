# Chat-SGP (Smart Grid Prosumer)

A multi-agent system that uses natural language to solve renewable energy optimization problems. The pipeline processes questions about energy scenarios (e.g., "What happens if imports increase by 10%?"), modifies optimization models accordingly, solves them, and returns interpretable results.

## Paper

This repository implements the approach described in:

**Towards Explainable Renewable Energy Communities Operations Using Generative AI**  
Amal Nammouchi∗, Cyrine Chaabani†, Andreas Theocharis‡, Andreas Kassler∗

Paper: [IEEE Xplore](https://ieeexplore.ieee.org/abstract/document/10863790)

## Overview

Chat-SGP solves energy system optimization problems using a three-agent pipeline:

1. **Coder Agent**: Parses natural language questions and proposes modifications to the optimization model (scaling imports/exports/PV generation, shifting load between hours, etc.)
2. **Optimizer Agent**: Solves a mixed-integer linear program (MILP) for 24-hour energy optimization with PV generation, battery storage, and grid import/export
3. **Interpreter Agent**: Interprets optimization results and provides human-readable answers

The system optimizes battery charging/discharging and grid transactions to minimize energy costs while respecting physical constraints.

## Features

- Multi-agent pipeline (Coder → Optimizer → Interpreter)
- **LLM-powered agents** with ICL (In-Context Learning) examples for intelligent parsing and interpretation
- **Rule-based fallback** when LLM is not available
- **Debug logging** to trace prompts and responses for all agents
- Optional **AutoGen** orchestration (`scripts/autogen_pipeline.py`)
- Expanded dataset builder across 3 categories (`scripts/build_dataset.py`)
- **Gurobi** hooks + **IIS** (Irreducible Inconsistent Subsystem) infeasibility diagnostics
- Support for both **PuLP** (default) and **Gurobi** solvers
- Natural language question processing

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Explainable-REC
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate
```

3. Install the package:
```bash
pip install -e .
```

This will install all required dependencies from `requirements.txt`.

4. Set up environment variables:
```bash
cp .env_example .env
# Edit .env and add your OpenAI API key
```

**Note**: The system works without an API key using rule-based fallback, but LLM features require an OpenAI API key.

5. (Optional) Install additional dependencies:
```bash
# For AutoGen orchestration
pip install pyautogen

# For Gurobi solver (requires license)
pip install gurobipy
```

## Usage

### Standard Pipeline

Run the standard multi-agent pipeline:

```bash
python scripts/run_pipeline.py --question "What happens if imports increase by 10%?"
```

With debug output to see prompts and responses:
```bash
python scripts/run_pipeline.py --question "What happens if imports increase by 10%?" --debug
```

With Gurobi solver:
```bash
python scripts/run_pipeline.py --question "What happens if imports increase by 10%?" --solver gurobi
```

Output format:
```json
{
  "ops": {
    "ops": [
      {
        "op": "scale_series",
        "target": "Pimp",
        "scale_pct": 10.0
      }
    ],
    "explanation": "llm-with-icl"
  },
  "result": {
    "status": "optimal",
    "objective": 9.26
  },
  "answer": "In the scenario where import capacity increased by 10.0%, The total cost increases to EUR 9.26, which is +14.8% higher than the baseline scenario (EUR 8.06). The optimization found the most cost-effective way to manage energy storage, grid imports, and exports over the 24-hour period."
}
```

**Note**: The `explanation` field shows:
- `"llm-with-icl"` when using LLM with ICL examples
- `"rule-based"` when using rule-based fallback (no API key or LLM unavailable)

### AutoGen Pipeline

Use AutoGen for multi-agent orchestration:

```bash
python scripts/autogen_pipeline.py --question "What happens if imports increase by 10%?"
```

### Example Questions

The system can handle various question types:

- **Import/Export modifications**: "What happens if imports increase by 10%?", "Reduce exports by 15%"
- **PV generation changes**: "Increase PV generation by 20%", "What if PV decreases by 10%?"
- **Load shifting**: "What if we shift 25% of the load from hour 13 to hour 14?", "Shift 50% from hour 9 to hour 15"
- **Consumption changes**: "Increase consumption by 10%", "Decrease load by 20% during the day"

### Building a Dataset

Generate test questions for evaluation:

```bash
python scripts/build_dataset.py --out questions.jsonl --n 60
```

This generates questions across three categories:
- `QPimpPexp`: Import/export percentage changes
- `QPconsPprod`: Consumption/production changes
- `QPshift`: Load shifting scenarios

## Architecture

### Agents

- **CoderAgent** (`chatsgp/agents/coder_agent.py`): 
  - Uses LLM with ICL examples for intelligent question parsing (when API key is available)
  - Falls back to rule-based pattern matching when LLM is unavailable
  - Extracts modifications from natural language questions
  - ICL examples: `chatsgp/icl/examples.jsonl`
  
- **OptimizerAgent** (`chatsgp/agents/optimizer_agent.py`): 
  - Runs MILP optimization with PuLP or Gurobi
  - Applies modifications to the optimization model
  - Solves 24-hour energy optimization problem
  
- **InterpreterAgent** (`chatsgp/agents/interpreter_agent.py`): 
  - Uses LLM with ICL examples to generate human-readable interpretations (when API key is available)
  - Falls back to rule-based interpretation when LLM is unavailable
  - Compares results with baseline scenario
  - ICL examples: `chatsgp/icl/interpreter_examples.jsonl`

### Optimization Model

The system solves a 24-hour energy optimization problem with:
- **Load**: Hourly energy demand
- **PV**: Hourly solar generation
- **Battery**: Storage with capacity, efficiency, and power limits
- **Grid**: Import/export with different prices

The objective is to minimize total cost: `minimize(price_import × Pimp - price_export × Pexp)`

Subject to:
- Energy balance: `Load = PV + Battery_Discharge + Pimp - Battery_Charge - Pexp`
- Battery state of charge constraints
- Power limits

## Solver Options

- **PuLP** (default): Open-source, no license required
- **Gurobi**: Commercial solver with better performance and IIS diagnostics for infeasible problems

## Debug Mode

Enable debug logging to see prompts and responses for all agents:

```bash
python scripts/run_pipeline.py --question "What happens if PV generation increases by 20%?" --debug
```

This will show:
- Input questions and ICL examples used
- LLM prompts sent to CoderAgent and InterpreterAgent
- LLM responses received
- Optimization data and results
- Final interpretations

## ICL (In-Context Learning) Examples

The system uses ICL examples to improve LLM performance:

- **CoderAgent ICL**: `chatsgp/icl/examples.jsonl` - Example question-to-operation mappings
- **InterpreterAgent ICL**: `chatsgp/icl/interpreter_examples.jsonl` - Example interpretation patterns

You can add more examples to these files to improve the system's understanding of different scenarios.

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.

Copyright 2024 Cyrine Chaabani

## Contributing

We welcome contributions to Chat-SGP! Here are some guidelines to help you get started:

### Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/SGP-Chat.git`
3. Create a new branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test your changes to ensure they work correctly
6. Commit your changes: `git commit -m "Add your descriptive message"`
7. Push to your fork: `git push origin feature/your-feature-name`
8. Open a Pull Request

### Code Style

- Follow Python PEP 8 style guidelines
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and modular

### Testing

- Test your changes before submitting a PR
- Ensure existing functionality still works
- Add tests for new features if applicable

### Pull Request Process

1. Ensure your code follows the project's style guidelines
2. Update documentation if needed
3. Make sure all tests pass
4. Provide a clear description of your changes in the PR
5. Reference any related issues

### Areas for Contribution

- Bug fixes
- Performance improvements
- Additional question types for the Coder Agent
- Enhanced optimization models
- Documentation improvements
- Test coverage

### Questions?

If you have questions or need help, please open an issue on GitHub.

## Citation

If you use this code in your research, please cite the following paper:

```bibtex
@inproceedings{nammouchi2024explainable,
  title={Towards Explainable Renewable Energy Communities Operations Using Generative AI},
  author={Nammouchi, Amal and Chaabani, Cyrine and Theocharis, Andreas and Kassler, Andreas},
  booktitle={IEEE Conference},
  year={2024},
  doi={10.1109/XXXX.2024.10863790}
}
```

Or in plain text:

> Nammouchi, A., Chaabani, C., Theocharis, A., & Kassler, A. (2024). Towards Explainable Renewable Energy Communities Operations Using Generative AI. *IEEE Conference*. DOI: 10.1109/XXXX.2024.10863790

Paper link: [IEEE Xplore](https://ieeexplore.ieee.org/abstract/document/10863790)
