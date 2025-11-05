from ..optimization.rec_baseline import build_and_solve
from ..optimization.modifications import apply_modifications
from ..utils.debug import debug_data
import numpy as np

class OptimizerAgent:
    def run(self, ops_bundle, solver='pulp'):
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
        
        apply_modifications(data, ops_bundle.get('ops', []))
        
        debug_data("OptimizerAgent", "MODIFIED DATA", {
            'Load': data['Load'].tolist() if isinstance(data['Load'], np.ndarray) else data['Load'],
            'PV': data['PV'].tolist() if isinstance(data['PV'], np.ndarray) else data['PV']
        })
        
        res = build_and_solve(data, solver=solver)
        debug_data("OptimizerAgent", "OPTIMIZATION RESULT", res)
        
        return data, res
    def _default(self):
        import numpy as np
        H=24
        return {'H':H,'Load':np.array([2.0]*H),'PV':np.array([0,0,0,0,0.2,0.5,1,1.5,2,2.2,2,1.5,1,0.8,0.5,0.2,0,0,0,0,0,0,0,0]),'price_import':0.25,'price_export':0.10,'battery_capacity_kwh':5.0,'battery_eff':0.95,'battery_pmax':2.0,'init_soc':0.5,'Pimp':None,'Pexp':None}
