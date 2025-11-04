from __future__ import annotations
import json
from typing import Optional
try:
    import autogen
    AUTOGEN_AVAILABLE=True
except Exception:
    AUTOGEN_AVAILABLE=False
from .coder_agent import CoderAgent
from .optimizer_agent import OptimizerAgent
from .interpreter_agent import InterpreterAgent
from ..utils.llm_backend import LLM

class AutoGenOrchestrator:
    def __init__(self, coder: CoderAgent, optimizer: OptimizerAgent, interpreter: InterpreterAgent, llm: Optional[LLM]=None):
        self.coder=coder; self.optimizer=optimizer; self.interpreter=interpreter; self.llm=llm
    def run_question(self, question: str, solver: str='pulp'):
        if not AUTOGEN_AVAILABLE:
            ops=self.coder.propose_modifications(question)
            data,res=self.optimizer.run(ops, solver=solver)
            ans=self.interpreter.interpret(data,res)
            return {'ops':ops,'result':res,'answer':ans,'autogen_used':False}
        llm_config={'model': getattr(self.llm,'model','gpt-4o-mini')} if self.llm else {}
        coder_agent=autogen.AssistantAgent('coder', system_message='Coder agent', llm_config=llm_config)
        optimizer_agent=autogen.AssistantAgent('optimizer', system_message='Optimizer agent', llm_config=llm_config)
        interpreter_agent=autogen.AssistantAgent('interpreter', system_message='Interpreter agent', llm_config=llm_config)
        user=autogen.UserProxyAgent('user', code_execution_config=False)
        def propose(q:str): return json.dumps(self.coder.propose_modifications(q))
        def optimize(ops_json:str, solver_name:str='pulp'):
            try: ops=json.loads(ops_json)
            except Exception: ops={'ops':[]}
            data,res=self.optimizer.run(ops, solver=solver_name)
            return json.dumps({'result':res})
        def interpret(payload:str):
            try: r=json.loads(payload).get('result',{})
            except Exception: r={}
            return self.interpreter.interpret({}, r)
        coder_agent.register_for_llm(name='propose', description='Propose ops')(propose)
        optimizer_agent.register_for_llm(name='optimize', description='Run MILP')(optimize)
        interpreter_agent.register_for_llm(name='interpret', description='Explain')(interpret)
        cr=user.initiate_chat(coder_agent, message=f'Question: {question}. Call propose().')
        orr=user.initiate_chat(optimizer_agent, message='Call optimize() with coder output.')
        ir=user.initiate_chat(interpreter_agent, message='Call interpret() with optimizer output.')
        try: ops=json.loads(cr.chat_history[-1]['content'])
        except Exception: ops={'ops':[]}
        return {'ops':ops,'result_raw': orr.chat_history[-1]['content'] if orr.chat_history else '{}','answer': ir.chat_history[-1]['content'] if ir.chat_history else 'N/A','autogen_used':True}
