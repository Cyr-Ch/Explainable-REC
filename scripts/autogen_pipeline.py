import argparse, json
from chatsgp.agents.coder_agent import CoderAgent
from chatsgp.agents.optimizer_agent import OptimizerAgent
from chatsgp.agents.interpreter_agent import InterpreterAgent
from chatsgp.agents.autogen_orchestrator import AutoGenOrchestrator
from chatsgp.utils.llm_backend import LLM

def load_icl(path='chatsgp/icl/examples.jsonl'):
    import pathlib
    p=pathlib.Path(path); ex=[]
    if p.exists():
        for line in p.read_text(encoding='utf-8').splitlines():
            ex.append(json.loads(line))
    return ex

if __name__=='__main__':
    import os
    ap=argparse.ArgumentParser()
    ap.add_argument('--question', required=True)
    ap.add_argument('--solver', default='pulp')
    ap.add_argument('--debug', action='store_true', help='Enable debug output showing prompts and responses')
    args=ap.parse_args()
    
    # Set debug environment variable
    if args.debug:
        os.environ['DEBUG'] = 'true'
    
    orch=AutoGenOrchestrator(CoderAgent(load_icl(), llm=LLM()), OptimizerAgent(), InterpreterAgent(), llm=LLM())
    out=orch.run_question(args.question, solver=args.solver)
    print(json.dumps(out, indent=2, ensure_ascii=False))
