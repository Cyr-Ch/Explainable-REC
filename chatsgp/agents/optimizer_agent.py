from ..optimization.rec_baseline import build_and_solve
from ..optimization.modifications import apply_modifications
from ..utils.debug import debug_data
from ..config import get_config
import numpy as np

class OptimizerAgent:
    def __init__(self, config=None):
        """
        Initialize OptimizerAgent
        
        Args:
            config: Optional Config object. If None, uses global config.
        """
        self.config = config if config is not None else get_config()
    
    def run(self, ops_bundle, solver='pulp'):
        """
        Run optimization with given operations
        
        Args:
            ops_bundle: Dictionary with 'ops' key containing list of operations
            solver: Solver to use ('pulp' or 'gurobi')
        
        Returns:
            Tuple of (data, result) where data is the optimization data and result is the optimization result
        
        Raises:
            ValueError: If ops_bundle is invalid
        """
        if not isinstance(ops_bundle, dict):
            raise ValueError(f"ops_bundle must be a dict, got {type(ops_bundle)}")
        
        if 'ops' not in ops_bundle:
            ops_bundle = {'ops': ops_bundle.get('ops', [])}
        
        debug_data("OptimizerAgent", "INPUT OPERATIONS", ops_bundle)
        
        data = self._default()
        debug_data("OptimizerAgent", "INITIAL DATA", {
            'H': data['H'],
            'Load': data['Load'].tolist() if isinstance(data['Load'], np.ndarray) else data['Load'],
            'PV': data['PV'].tolist() if isinstance(data['PV'], np.ndarray) else data['PV'],
            'price_import': data['price_import'],
            'price_export': data['price_export'],
            'battery_capacity_kwh': data['battery_capacity_kwh'],
            'battery_eff': data['battery_eff'],
            'battery_pmax': data['battery_pmax'],
            'init_soc': data['init_soc']
        })
        
        try:
            apply_modifications(data, ops_bundle.get('ops', []))
        except Exception as e:
            raise ValueError(f"Failed to apply modifications: {e}")
        
        debug_data("OptimizerAgent", "MODIFIED DATA", {
            'Load': data['Load'].tolist() if isinstance(data['Load'], np.ndarray) else data['Load'],
            'PV': data['PV'].tolist() if isinstance(data['PV'], np.ndarray) else data['PV']
        })
        
        res = build_and_solve(data, solver=solver)
        debug_data("OptimizerAgent", "OPTIMIZATION RESULT", res)
        
        if res.get('status') == 'error':
            raise RuntimeError(f"Optimization error: {res.get('error', 'Unknown error')}")
        
        return data, res
    
    def _default(self):
        """Get default optimization data, using config if available"""
        import numpy as np
        
        # Get config values or use defaults
        battery_config = self.config.get_battery_config()
        price_config = self.config.get_price_config()
        opt_config = self.config.get_optimization_config()
        
        H = opt_config.get('hours', 24)
        
        # Get PV and Load profiles from config or use defaults
        pv_profile = self.config.get('pv_profile')
        load_profile = self.config.get('load_profile')
        
        if pv_profile is None:
            pv_profile = np.array([0,0,0,0,0.2,0.5,1,1.5,2,2.2,2,1.5,1,0.8,0.5,0.2,0,0,0,0,0,0,0,0])
        else:
            pv_profile = np.array(pv_profile)
        
        if load_profile is None:
            load_profile = np.array([2.0]*H)
        else:
            load_profile = np.array(load_profile)
        
        return {
            'H': H,
            'Load': load_profile,
            'PV': pv_profile,
            'price_import': price_config.get('import', 0.25),
            'price_export': price_config.get('export', 0.10),
            'battery_capacity_kwh': battery_config.get('capacity_kwh', 5.0),
            'battery_eff': battery_config.get('efficiency', 0.95),
            'battery_pmax': battery_config.get('max_power', 2.0),
            'init_soc': battery_config.get('initial_soc', 0.5),
            'Pimp': None,
            'Pexp': None
        }
