from rsome import ro                # import the ro modeling tool
import numpy as np

###DEFINE ALL PARAMETERS
m= 3 #5 timesteps
n= 4 #6 prosumers
Pprod = np.array([[65,45,36,25],
                      [60, 40,30,27],
                       [69,44,31,26]]
                      )
Pcons = np.array([[10,30,20,25],
                       [13,24,20,25],
                      [25,26,20,25]
                       ])

PriceEx = 0.10 #Price of exported power from the paper euro
PriceImp = 0.13 #Price of imported power from the paper

Dt = 3*60 #300 seconds m*60s , timeslots*60s

SoEmin = [1800]*m #minimum of SoE (Energy ws)
SoEmax= [4800]*m #maximum of SoE  (Energy ws)

#SoEmin = [1800, 1800, 1800] #minimum of SoE (Energy ws)
#SoEmax= [4800, 4800, 4800] #maximum of SoE  (Energy ws)

Bch_prev = [0, 0, 0,0] #Power(w) initialize Battery charge level to zero
Bdis_prev = [0 , 0, 0,0] #Power(w) initialize battery discharge leverl to zero

SoEprev = np.array([2800, 3400, 2500, 3200]) #i(Energy ws) initialize SoE to previous timestep values

#Bch_prev = [0]*(n+1) #Power(w) initialize Battery charge level to zero
#Bdis_prev = [0]*(n+1) #Power(w) initialize battery discharge leverl to zero

#SoEprev = [2000]*(n+1) #i(Energy ws) initialize SoE to previous timestep values
capacity = 6000  #maximum capacity of the battery (Energy ws)

#Kch = (0.8*capacity)/Dt #40% charging limit  Energy/time > Power
#Kdis = (0.8*capacity)/Dt #40% discharging limit  Energy/time => Power

Kch = (0.8*capacity)/Dt #40% charging limit  Energy/time > Power
Kdis = (0.8*capacity)/Dt #40% discharging limit  Energy/time => Power

#upper and lower bounds
UB_x = 10000000 #maximum import
UB_y = 10000000 #maximum export


#create a model object
model = ro.Model('model')
#decision variables
Pimp = model.dvar(m) #Imported Power                
Pexp = model.dvar(m)    #Exported Power
Bch = model.dvar((m,n))       #Charge the battery         
Bdis = model.dvar((m,n))        #Discharge the battery
SoE = model.dvar((m,n)) #State of Energy (of the battery)
b = model.dvar(m, 'B')  #binary variable
c = model.dvar((m,n), 'B') #binary variable
SoEnext = model.dvar((m,n)) #State of Energy of the battery in the next time timeslot

#define the two objective functions/startegies
#if obj_fct == 'min_cost': #cost minimization strategy/profit maximization 
model.min((PriceImp*Pimp).sum() - (PriceEx * Pexp).sum())
#if obj_fct == 'min_exchange':
    #model.min(Pimp.sum() + Pexp.sum()) #energy exchange minimization

#Constraints
#1. Energy balance constraint
model.st(((sum(Pprod[t]) - Bch.sum(axis = 1) + Bdis.sum(axis = 1) + Pimp[t] - Pexp[t]) ==  sum(Pcons[t])) for t in range(0,m)) 

#2. No import and export at the same time constraint
model.st(Pimp[t] <= (1-b[t]) * UB_x for t in range(0,m))   #constraint (2) x <= (1-b) * UB_x  ,y <= b * UB_y
model.st(Pexp[t] <= b[t] * UB_y for t in range(0,m) )
model.st(Pimp >=0 )
model.st(Pexp >=0 )
 
#ESS constraints, i.e, battery constraints
model.st( SoE[0] == SoEprev ) #initialize the state of Energy of the battery
model.st( SoEnext[t] == SoE[t] + (Bch[t] - Bdis[t]) * Dt for t in range(0,m))
model.st( SoE[t] == SoEnext[t-1] for t in range(1,m-1))
model.st( SoE[m-1] == SoEnext[m-2])

model.st( SoEnext[t] <= SoEmax[t] for t in range(0,m)) #constraint (4)
model.st( SoEnext[t] >= SoEmin[t] for t in range(0,m) ) #constraint (4)

model.st(Bch>=0)
model.st(Bch <= Kch) #constraint (5)

model.st(Bdis>=0)
model.st(Bdis <= Kdis) #constraint (6)

#model.st(Bch[i] <= (1-c[i]) * 100000 for i in range(0,n))   #constraint (7) x <= (1-b) * UB_x  ,y <= b * UB_y
#model.st(Bdis[i] <= c[i] * 100000 for i in range(0,n))
model.st(Bch[t] <= (1-c[t]) * 100000 for t in range(0,m))
model.st(Bdis[t] <= c[t] * 100000 for t in range(0,m))
#SoEprev = SoEnext.get()

############################# SOLVING ############################
print('SOLVING')
#model.solve(grb) #solve the problem using Gurobi solver
model.solve() #solve the problem using Gurobi solver

obj_value=model.get()
Pimport=Pimp.get()
Pexport=Pexp.get()
Bcharge=Bch.get()
Bdischarge =Bdis.get()
Soe=SoE.get()
soenext=SoEnext.get()

print("PV Production", Pprod)
print("Load", Pcons)
#print(obj,imp,exp,a,e,x)
print("############")
print("objective value:",obj_value)
print("Import:",Pimport )
print("Export:",Pexport )
    
print("Charge Battery:",Bcharge )
print("Discharge Battery:",Bdischarge )
print("SoE:",Soe )
print("SoEnext:",soenext )
