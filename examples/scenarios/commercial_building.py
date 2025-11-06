"""
Commercial Building Scenario

This scenario models a commercial building with:
- Larger battery capacity (10 kWh)
- Commercial PV and load profiles (higher daytime load)
- Commercial energy prices

Use case: Analyzing energy optimization for a commercial building with solar panels.
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


def create_commercial_config():
    """Create configuration for commercial building"""
    # Commercial PV profile (larger system, peak during midday)
    pv_profile = np.array([
        0, 0, 0, 0, 0, 0.2, 0.5, 1.0, 2.0, 3.0, 4.0, 4.5, 4.0, 3.5, 3.0, 2.0, 1.0, 0.5, 0, 0, 0, 0, 0, 0
    ])
    
    # Commercial load profile (high during business hours, low at night)
    load_profile = np.array([
        1.0, 0.8, 0.8, 0.8, 1.0, 1.5, 2.5, 3.5, 4.0, 4.5, 5.0, 5.0,
        5.0, 5.0, 4.5, 4.0, 3.5, 3.0, 2.0, 1.5, 1.0, 0.8, 0.8, 0.8
    ])
    
    config_dict = {
        'battery': {
            'capacity_kwh': 10.0,  # Larger commercial battery
            'efficiency': 0.95,
            'max_power': 5.0,  # Higher power for commercial
            'initial_soc': 0.5
        },
        'prices': {
            'import': 0.22,  # Lower commercial rates
            'export': 0.08   # Lower feed-in tariff
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
    """Run commercial building scenario"""
    print("=" * 60)
    print("Commercial Building Scenario")
    print("=" * 60)
    print("\nConfiguration:")
    print("  Battery Capacity: 10.0 kWh")
    print("  Battery Power: 5.0 kW")
    print("  Import Price: EUR 0.22/kWh")
    print("  Export Price: EUR 0.08/kWh")
    print("  Profile: Commercial PV and Load patterns")
    
    # Create configuration
    config = create_commercial_config()
    
    # Initialize agents
    icl_examples = load_icl()
    llm = LLM()
    coder = CoderAgent(icl_examples, llm=llm)
    optimizer = OptimizerAgent(config=config)
    interpreter = InterpreterAgent()
    orchestrator = Orchestrator(coder, optimizer, interpreter)
    
    # Example questions for commercial scenario
    questions = [
        "What happens if PV generation increases by 25%?",
        "What happens if we shift 30% of morning load to midday?",
        "What happens if import prices decrease by 10%?",
    ]
    
    print("\n" + "=" * 60)
    print("Running Scenarios")
    print("=" * 60)
    
    results = []
    for i, question in enumerate(questions, 1):
        print(f"\n--- Scenario {i} ---")
        print(f"Question: {question}")
        
        try:
            result = orchestrator.run_question(question, solver='pulp')
            cost = result['result']['objective']
            status = result['result']['status']
            
            print(f"[OK] Status: {status}")
            print(f"[OK] Total Cost: EUR {cost:.2f}")
            print(f"\nAnswer:\n{result['answer']}")
            
            results.append({
                'question': question,
                'cost': cost,
                'status': status
            })
        except Exception as e:
            print(f"[ERROR] Error: {e}")
            results.append({
                'question': question,
                'error': str(e)
            })
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    for i, r in enumerate(results, 1):
        if 'cost' in r:
            print(f"{i}. {r['question']}: EUR {r['cost']:.2f}")
        else:
            print(f"{i}. {r['question']}: ERROR - {r.get('error', 'Unknown')}")


if __name__ == '__main__':
    main()

