"""
Example: Using Configuration File

This example shows how to use Chat-SGP with a custom configuration file.
"""

from chatsgp.agents.coder_agent import CoderAgent
from chatsgp.agents.optimizer_agent import OptimizerAgent
from chatsgp.agents.interpreter_agent import InterpreterAgent
from chatsgp.agents.orchestrator import Orchestrator
from chatsgp.utils.llm_backend import LLM
from chatsgp.config import Config
import json


def load_icl(path='chatsgp/icl/examples.jsonl'):
    """Load ICL examples"""
    import pathlib
    p = pathlib.Path(path)
    ex = []
    if p.exists():
        for line in p.read_text(encoding='utf-8').splitlines():
            ex.append(json.loads(line))
    return ex


def main():
    """Example using custom configuration"""
    print("Chat-SGP Example: Using Configuration File")
    print("=" * 60)
    
    # Load configuration from file (if config.yaml exists)
    # Otherwise uses defaults
    config = Config()
    
    print("\nCurrent Configuration:")
    print(f"  Battery Capacity: {config.get('battery.capacity_kwh')} kWh")
    print(f"  Battery Efficiency: {config.get('battery.efficiency')}")
    print(f"  Max Power: {config.get('battery.max_power')} kW")
    print(f"  Import Price: EUR {config.get('prices.import')}/kWh")
    print(f"  Export Price: EUR {config.get('prices.export')}/kWh")
    print(f"  LLM Model: {config.get('llm.model')}")
    
    # Initialize agents with config
    icl_examples = load_icl()
    coder = CoderAgent(icl_examples, llm=LLM())
    optimizer = OptimizerAgent(config=config)  # Pass config
    interpreter = InterpreterAgent()
    
    orchestrator = Orchestrator(coder, optimizer, interpreter)
    
    # Run a question
    question = "What happens if PV generation increases by 20%?"
    print(f"\nQuestion: {question}")
    print("\nRunning optimization...")
    
    try:
        result = orchestrator.run_question(question, solver='pulp')
        
        print("\n" + "-" * 60)
        print("Results:")
        print("-" * 60)
        print(f"Status: {result['result']['status']}")
        print(f"Total Cost: EUR {result['result']['objective']:.2f}")
        print(f"Method: {result['ops']['explanation']}")
        print(f"\nInterpretation:\n{result['answer']}")
        
    except ValueError as e:
        print(f"\n[ERROR] Validation Error: {e}")
    except RuntimeError as e:
        print(f"\n[ERROR] Runtime Error: {e}")
    except Exception as e:
        print(f"\n[ERROR] Unexpected Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()

