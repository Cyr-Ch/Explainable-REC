"""Unit tests for CoderAgent"""
import pytest
import json
from chatsgp.agents.coder_agent import CoderAgent
from chatsgp.utils.llm_backend import LLM


class TestCoderAgent:
    """Test suite for CoderAgent"""
    
    def test_rule_based_pv_increase(self):
        """Test rule-based parsing for PV generation increase"""
        agent = CoderAgent([], llm=None)
        result = agent.propose_modifications("What happens if PV generation increases by 20%?")
        
        assert result['explanation'] == 'rule-based'
        assert len(result['ops']) == 1
        assert result['ops'][0]['op'] == 'scale_series'
        assert result['ops'][0]['target'] == 'PV'
        assert result['ops'][0]['scale_pct'] == 20.0
    
    def test_rule_based_import_increase(self):
        """Test rule-based parsing for import increase"""
        agent = CoderAgent([], llm=None)
        result = agent.propose_modifications("What happens if imports increase by 10%?")
        
        assert result['explanation'] == 'rule-based'
        assert len(result['ops']) == 1
        assert result['ops'][0]['op'] == 'scale_series'
        assert result['ops'][0]['target'] == 'Pimp'
        assert result['ops'][0]['scale_pct'] == 10.0
    
    def test_rule_based_export_decrease(self):
        """Test rule-based parsing for export decrease"""
        agent = CoderAgent([], llm=None)
        # Note: "reduce exports by 15%" is parsed as positive 15%, 
        # the actual decrease is handled in modifications.py
        result = agent.propose_modifications("Reduce exports by 15%")
        
        assert result['explanation'] == 'rule-based'
        assert len(result['ops']) == 1
        assert result['ops'][0]['op'] == 'scale_series'
        assert result['ops'][0]['target'] == 'Pexp'
        # The parser extracts 15%, the sign is handled by context
        assert result['ops'][0]['scale_pct'] == 15.0
    
    def test_rule_based_load_shift(self):
        """Test rule-based parsing for load shifting"""
        agent = CoderAgent([], llm=None)
        result = agent.propose_modifications("What if we shift 25% of load from hour 13 to hour 14?")
        
        assert result['explanation'] == 'rule-based'
        assert len(result['ops']) == 1
        assert result['ops'][0]['op'] == 'shift_load'
        assert result['ops'][0]['percentage'] == 25.0
        assert result['ops'][0]['from_hour'] == 13
        assert result['ops'][0]['to_hour'] == 14
    
    def test_rule_based_no_percentage(self):
        """Test rule-based parsing when no percentage is found"""
        agent = CoderAgent([], llm=None)
        result = agent.propose_modifications("What is the weather?")
        
        assert result['explanation'] == 'rule-based'
        assert len(result['ops']) == 0
    
    def test_icl_examples_loaded(self):
        """Test that ICL examples are properly loaded"""
        icl_examples = [
            {'question': 'imports increase by 18%', 'ops': [{'op': 'scale_series', 'target': 'Pimp', 'scale_pct': 18}]}
        ]
        agent = CoderAgent(icl_examples, llm=None)
        assert len(agent.icl) == 1
        assert agent.icl[0]['question'] == 'imports increase by 18%'
    
    def test_llm_fallback_when_unavailable(self):
        """Test that rule-based fallback works when LLM is unavailable"""
        # Create LLM without API key by temporarily removing it
        import os
        original_key = os.environ.get('OPENAI_API_KEY')
        try:
            if 'OPENAI_API_KEY' in os.environ:
                del os.environ['OPENAI_API_KEY']
            
            # Force reload LLM without API key
            from chatsgp.utils.llm_backend import LLM
            llm = LLM()
            # Clear client if it was set
            llm.client = None
            
            agent = CoderAgent([{'question': 'test', 'ops': []}], llm=llm)
            result = agent.propose_modifications("What happens if PV increases by 20%?")
            
            # Should fall back to rule-based
            assert result['explanation'] == 'rule-based'
            assert len(result['ops']) == 1
            assert result['ops'][0]['target'] == 'PV'
        finally:
            # Restore original API key
            if original_key:
                os.environ['OPENAI_API_KEY'] = original_key

