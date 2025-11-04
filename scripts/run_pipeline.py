import argparse, json
from chatsgp.agents.coder_agent import CoderAgent
from chatsgp.agents.optimizer_agent import OptimizerAgent
from chatsgp.agents.interpreter_agent import InterpreterAgent
from chatsgp.agents.orchestrator import Orchestrator

def load_icl(path='chatsgp/icl/examples.jsonl'):
    import pathlib
    p=pathlib.Path(path); ex=[]
    if p.exists():
        for line in p.read_text(encoding='utf-8').splitlines():
            ex.append(json.loads(line))
    return ex

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--question', required=True); ap.add_argument('--solver', default='pulp'); args=ap.parse_args()
    o=Orchestrator(CoderAgent(load_icl()), OptimizerAgent(), InterpreterAgent())
    out=o.run_question(args.question, solver=args.solver)
    print(json.dumps(out, indent=2))
