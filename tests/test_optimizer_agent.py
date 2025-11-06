"""Unit tests for OptimizerAgent"""
import pytest
import numpy as np
from chatsgp.agents.optimizer_agent import OptimizerAgent


class TestOptimizerAgent:
    """Test suite for OptimizerAgent"""
    
    def test_default_data_structure(self):
        """Test that default data has correct structure"""
        agent = OptimizerAgent()
        data = agent._default()
        
        assert 'H' in data
        assert 'Load' in data
        assert 'PV' in data
        assert 'price_import' in data
        assert 'price_export' in data
        assert 'battery_capacity_kwh' in data
        assert 'battery_eff' in data
        assert 'battery_pmax' in data
        assert 'init_soc' in data
        
        assert data['H'] == 24
        assert len(data['Load']) == 24
        assert len(data['PV']) == 24
        assert isinstance(data['Load'], np.ndarray)
        assert isinstance(data['PV'], np.ndarray)
    
    def test_optimization_baseline(self):
        """Test optimization with no modifications (baseline)"""
        agent = OptimizerAgent()
        ops_bundle = {'ops': []}
        data, result = agent.run(ops_bundle, solver='pulp')
        
        assert 'status' in result
        assert 'objective' in result
        assert result['status'] == 'optimal'
        assert isinstance(result['objective'], (int, float))
        assert result['objective'] >= 0
    
    def test_optimization_with_pv_increase(self):
        """Test optimization with PV generation increase"""
        agent = OptimizerAgent()
        ops_bundle = {
            'ops': [{'op': 'scale_series', 'target': 'PV', 'scale_pct': 20.0}]
        }
        data, result = agent.run(ops_bundle, solver='pulp')
        
        assert result['status'] == 'optimal'
        assert isinstance(result['objective'], (int, float))
        # PV increased, so cost should generally decrease
        # (but we don't assert exact value as it depends on optimization)
    
    def test_optimization_with_load_shift(self):
        """Test optimization with load shifting"""
        agent = OptimizerAgent()
        ops_bundle = {
            'ops': [{'op': 'shift_load', 'percentage': 25.0, 'from_hour': 13, 'to_hour': 14}]
        }
        data, result = agent.run(ops_bundle, solver='pulp')
        
        assert result['status'] == 'optimal'
        assert isinstance(result['objective'], (int, float))
    
    def test_data_modification_applied(self):
        """Test that modifications are applied to data"""
        agent = OptimizerAgent()
        initial_data = agent._default()
        initial_pv_sum = np.sum(initial_data['PV'])
        
        ops_bundle = {
            'ops': [{'op': 'scale_series', 'target': 'PV', 'scale_pct': 20.0}]
        }
        data, result = agent.run(ops_bundle, solver='pulp')
        
        modified_pv_sum = np.sum(data['PV'])
        # PV should be 20% higher
        assert abs(modified_pv_sum - initial_pv_sum * 1.2) < 0.01

