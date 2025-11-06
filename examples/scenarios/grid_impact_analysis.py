"""
Grid Impact Analysis Scenario

This scenario analyzes the impact of different energy scenarios on grid interactions:
- Baseline vs. modified scenarios
- Grid import/export patterns
- Cost comparisons
- Multiple scenario analysis

Use case: Analyzing how different energy scenarios affect grid interactions and costs.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from chatsgp.agents.coder_agent import CoderAgent
from chatsgp.agents.optimizer_agent import OptimizerAgent
from chatsgp.agents.interpreter_agent import InterpreterAgent
from chatsgp.agents.orchestrator import Orchestrator
from chatsgp.utils.llm_backend import LLM
from chatsgp.config import Config
from chatsgp.utils.visualization import plot_cost_comparison, plot_multiple_scenarios
import json
import numpy as np


def load_icl(path='chatsgp/icl/examples.jsonl'):
    """Load ICL examples"""
    p = Path(path)
    ex = []
    if p.exists():
        for line in p.read_text(encoding='utf-8').splitlines():
            ex.append(json.loads(line))
    return ex


def create_grid_analysis_config():
    """Create configuration for grid impact analysis"""
    # Standard PV profile
    pv_profile = np.array([
        0, 0, 0, 0, 0, 0.2, 0.5, 1, 1.5, 2, 2.2, 2, 1.5, 1, 0.8, 0.5, 0.2, 0, 0, 0, 0, 0, 0, 0
    ])
    
    # Standard load profile
    load_profile = np.array([2.0] * 24)
    
    config_dict = {
        'battery': {
            'capacity_kwh': 5.0,
            'efficiency': 0.95,
            'max_power': 2.0,
            'initial_soc': 0.5
        },
        'prices': {
            'import': 0.25,
            'export': 0.10
        },
        'optimization': {
            'default_solver': 'pulp',
            'hours': 24
        },
        'pv_profile': pv_profile.tolist(),
        'load_profile': load_profile.tolist()
    }
    
    return Config(config_dict=config_dict)


def main():
    """Run grid impact analysis scenario"""
    print("=" * 60)
    print("Grid Impact Analysis Scenario")
    print("=" * 60)
    print("\nThis scenario analyzes the impact of different energy scenarios")
    print("on grid interactions and total costs.\n")
    
    # Create configuration
    config = create_grid_analysis_config()
    
    # Initialize agents
    icl_examples = load_icl()
    llm = LLM()
    coder = CoderAgent(icl_examples, llm=llm)
    optimizer = OptimizerAgent(config=config)
    interpreter = InterpreterAgent()
    orchestrator = Orchestrator(coder, optimizer, interpreter)
    
    # Get baseline
    print("Calculating baseline scenario...")
    baseline_ops = {'ops': [], 'explanation': 'baseline'}
    baseline_data, baseline_res = optimizer.run(baseline_ops, solver='pulp')
    baseline_cost = baseline_res['objective']
    
    print(f"Baseline Cost: EUR {baseline_cost:.2f}\n")
    
    # Scenarios to analyze
    scenarios = [
        {
            'name': 'Baseline',
            'question': None,
            'cost': baseline_cost
        },
        {
            'name': 'PV +20%',
            'question': 'What happens if PV generation increases by 20%?'
        },
        {
            'name': 'PV +50%',
            'question': 'What happens if PV generation increases by 50%?'
        },
        {
            'name': 'Import +15%',
            'question': 'What happens if imports increase by 15%?'
        },
        {
            'name': 'Load Shift',
            'question': 'What if we shift 25% of load from hour 13 to hour 14?'
        },
    ]
    
    print("=" * 60)
    print("Running Scenarios")
    print("=" * 60)
    
    results = []
    for scenario in scenarios:
        if scenario['question'] is None:
            # Baseline already calculated
            results.append({
                'name': scenario['name'],
                'cost': scenario['cost'],
                'status': 'optimal'
            })
            continue
        
        print(f"\n--- {scenario['name']} ---")
        print(f"Question: {scenario['question']}")
        
        try:
            result = orchestrator.run_question(scenario['question'], solver='pulp')
            cost = result['result']['objective']
            status = result['result']['status']
            
            print(f"[OK] Status: {status}")
            print(f"[OK] Total Cost: EUR {cost:.2f}")
            
            # Calculate change from baseline
            change = cost - baseline_cost
            change_pct = (change / baseline_cost) * 100 if baseline_cost > 0 else 0
            print(f"[OK] Change: EUR {change:+.2f} ({change_pct:+.1f}%)")
            
            results.append({
                'name': scenario['name'],
                'cost': cost,
                'status': status,
                'change': change,
                'change_pct': change_pct
            })
        except Exception as e:
            print(f"[ERROR] Error: {e}")
            results.append({
                'name': scenario['name'],
                'error': str(e)
            })
    
    # Summary table
    print("\n" + "=" * 60)
    print("Summary Table")
    print("=" * 60)
    print(f"{'Scenario':<20} {'Cost (EUR)':<15} {'Change (EUR)':<15} {'Change (%)':<12}")
    print("-" * 60)
    
    for r in results:
        if 'cost' in r:
            change_str = f"{r.get('change', 0):+.2f}" if 'change' in r else "N/A"
            change_pct_str = f"{r.get('change_pct', 0):+.1f}%" if 'change_pct' in r else "N/A"
            print(f"{r['name']:<20} {r['cost']:<15.2f} {change_str:<15} {change_pct_str:<12}")
        else:
            print(f"{r['name']:<20} {'ERROR':<15} {'N/A':<15} {'N/A':<12}")
    
    # Visualization
    print("\n" + "=" * 60)
    print("Generating Visualizations")
    print("=" * 60)
    
    try:
        # Cost comparison for first scenario
        if len(results) > 1 and 'cost' in results[1]:
            plot_cost_comparison(
                baseline_cost,
                results[1]['cost'],
                scenario_name=results[1]['name'],
                show=True
            )
        
        # Multiple scenarios comparison
        scenario_data = [{'name': r['name'], 'cost': r['cost']} 
                        for r in results if 'cost' in r]
        if len(scenario_data) > 1:
            plot_multiple_scenarios(scenario_data, show=True)
            
    except Exception as e:
        print(f"Warning: Could not generate visualizations: {e}")
    
    print("\n" + "=" * 60)
    print("Analysis Complete")
    print("=" * 60)


if __name__ == '__main__':
    main()

