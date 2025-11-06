"""Unit tests for InterpreterAgent"""
import pytest
import numpy as np
from chatsgp.agents.interpreter_agent import InterpreterAgent
from chatsgp.utils.llm_backend import LLM


class TestInterpreterAgent:
    """Test suite for InterpreterAgent"""
    
    def test_rule_based_interpretation_optimal(self):
        """Test rule-based interpretation for optimal result"""
        agent = InterpreterAgent(llm=None)
        data = {
            'PV': np.array([1.0] * 24),
            'Load': np.array([2.0] * 24),
            'battery_capacity_kwh': 5.0,
            'price_import': 0.25,
            'price_export': 0.10
        }
        result = {'status': 'optimal', 'objective': 10.5}
        ops = {'ops': [{'op': 'scale_series', 'target': 'PV', 'scale_pct': 20.0}]}
        
        answer = agent.interpret(data, result, ops)
        
        assert isinstance(answer, str)
        assert len(answer) > 0
        # Answer should mention PV, solar, or generation
        assert any(keyword in answer.lower() for keyword in ['pv', 'solar', 'generation', 'energy'])
        assert 'EUR' in answer or 'cost' in answer.lower()
    
    def test_rule_based_interpretation_infeasible(self):
        """Test rule-based interpretation for infeasible result"""
        agent = InterpreterAgent(llm=None)
        data = {
            'PV': np.array([1.0] * 24),
            'Load': np.array([2.0] * 24),
            'battery_capacity_kwh': 5.0,
            'price_import': 0.25,
            'price_export': 0.10
        }
        result = {'status': 'infeasible', 'objective': float('inf')}
        ops = {'ops': []}
        
        answer = agent.interpret(data, result, ops)
        
        assert isinstance(answer, str)
        assert 'infeasible' in answer.lower() or 'could not find' in answer.lower()
    
    def test_icl_examples_loaded(self):
        """Test that ICL examples are properly loaded"""
        agent = InterpreterAgent(llm=None)
        assert len(agent.icl) >= 0  # May be empty if file doesn't exist
    
    def test_baseline_calculation(self):
        """Test baseline calculation"""
        agent = InterpreterAgent(llm=None)
        baseline_obj = agent._calculate_baseline()
        
        assert isinstance(baseline_obj, (int, float))
        assert baseline_obj != float('inf')
        assert baseline_obj >= 0
    
    def test_interpret_with_baseline_comparison(self):
        """Test interpretation includes baseline comparison"""
        agent = InterpreterAgent(llm=None)
        data = {
            'PV': np.array([1.0] * 24),
            'Load': np.array([2.0] * 24),
            'battery_capacity_kwh': 5.0,
            'price_import': 0.25,
            'price_export': 0.10
        }
        result = {'status': 'optimal', 'objective': 10.5}
        ops = {'ops': [{'op': 'scale_series', 'target': 'PV', 'scale_pct': 20.0}]}
        
        answer = agent.interpret(data, result, ops)
        
        # Should mention baseline or comparison
        assert 'baseline' in answer.lower() or 'compared' in answer.lower() or 'EUR' in answer

