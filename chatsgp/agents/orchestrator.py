from .coder_agent import CoderAgent
from .optimizer_agent import OptimizerAgent
from .interpreter_agent import InterpreterAgent
class Orchestrator:
    def __init__(self, coder, optimizer, interpreter): self.coder=coder; self.optimizer=optimizer; self.interpreter=interpreter
    def run_question(self, q, solver='pulp'):
        ops=self.coder.propose_modifications(q); data,res=self.optimizer.run(ops, solver=solver); ans=self.interpreter.interpret(data,res); return {'ops':ops,'result':res,'answer':ans}
