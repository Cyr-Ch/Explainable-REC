"""Integration tests for the full pipeline"""
import pytest
from chatsgp.agents.coder_agent import CoderAgent
from chatsgp.agents.optimizer_agent import OptimizerAgent
from chatsgp.agents.interpreter_agent import InterpreterAgent
from chatsgp.agents.orchestrator import Orchestrator
from chatsgp.utils.llm_backend import LLM
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


class TestIntegration:
    """Integration tests for the full pipeline"""
    
    def test_full_pipeline_pv_increase(self):
        """Test full pipeline with PV increase question"""
        orchestrator = Orchestrator(
            CoderAgent(load_icl(), llm=LLM()),
            OptimizerAgent(),
            InterpreterAgent()
        )
        
        result = orchestrator.run_question(
            "What happens if PV generation increases by 20%?",
            solver='pulp'
        )
        
        assert 'ops' in result
        assert 'result' in result
        assert 'answer' in result
        
        assert 'ops' in result['ops']
        assert len(result['ops']['ops']) > 0
        assert result['ops']['ops'][0]['target'] == 'PV'
        
        assert result['result']['status'] == 'optimal'
        assert 'objective' in result['result']
        
        assert isinstance(result['answer'], str)
        assert len(result['answer']) > 0
    
    def test_full_pipeline_import_increase(self):
        """Test full pipeline with import increase question"""
        orchestrator = Orchestrator(
            CoderAgent(load_icl(), llm=LLM()),
            OptimizerAgent(),
            InterpreterAgent()
        )
        
        result = orchestrator.run_question(
            "What happens if imports increase by 10%?",
            solver='pulp'
        )
        
        assert result['result']['status'] == 'optimal'
        assert 'objective' in result['result']
        assert isinstance(result['answer'], str)
    
    def test_full_pipeline_load_shift(self):
        """Test full pipeline with load shifting question"""
        orchestrator = Orchestrator(
            CoderAgent(load_icl(), llm=LLM()),
            OptimizerAgent(),
            InterpreterAgent()
        )
        
        result = orchestrator.run_question(
            "What if we shift 25% of load from hour 13 to hour 14?",
            solver='pulp'
        )
        
        assert result['result']['status'] == 'optimal'
        assert 'objective' in result['result']
        assert isinstance(result['answer'], str)
    
    def test_pipeline_output_structure(self):
        """Test that pipeline output has correct structure"""
        orchestrator = Orchestrator(
            CoderAgent(load_icl(), llm=LLM()),
            OptimizerAgent(),
            InterpreterAgent()
        )
        
        result = orchestrator.run_question(
            "What happens if exports decrease by 15%?",
            solver='pulp'
        )
        
        # Check top-level keys
        assert 'ops' in result
        assert 'result' in result
        assert 'answer' in result
        
        # Check ops structure
        assert 'ops' in result['ops']
        assert 'explanation' in result['ops']
        
        # Check result structure
        assert 'status' in result['result']
        assert 'objective' in result['result']
        
        # Check answer is string
        assert isinstance(result['answer'], str)

