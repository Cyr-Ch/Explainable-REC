import time
from gurobipy import GRB, Model

# Example data
QUALITY_THRESHOLD= 7
DEMAND = 1

material_quality = {'M1': 3, 'M2': 9, 'M3': 6} # 1: low quality, 10: extremely high quality
material_abandunce = {'M1': 8, 'M2': 3, 'M3': 5} #1: very rare, 10:extremely abandunt
material_usage = {'M1': 0.4, 'M2': 0.1, 'M3': 0.5} # sums up to 1 - represents how much is used of the material to produce a unit
material_cost = {'M1': 2, 'M2': 9, 'M3': 5} # 1: very cheap, 10:extremely expensive
demand = {'demand': DEMAND}
materials = list(set(i for i in material_quality.keys()))

# Create a new model
model = Model("material_distribution")

# OPTIGUIDE DATA CODE GOES HERE

# Create variables
# x is material distribution
x = model.addVars(material_quality.keys(),
                  vtype=GRB.CONTINUOUS,
                  name="x")


# Set objective
# production cost
# x[i] corresponds to the quantity of material needed per product
# to get the overall usage of each material for the demand we should do demand['demand'] * x[i]
model.setObjective(
    sum(x[i] * material_cost[i] for i in material_cost.keys()) 
    , GRB.MINIMIZE)

# Quantity sums up to 10 constraint
model.addConstr(sum(x[i] for i in material_cost.keys()) == 1, name='quantity constraint')
# Quality constraint
model.addConstr(
        sum(x[i]* material_quality[i] for i in material_quality.keys()) >= QUALITY_THRESHOLD, name='quality constraint')

# Add Abandunce constraint
for i in material_abandunce.keys():
    model.addConstr(
            x[i]* demand['demand'] <= material_abandunce[i], name='abandunce constraint '+str(i))


# Optimize model
model.optimize()
m = model

# OPTIGUIDE CONSTRAINT CODE GOES HERE

# Solve
model.update()
model.optimize()

print(time.ctime())
if model.status == GRB.OPTIMAL:
    print(f'Optimal cost: {model.objVal}')
    for i in material_quality.keys():
        print(f'new material {i} usage : {str(x[i])}')
else:
    print("Not solved to optimality. Optimization status:", model.status)
