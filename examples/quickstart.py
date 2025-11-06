"""
Quick Start Example for Chat-SGP

This script demonstrates basic usage of the Chat-SGP system.
Shows how to use the system with and without configuration files.
"""

from chatsgp.agents.coder_agent import CoderAgent
from chatsgp.agents.optimizer_agent import OptimizerAgent
from chatsgp.agents.interpreter_agent import InterpreterAgent
from chatsgp.agents.orchestrator import Orchestrator
from chatsgp.utils.llm_backend import LLM
from chatsgp.config import get_config
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


def example_basic_usage():
    """Example 1: Basic usage without configuration"""
    print("\n" + "=" * 60)
    print("Example 1: Basic Usage (Default Configuration)")
    print("=" * 60)
    
    # Initialize agents with defaults
    icl_examples = load_icl()
    coder = CoderAgent(icl_examples, llm=LLM())
    optimizer = OptimizerAgent()  # Uses default config
    interpreter = InterpreterAgent()
    
    orchestrator = Orchestrator(coder, optimizer, interpreter)
    
    question = "What happens if PV generation increases by 20%?"
    print(f"\nQuestion: {question}")
    
    try:
        result = orchestrator.run_question(question, solver='pulp')
        print(f"\n[OK] Status: {result['result']['status']}")
        print(f"[OK] Objective: EUR {result['result']['objective']:.2f}")
        print(f"[OK] Method: {result['ops']['explanation']}")
        print(f"\nAnswer:\n{result['answer']}")
    except Exception as e:
        print(f"[ERROR] Error: {e}")


def example_with_config():
    """Example 2: Using configuration file"""
    print("\n" + "=" * 60)
    print("Example 2: Using Configuration File")
    print("=" * 60)
    
    # Load configuration
    config = get_config()
    
    print("\nConfiguration loaded:")
    print(f"  Battery Capacity: {config.get('battery.capacity_kwh')} kWh")
    print(f"  Import Price: EUR {config.get('prices.import')}/kWh")
    print(f"  Export Price: EUR {config.get('prices.export')}/kWh")
    print(f"  Default Solver: {config.get('optimization.default_solver')}")
    
    # Initialize agents with config
    icl_examples = load_icl()
    coder = CoderAgent(icl_examples, llm=LLM())
    optimizer = OptimizerAgent(config=config)  # Use config
    interpreter = InterpreterAgent()
    
    orchestrator = Orchestrator(coder, optimizer, interpreter)
    
    question = "What happens if imports increase by 10%?"
    print(f"\nQuestion: {question}")
    
    try:
        result = orchestrator.run_question(question, solver='pulp')
        print(f"\n[OK] Status: {result['result']['status']}")
        print(f"[OK] Objective: EUR {result['result']['objective']:.2f}")
        print(f"\nAnswer:\n{result['answer']}")
    except Exception as e:
        print(f"[ERROR] Error: {e}")


def example_multiple_questions():
    """Example 3: Processing multiple questions"""
    print("\n" + "=" * 60)
    print("Example 3: Processing Multiple Questions")
    print("=" * 60)
    
    icl_examples = load_icl()
    coder = CoderAgent(icl_examples, llm=LLM())
    optimizer = OptimizerAgent()
    interpreter = InterpreterAgent()
    orchestrator = Orchestrator(coder, optimizer, interpreter)
    
    questions = [
        "What happens if PV generation increases by 20%?",
        "What happens if imports increase by 10%?",
        "What if we shift 25% of load from hour 13 to hour 14?",
    ]
    
    print("\nProcessing questions...")
    for i, question in enumerate(questions, 1):
        print(f"\n--- Question {i} ---")
        print(f"Q: {question}")
        
        try:
            result = orchestrator.run_question(question, solver='pulp')
            print(f"[OK] Cost: EUR {result['result']['objective']:.2f}")
            print(f"[OK] Answer: {result['answer'][:100]}...")
        except Exception as e:
            print(f"[ERROR] Error: {e}")


def main():
    """Run all examples"""
    print("=" * 60)
    print("Chat-SGP Quick Start Examples")
    print("=" * 60)
    print("\nThis script demonstrates:")
    print("  1. Basic usage with default configuration")
    print("  2. Using configuration files")
    print("  3. Processing multiple questions")
    
    # Run examples
    example_basic_usage()
    example_with_config()
    example_multiple_questions()
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)
    print("\nNext steps:")
    print("  - Create config.yaml to customize system parameters")
    print("  - Try different questions")
    print("  - Use --debug flag to see detailed processing")
    print("  - See README.md for more information")


if __name__ == '__main__':
    main()

