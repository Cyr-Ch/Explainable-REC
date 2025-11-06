"""
Benchmark runner for Chat-SGP

Provides functions to run benchmarks and evaluate performance.
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from .metrics import generate_evaluation_report


def load_benchmark_questions(file_path: str) -> List[Dict[str, Any]]:
    """
    Load benchmark questions from a JSONL file.
    
    Args:
        file_path: Path to JSONL file with questions
    
    Returns:
        List of question dictionaries
    """
    questions = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                questions.append(json.loads(line))
    return questions


def run_benchmark(
    questions_file: str,
    output_file: Optional[str] = None,
    config_file: Optional[str] = None,
    solver: str = 'pulp'
) -> Dict[str, Any]:
    """
    Run a benchmark on a set of questions.
    
    Args:
        questions_file: Path to JSONL file with questions
        output_file: Optional path to save results
        config_file: Optional configuration file path
        solver: Solver to use ('pulp' or 'gurobi')
    
    Returns:
        Dictionary with benchmark results and evaluation metrics
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
    
    # Load configuration
    config = get_config(config_file) if config_file else get_config()
    
    # Initialize agents
    icl_examples = load_icl()
    llm = LLM()
    coder = CoderAgent(icl_examples, llm=llm)
    optimizer = OptimizerAgent(config=config)
    interpreter = InterpreterAgent()
    orchestrator = Orchestrator(coder, optimizer, interpreter)
    
    # Load questions
    questions = load_benchmark_questions(questions_file)
    
    # Process questions
    results = []
    for i, item in enumerate(questions, 1):
        question = item.get('question', '')
        print(f"[{i}/{len(questions)}] Processing: {question}")
        
        try:
            result = orchestrator.run_question(question, solver=solver)
            results.append({
                'question': question,
                'result': result,
                'status': 'success'
            })
        except Exception as e:
            results.append({
                'question': question,
                'error': str(e),
                'status': 'error'
            })
    
    # Generate evaluation report
    evaluation_report = generate_evaluation_report(results)
    
    # Save results if output file specified
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            for result in results:
                f.write(json.dumps(result) + '\n')
    
    return {
        'results': results,
        'evaluation': evaluation_report
    }

