# Prompt Templates

This directory contains prompt templates used by the Chat-SGP agents.

## Files

- `coder_system.txt` - System prompt for CoderAgent
- `coder_user_template.txt` - User prompt template for CoderAgent (with placeholders)
- `interpreter_system.txt` - System prompt for InterpreterAgent
- `interpreter_user_template.txt` - User prompt template for InterpreterAgent (with placeholders)

## Usage

Prompts are loaded and used by the agents in:
- `chatsgp/agents/coder_agent.py` - Uses coder prompts
- `chatsgp/agents/interpreter_agent.py` - Uses interpreter prompts

## Template Variables

### CoderAgent Template Variables
- `{examples_text}` - ICL examples formatted as text
- `{question}` - The natural language question to parse

### InterpreterAgent Template Variables
- `{examples_text}` - ICL examples formatted as text
- `{modifications}` - Description of scenario modifications
- `{status}` - Optimization status (optimal, infeasible, etc.)
- `{objective}` - Total cost objective value
- `{baseline_info}` - Baseline cost information (if available)
- `{cost_change_info}` - Cost change information (if available)
- `{pv_profile}` - PV generation profile array
- `{load_profile}` - Load profile array
- `{battery_capacity_kwh}` - Battery capacity in kWh
- `{price_import}` - Import price per kWh
- `{price_export}` - Export price per kWh

## Modifying Prompts

To modify prompts:
1. Edit the template files in this directory
2. Update the agent code to load from these files (if not already implemented)
3. Test with example questions to ensure prompts work correctly

## Note

The current implementation embeds prompts in the agent code. Future versions will load from these template files for easier modification and reproducibility.

