"""
Residential Energy Community Scenario

This scenario models a residential energy community with:
- Smaller battery capacity (3 kWh)
- Typical residential PV and load profiles
- Standard residential energy prices

Use case: Analyzing energy optimization for a residential home with solar panels.
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


def create_residential_config():
    """Create configuration for residential energy community"""
    # Residential PV profile (peak during midday)
    pv_profile = np.array([
        0, 0, 0, 0, 0, 0.1, 0.3, 0.6, 1.0, 1.5, 2.0, 2.2, 2.0, 1.8, 1.5, 1.0, 0.5, 0.2, 0, 0, 0, 0, 0, 0
    ])
    
    # Residential load profile (higher in morning and evening)
    load_profile = np.array([
        1.5, 1.2, 1.0, 1.0, 1.2, 1.5, 2.0, 2.5, 1.8, 1.5, 1.5, 1.5,
        1.5, 1.5, 1.5, 1.8, 2.2, 2.5, 2.8, 2.5, 2.2, 2.0, 1.8, 1.5
    ])
    
    config_dict = {
        'battery': {
            'capacity_kwh': 3.0,  # Smaller residential battery
            'efficiency': 0.95,
            'max_power': 1.5,  # Lower power for residential
            'initial_soc': 0.5
        },
        'prices': {
            'import': 0.28,  # Slightly higher residential rates
            'export': 0.12   # Feed-in tariff
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
    """Run residential energy community scenario"""
    print("=" * 60)
    print("Residential Energy Community Scenario")
    print("=" * 60)
    print("\nConfiguration:")
    print("  Battery Capacity: 3.0 kWh")
    print("  Battery Power: 1.5 kW")
    print("  Import Price: EUR 0.28/kWh")
    print("  Export Price: EUR 0.12/kWh")
    print("  Profile: Residential PV and Load patterns")
    
    # Create configuration
    config = create_residential_config()
    
    # Initialize agents
    icl_examples = load_icl()
    llm = LLM()
    coder = CoderAgent(icl_examples, llm=llm)
    optimizer = OptimizerAgent(config=config)
    interpreter = InterpreterAgent()
    orchestrator = Orchestrator(coder, optimizer, interpreter)
    
    # Example questions for residential scenario
    questions = [
        "What happens if PV generation increases by 30%?",
        "What happens if we shift 20% of evening load to midday?",
        "What happens if import prices increase by 15%?",
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

