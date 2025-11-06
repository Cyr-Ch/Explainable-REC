"""
Enhanced CLI for Chat-SGP pipeline

Supports:
- Configuration file loading
- Multiple output formats (json, yaml, text)
- Saving results to file
- Interactive Q&A mode
- Visualization
"""

import argparse
import json
import os
import sys
from pathlib import Path
import yaml

from chatsgp.agents.coder_agent import CoderAgent
from chatsgp.agents.optimizer_agent import OptimizerAgent
from chatsgp.agents.interpreter_agent import InterpreterAgent
from chatsgp.agents.orchestrator import Orchestrator
from chatsgp.utils.llm_backend import LLM
from chatsgp.config import get_config
from chatsgp.utils.visualization import plot_energy_flows, plot_cost_comparison


def load_icl(path='chatsgp/icl/examples.jsonl'):
    """Load ICL examples"""
    p = Path(path)
    ex = []
    if p.exists():
        for line in p.read_text(encoding='utf-8').splitlines():
            ex.append(json.loads(line))
    return ex


def format_output(result, format_type='json'):
    """Format output based on format type"""
    if format_type == 'json':
        return json.dumps(result, indent=2, ensure_ascii=False)
    elif format_type == 'yaml':
        return yaml.dump(result, default_flow_style=False, allow_unicode=True)
    elif format_type == 'text':
        output = []
        output.append("=" * 60)
        output.append("Chat-SGP Results")
        output.append("=" * 60)
        output.append(f"\nQuestion: {result.get('question', 'N/A')}")
        output.append(f"\nOperations:")
        for op in result.get('ops', {}).get('ops', []):
            output.append(f"  - {op}")
        output.append(f"\nOptimization Result:")
        output.append(f"  Status: {result.get('result', {}).get('status', 'N/A')}")
        output.append(f"  Objective: EUR {result.get('result', {}).get('objective', 0):.2f}")
        output.append(f"\nAnswer:")
        output.append(result.get('answer', 'N/A'))
        output.append("\n" + "=" * 60)
        return "\n".join(output)
    else:
        raise ValueError(f"Unknown format: {format_type}")


def save_output(output, output_path, format_type='json'):
    """Save output to file"""
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    if format_type == 'json':
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
    elif format_type == 'yaml':
        with open(output_file, 'w', encoding='utf-8') as f:
            yaml.dump(output, f, default_flow_style=False, allow_unicode=True)
    else:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output)
    
    print(f"Results saved to {output_file}")


def interactive_mode(orchestrator, solver='pulp', format_type='text'):
    """Interactive Q&A mode"""
    print("=" * 60)
    print("Chat-SGP Interactive Mode")
    print("=" * 60)
    print("\nEnter questions about energy scenarios.")
    print("Type 'quit' or 'exit' to exit, 'help' for examples.\n")
    
    while True:
        try:
            question = input("Question: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye!")
                break
            
            if question.lower() == 'help':
                print("\nExample questions:")
                print("  - What happens if PV generation increases by 20%?")
                print("  - What happens if imports increase by 10%?")
                print("  - What if we shift 25% of load from hour 13 to hour 14?")
                print("  - What happens if exports decrease by 15%?")
                print()
                continue
            
            if not question:
                continue
            
            print("\nProcessing...")
            result = orchestrator.run_question(question, solver=solver)
            result['question'] = question  # Add question to result
            
            output = format_output(result, format_type)
            print(output)
            print()
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}\n")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Chat-SGP: Renewable Energy Optimization Pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python scripts/run_pipeline.py --question "What happens if PV increases by 20%?"
  
  # With configuration file
  python scripts/run_pipeline.py --question "What if imports increase by 10%?" --config config.yaml
  
  # Save results to file
  python scripts/run_pipeline.py --question "What if we shift load?" --output results.json
  
  # Text format output
  python scripts/run_pipeline.py --question "What happens if PV increases by 20%?" --format text
  
  # Interactive mode
  python scripts/run_pipeline.py --interactive
  
  # With visualization
  python scripts/run_pipeline.py --question "What happens if PV increases by 20%?" --plot
        """
    )
    
    parser.add_argument('--question', '-q', 
                       help='Question about energy scenario (required unless --interactive)')
    parser.add_argument('--solver', '-s', default='pulp', choices=['pulp', 'gurobi'],
                       help='Optimization solver to use (default: pulp)')
    parser.add_argument('--config', '-c',
                       help='Path to configuration file (YAML or JSON)')
    parser.add_argument('--output', '-o',
                       help='Path to save results (JSON, YAML, or TXT)')
    parser.add_argument('--format', '-f', default='json', choices=['json', 'yaml', 'text'],
                       help='Output format (default: json)')
    parser.add_argument('--interactive', '-i', action='store_true',
                       help='Start interactive Q&A mode')
    parser.add_argument('--plot', '-p', action='store_true',
                       help='Generate and display visualization plots')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug output showing prompts and responses')
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.interactive and not args.question:
        parser.error("--question is required unless --interactive is used")
    
    # Set debug environment variable
    if args.debug:
        os.environ['DEBUG'] = 'true'
    
    # Load configuration if provided
    config = get_config(args.config) if args.config else get_config()
    
    # Initialize agents
    icl_examples = load_icl()
    llm = LLM()
    coder = CoderAgent(icl_examples, llm=llm)
    optimizer = OptimizerAgent(config=config)
    interpreter = InterpreterAgent()
    orchestrator = Orchestrator(coder, optimizer, interpreter)
    
    # Interactive mode
    if args.interactive:
        interactive_mode(orchestrator, solver=args.solver, format_type=args.format)
        sys.exit(0)
    
    # Single question mode
    try:
        result = orchestrator.run_question(args.question, solver=args.solver)
        result['question'] = args.question  # Add question to result
        
        # Generate plots if requested
        if args.plot:
            try:
                ops = result['ops']
                data, res = optimizer.run(ops, solver=args.solver)
                
                # Plot energy flows
                plot_energy_flows(data, res, show=True)
                
                # Plot cost comparison if baseline available
                baseline_ops = {'ops': [], 'explanation': 'baseline'}
                baseline_data, baseline_res = optimizer.run(baseline_ops, solver=args.solver)
                baseline_cost = baseline_res['objective']
                scenario_cost = result['result']['objective']
                
                plot_cost_comparison(
                    baseline_cost,
                    scenario_cost,
                    scenario_name="Scenario",
                    show=True
                )
            except Exception as e:
                print(f"Warning: Could not generate plots: {e}", file=sys.stderr)
        
        # Format output
        output = format_output(result, args.format)
        
        # Save or print output
        if args.output:
            save_output(result if args.format in ['json', 'yaml'] else output, 
                       args.output, args.format)
        else:
            print(output)
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
