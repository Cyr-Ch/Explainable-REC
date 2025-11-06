"""
Batch evaluation script

Runs the pipeline on multiple questions from a file.
Run with: python scripts/pipelines/batch_evaluation/run_batch.py --input questions.jsonl --output results.jsonl
"""

import argparse
import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from chatsgp.agents.coder_agent import CoderAgent
from chatsgp.agents.optimizer_agent import OptimizerAgent
from chatsgp.agents.interpreter_agent import InterpreterAgent
from chatsgp.agents.orchestrator import Orchestrator
from chatsgp.utils.llm_backend import LLM
from chatsgp.config import get_config


def load_icl(path='chatsgp/icl/examples.jsonl'):
    """Load ICL examples"""
    p = Path(path)
    ex = []
    if p.exists():
        for line in p.read_text(encoding='utf-8').splitlines():
            if line.strip():
                ex.append(json.loads(line))
    return ex


def main():
    parser = argparse.ArgumentParser(description='Run batch evaluation on questions')
    parser.add_argument('--input', required=True, help='Input JSONL file with questions')
    parser.add_argument('--output', required=True, help='Output JSONL file for results')
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--solver', default='pulp', choices=['pulp', 'gurobi'], help='Solver to use')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    args = parser.parse_args()
    
    # Load configuration
    config = get_config(args.config) if args.config else get_config()
    
    # Initialize agents
    icl_examples = load_icl()
    llm = LLM()
    coder = CoderAgent(icl_examples, llm=llm)
    optimizer = OptimizerAgent(config=config)
    interpreter = InterpreterAgent()
    orchestrator = Orchestrator(coder, optimizer, interpreter)
    
    # Load questions
    questions = []
    with open(args.input, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                questions.append(json.loads(line))
    
    print(f"Processing {len(questions)} questions...")
    
    # Process questions
    results = []
    for i, item in enumerate(questions, 1):
        question = item.get('question', '')
        print(f"\n[{i}/{len(questions)}] Processing: {question}")
        
        try:
            result = orchestrator.run_question(question, solver=args.solver)
            results.append({
                'question': question,
                'result': result,
                'status': 'success'
            })
            print(f"  ✓ Success - Cost: EUR {result['result']['objective']:.2f}")
        except Exception as e:
            print(f"  ✗ Error: {e}")
            results.append({
                'question': question,
                'error': str(e),
                'status': 'error'
            })
    
    # Save results
    with open(args.output, 'w', encoding='utf-8') as f:
        for result in results:
            f.write(json.dumps(result) + '\n')
    
    # Summary
    success_count = sum(1 for r in results if r['status'] == 'success')
    print(f"\n{'='*60}")
    print(f"Summary: {success_count}/{len(results)} successful")
    print(f"Results saved to: {args.output}")


if __name__ == '__main__':
    main()

