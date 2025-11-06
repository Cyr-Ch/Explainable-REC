# Chat-SGP (Smart Grid Prosumer)

**Ask natural-language questions about your renewable energy system and get optimized action plans with human-readable explanations.**

Chat-SGP is a multi-agent system that transforms natural language questions (e.g., "What happens if imports increase by 10%?") into optimized energy management strategies. The system processes your questions, modifies optimization models accordingly, solves them, and returns interpretable results with actionable insights.

## Paper

This repository implements the approach described in:

**Towards Explainable Renewable Energy Communities Operations Using Generative AI**  
Amal Nammouchi∗, Cyrine Chaabani†, Andreas Theocharis‡, Andreas Kassler∗

Paper: [IEEE Xplore](https://ieeexplore.ieee.org/abstract/document/10863790)

---

## 🎯 Why use this?

Chat-SGP makes renewable energy optimization **accessible to everyone**—no optimization expertise required. Simply ask questions in plain English and get:

- ✅ **Instant insights**: Understand how changes to PV generation, load patterns, or energy prices affect your system
- ✅ **Optimized solutions**: Get cost-minimized energy management strategies for 24-hour periods
- ✅ **Human-readable explanations**: Understand *why* the system recommends specific actions
- ✅ **Flexible scenarios**: Test "what-if" scenarios without writing code or modifying optimization models
- ✅ **Production-ready**: Works with or without LLM APIs, includes comprehensive tests and documentation

Perfect for energy managers, researchers, and developers working with renewable energy systems.

---

## 🚀 Quickstart (1-2 commands)

Get started in minutes:

```bash
# 1. Install and setup
pip install -e .
cp .env_example .env  # Optional: Add OpenAI API key for LLM features

# 2. Ask your first question
python scripts/run_pipeline.py --question "What happens if PV generation increases by 20%?"
```

That's it! The system will:
1. Parse your question
2. Optimize the energy system
3. Return a human-readable answer with cost analysis

**Interactive mode:**
```bash
python scripts/run_pipeline.py --interactive
```

**With visualization:**
```bash
python scripts/run_pipeline.py --question "What happens if imports increase by 10%?" --plot
```

---

## 📚 How it works (agents + optimiser)

Chat-SGP uses a three-agent pipeline to transform questions into optimized solutions:

### 1. **Coder Agent** → Understands your question
- Parses natural language questions using LLM (with ICL examples) or rule-based fallback
- Extracts modifications: scaling imports/exports/PV generation, shifting load between hours, etc.
- Outputs structured operations for the optimizer

### 2. **Optimizer Agent** → Solves the problem
- Solves a mixed-integer linear program (MILP) for 24-hour energy optimization
- Considers PV generation, battery storage, and grid import/export
- Minimizes total energy cost while respecting physical constraints
- Supports PuLP (open-source) and Gurobi (commercial) solvers

### 3. **Interpreter Agent** → Explains the results
- Interprets optimization results using LLM (with ICL examples) or rule-based fallback
- Compares scenario results with baseline
- Provides human-readable explanations with cost analysis and insights

**The system optimizes battery charging/discharging and grid transactions to minimize energy costs while respecting physical constraints.**

## Features

- Multi-agent pipeline (Coder → Optimizer → Interpreter)
- **LLM-powered agents** with ICL (In-Context Learning) examples for intelligent parsing and interpretation
- **Rule-based fallback** when LLM is not available
- **Debug logging** to trace prompts and responses for all agents
- **Configuration file support** (YAML/JSON) for easy customization
- **Input validation** and helpful error messages
- **Unit tests** and integration tests for reliability
- **Enhanced CLI** with interactive mode, multiple output formats, and visualization
- **Result visualization** with energy flow plots and cost comparison charts
- **Jupyter notebook tutorial** for interactive learning
- **Example scenarios** for residential, commercial, and grid analysis use cases
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

5. (Optional) Create configuration file:
```bash
cp config.yaml.example config.yaml
# Edit config.yaml to customize system parameters
```

6. (Optional) Install additional dependencies:
```bash
# For AutoGen orchestration
pip install pyautogen

# For Gurobi solver (requires license)
pip install gurobipy

# For development (testing, linting)
pip install -r requirements-dev.txt
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

### Enhanced CLI Features

The CLI supports many additional options:

**Configuration file:**
```bash
python scripts/run_pipeline.py --question "What happens if PV increases by 20%?" --config config.yaml
```

**Save results to file:**
```bash
python scripts/run_pipeline.py --question "What if we shift load?" --output results.json
```

**Different output formats:**
```bash
# JSON (default)
python scripts/run_pipeline.py --question "What happens if PV increases by 20%?" --format json

# YAML
python scripts/run_pipeline.py --question "What happens if PV increases by 20%?" --format yaml

# Human-readable text
python scripts/run_pipeline.py --question "What happens if PV increases by 20%?" --format text
```

**Interactive mode:**
```bash
python scripts/run_pipeline.py --interactive
```

This starts an interactive Q&A session where you can ask multiple questions. Type `help` for example questions, or `quit` to exit.

**Visualization:**
```bash
python scripts/run_pipeline.py --question "What happens if PV increases by 20%?" --plot
```

This generates plots showing:
- 24-hour energy flows (PV, Load, Battery, Grid)
- Cost comparison between baseline and scenario

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

### Running Examples

Try the example scripts:

```bash
# Quick start examples
python examples/quickstart.py

# Configuration example
python examples/example_with_config.py
```

### Jupyter Notebook Tutorial

For an interactive tutorial with visualizations, open the Jupyter notebook:

```bash
jupyter notebook examples/tutorial.ipynb
```

The tutorial covers:
- Basic usage and setup
- Different question types
- Visualizing results
- Comparing scenarios
- Customizing parameters

### Example Scenarios

Explore real-world scenarios with different parameter sets:

```bash
# Residential energy community
python examples/scenarios/residential_energy_community.py

# Commercial building
python examples/scenarios/commercial_building.py

# Grid impact analysis
python examples/scenarios/grid_impact_analysis.py
```

Each scenario demonstrates:
- Different battery capacities and power limits
- Custom PV and load profiles
- Different energy prices
- Multiple scenario comparisons

### Running Tests

Run the test suite:

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_coder_agent.py
```

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

## Configuration

The system supports configuration files for easy customization. Create a `config.yaml` file:

```yaml
# Battery configuration
battery:
  capacity_kwh: 5.0
  efficiency: 0.95
  max_power: 2.0
  initial_soc: 0.5

# Energy prices
prices:
  import: 0.25  # EUR/kWh
  export: 0.10  # EUR/kWh

# LLM configuration
llm:
  model: "gpt-4o-mini"
  temperature: 0.0
  max_tokens: 300

# Optimization settings
optimization:
  default_solver: "pulp"
  hours: 24
```

The system will automatically load `config.yaml` if it exists in the project root. See `config.yaml.example` for a template.

## Testing

The repository includes comprehensive tests:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=chatsgp

# Run specific test file
pytest tests/test_coder_agent.py -v
```

Test coverage includes:
- Unit tests for each agent
- Integration tests for the full pipeline
- Validation tests
- Error handling tests

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.

Copyright 2024 Cyrine Chaabani

## 🧑‍💻 How to contribute

We welcome contributions to Chat-SGP! Whether you're fixing bugs, adding features, or improving documentation, your help makes this project better.

### Getting Started

1. **Fork the repository** and clone your fork
2. **Create a new branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes** and test them
4. **Commit your changes**: `git commit -m "Add your descriptive message"`
5. **Push to your fork**: `git push origin feature/your-feature-name`
6. **Open a Pull Request** with a clear description

### Good First Issues

Looking for a place to start? Check out issues tagged with:
- [`good first issue`](https://github.com/yourusername/Explainable-REC/labels/good%20first%20issue) - Great for newcomers
- [`help wanted`](https://github.com/yourusername/Explainable-REC/labels/help%20wanted) - Community help needed

**Note**: If you don't see any tagged issues yet, check the [IMPROVEMENTS.md](IMPROVEMENTS.md) file for ideas on what to work on!

### Code Style

- Follow Python PEP 8 style guidelines
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and modular

### Testing

- Test your changes before submitting a PR: `pytest`
- Ensure existing functionality still works
- Add tests for new features if applicable

### Pull Request Process

1. Ensure your code follows the project's style guidelines
2. Update documentation if needed
3. Make sure all tests pass: `pytest`
4. Provide a clear description of your changes in the PR
5. Reference any related issues

### Areas for Contribution

- 🐛 **Bug fixes**: Help us improve stability
- ⚡ **Performance improvements**: Make the system faster
- 🆕 **New features**: See [IMPROVEMENTS.md](IMPROVEMENTS.md) for ideas
- 📝 **Documentation**: Improve clarity and examples
- 🧪 **Test coverage**: Add more tests
- 🎨 **UI/UX**: Improve CLI or add web interface

### Questions?

If you have questions or need help, please:
- Open an issue on GitHub
- Check the [IMPROVEMENTS.md](IMPROVEMENTS.md) for roadmap ideas
- Review existing issues and pull requests

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
