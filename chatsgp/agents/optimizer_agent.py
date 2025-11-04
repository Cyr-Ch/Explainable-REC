from ..optimization.rec_baseline import build_and_solve
from ..optimization.modifications import apply_modifications
class OptimizerAgent:
    def run(self, ops_bundle, solver='pulp'):
        data=self._default(); apply_modifications(data, ops_bundle.get('ops',[])); res=build_and_solve(data, solver=solver); return data,res
    def _default(self):
        import numpy as np
        H=24
        return {'H':H,'Load':np.array([2.0]*H),'PV':np.array([0,0,0,0,0.2,0.5,1,1.5,2,2.2,2,1.5,1,0.8,0.5,0.2,0,0,0,0,0,0,0,0]),'price_import':0.25,'price_export':0.10,'battery_capacity_kwh':5.0,'battery_eff':0.95,'battery_pmax':2.0,'init_soc':0.5,'Pimp':None,'Pexp':None}
