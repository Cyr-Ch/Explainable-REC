import gurobipy as gp
from gurobipy import GRB
import numpy as np

# Define all parameters
m = 3  # 5 timesteps
n = 4  # 6 prosumers
Pprod = np.array([[65, 45, 36, 25],
                  [60, 40, 30, 27],
                  [69, 44, 31, 26]])

Pcons = np.array([[10, 30, 20, 25],
                  [13, 24, 20, 25],
                  [25, 26, 20, 25]])

PriceEx = 0.10  # Price of exported power from the paper euro
PriceImp = 0.13  # Price of imported power from the paper

Dt = 3 * 60  # 300 seconds m*60s, timeslots*60s

SoEmin = [1800] * m  # minimum of SoE (Energy ws)
SoEmax = [4800] * m  # maximum of SoE  (Energy ws)

Bch_prev = [0, 0, 0, 0]  # Power(w) initialize Battery charge level to zero
Bdis_prev = [0, 0, 0, 0]  # Power(w) initialize battery discharge level to zero

SoEprev = np.array([2800, 3400, 2500, 3200])  # i(Energy ws) initialize SoE to previous timestep values

capacity = 6000  # maximum capacity of the battery (Energy ws)

Kch = (0.8 * capacity) / Dt  # 40% charging limit Energy/time > Power
Kdis = (0.8 * capacity) / Dt  # 40% discharging limit Energy/time => Power

# upper and lower bounds
UB_x = 10000000  # maximum import
UB_y = 10000000  # maximum export

# Create a model object
model = gp.Model('model')

# OPTIGUIDE *** CODE GOES HERE
# OPTIGUIDE DATA CODE GOES HERE

# Create variables
# decision variables
Pimp = model.addVars(m, name="Pimp")  # Imported Power
Pexp = model.addVars(m, name="Pexp")  # Exported Power
Bch = model.addVars(m, n, name="Bch")  # Charge the battery
Bdis = model.addVars(m, n, name="Bdis")  # Discharge the battery
SoE = model.addVars(m, n, name="SoE")  # State of Energy (of the battery)
b = model.addVars(m, vtype=GRB.BINARY, name="b")  # binary variable
c = model.addVars(m, n, vtype=GRB.BINARY, name="c")  # binary variable
SoEnext = model.addVars(m, n, name="SoEnext")  # State of Energy of the battery in the next time timeslot

# Define the objective function
model.setObjective((PriceImp * Pimp.sum() - PriceEx * Pexp.sum()), GRB.MINIMIZE)

# Constraints

# 1. Energy balance constraint
for t in range(m):
    model.addConstr(
        gp.quicksum(Pprod[t, i] for i in range(n)) - Bch.sum(t, '*') + Bdis.sum(t, '*') + Pimp[t] - Pexp[t] ==
        np.sum(Pcons[t]))

# 2. No import and export at the same time constraint
for t in range(m):
    model.addConstr(Pimp[t] <= (1 - b[t]) * UB_x)
    model.addConstr(Pexp[t] <= b[t] * UB_y)
    model.addConstr(Pimp[t] >= 0)
    model.addConstr(Pexp[t] >= 0)

# ESS constraints, i.e., battery constraints
model.addConstrs(SoE[0, i] == SoEprev[i] for i in range(n))  # initialize the state of Energy of the battery
model.addConstrs(SoEnext[t, i] == SoE[t, i] + (Bch[t, i] - Bdis[t, i]) * Dt for t in range(m) for i in range(n))
model.addConstrs(SoE[t, i] == SoEnext[t - 1, i] for t in range(1, m - 1) for i in range(n))
model.addConstrs(SoE[m - 1, i] == SoEnext[m - 2, i] for i in range(n))

model.addConstrs(SoEnext[t, i] <= SoEmax[t] for t in range(m) for i in range(n))
model.addConstrs(SoEnext[t, i] >= SoEmin[t] for t in range(m) for i in range(n))

model.addConstrs(Bch[t, i] >= 0 for t in range(m) for i in range(n))
model.addConstrs(Bch[t, i] <= Kch for t in range(m) for i in range(n))

model.addConstrs(Bdis[t, i] >= 0 for t in range(m) for i in range(n))
model.addConstrs(Bdis[t, i] <= Kdis for t in range(m) for i in range(n))

model.addConstrs(Bch[t, i] <= (1 - c[t, i]) * 100000 for t in range(m) for i in range(n))
model.addConstrs(Bdis[t, i] <= c[t, i] * 100000 for t in range(m) for i in range(n))

model.addConstr(Pimp[2] == Pimp[2-1]*(100-97)/100) 
model.addConstrs(Pimp[i] <= Pimp[2] for i in range(2+1, len(Pimp)))


# Solve the problem using Gurobi solver
print('SOLVING')
model.optimize()

'''
# Get the results
Pimport = np.array([Pimp[t] for t in range(m)])
Pexport = np.array([Pexp[t] for t in range(m)])
Bcharge = np.array([[Bch[t, i] for i in range(n)] for t in range(m)])
Bdischarge = np.array([[Bdis[t, i]for i in range(n)] for t in range(m)])
Soe = np.array([[SoE[t, i] for i in range(n)] for t in range(m)])
soenext = np.array([[SoEnext[t, i] for i in range(n)] for t in range(m)])

# Print results
print("PV Production", Pprod)
print("Load", Pcons)
print("############")
#print("Objective value:", obj_value)
print("Import:", Pimport)
print("Export:", Pexport)
print("Charge Battery:", Bcharge)
print("Discharge Battery:", Bdischarge)
print("SoE:", Soe)
print("SoEnext:", soenext)
'''

m = model
