from __future__ import annotations
from typing import Dict, Any

def build_and_solve(data: Dict[str, Any], solver='pulp') -> Dict[str, Any]:
    H=data['H']; Load=data['Load']; PV=data['PV']
    cap=data['battery_capacity_kwh']; eff=data['battery_eff']; pmax=data['battery_pmax']
    price_i=data['price_import']; price_e=data['price_export']; init_soc=data['init_soc']*cap
    if solver=='gurobi':
        try:
            import gurobipy as gp
            m=gp.Model('rec'); m.Params.OutputFlag=0
            Pimp=m.addVars(H, lb=0.0, name='Pimp'); Pexp=m.addVars(H, lb=0.0, name='Pexp')
            C=m.addVars(H, lb=0.0, ub=pmax, name='C'); D=m.addVars(H, lb=0.0, ub=pmax, name='D')
            SoC=m.addVars(H, lb=0.0, ub=cap, name='SoC')
            for t in range(H): m.addConstr(Load[t]==PV[t]+D[t]+Pimp[t]-C[t]-Pexp[t], name=f'balance_{t}')
            for t in range(H): m.addConstr(SoC[t]==(init_soc + (eff*C[t]-D[t]/eff) if t==0 else SoC[t-1]+eff*C[t]-D[t]/eff), name=f'soc_{t}')
            m.setObjective(gp.quicksum(price_i*Pimp[t]-price_e*Pexp[t] for t in range(H)), gp.GRB.MINIMIZE)
            m.optimize()
            if m.Status==gp.GRB.OPTIMAL: return {'status':'optimal','objective': m.ObjVal}
            if m.Status==gp.GRB.INFEASIBLE:
                try:
                    m.computeIIS(); iis=[c.ConstrName for c in m.getConstrs() if c.IISConstr]
                except Exception:
                    iis=[]
                return {'status':'infeasible','objective': float('inf'), 'diagnostics': {'IIS': iis}}
            if m.Status==gp.GRB.UNBOUNDED: return {'status':'unbounded','objective': float('inf')}
            return {'status':'other','objective': float('inf'), 'code': int(m.Status)}
        except Exception as e:
            return {'status':'error','objective': float('inf'), 'error': str(e)}
    else:
        try:
            import pulp as pl
            prob=pl.LpProblem('rec', pl.LpMinimize)
            Pimp=pl.LpVariable.dicts('Pimp', range(H), lowBound=0)
            Pexp=pl.LpVariable.dicts('Pexp', range(H), lowBound=0)
            C=pl.LpVariable.dicts('C', range(H), lowBound=0, upBound=pmax)
            D=pl.LpVariable.dicts('D', range(H), lowBound=0, upBound=pmax)
            SoC=pl.LpVariable.dicts('SoC', range(H), lowBound=0, upBound=cap)
            for t in range(H): prob += Load[t] == PV[t] + D[t] + Pimp[t] - C[t] - Pexp[t]
            for t in range(H): prob += (SoC[t] == (init_soc + (eff*C[t] - D[t]/eff) if t==0 else SoC[t-1] + eff*C[t] - D[t]/eff))
            prob += pl.lpSum(price_i*Pimp[t] - price_e*Pexp[t] for t in range(H))
            prob.solve(pl.PULP_CBC_CMD(msg=False))
            if pl.LpStatus[prob.status]=='Optimal': return {'status':'optimal','objective': pl.value(prob.objective)}
            if pl.LpStatus[prob.status]=='Infeasible': return {'status':'infeasible','objective': float('inf')}
            if pl.LpStatus[prob.status]=='Unbounded': return {'status':'unbounded','objective': float('inf')}
            return {'status':'other','objective': float('inf'), 'status_str': pl.LpStatus[prob.status]}
        except Exception as e:
            return {'status':'error','objective': float('inf'), 'error': str(e)}
