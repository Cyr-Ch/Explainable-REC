#Save To CSV########################################################## SAVE RESULTS TO CSV FILE ##########################
###Prosumer data###

def save_results_Prosumers(Pprod,Pcons,Soe,Bcharge,Bdischarge, n = 9, m = 24):
    k=0 
    #Pprod, Pcons, n, m = InputParameters( n1 = 8 , filename= "aggregatedData.csv", n=250, m=12) #the input csv file contains data about 250 prosumers for 12 tiesteps. we use n1 prosumers for m timesteps
    #obj,imp,exp,Soe,Bcharge,Bdischarge = solveZeroKnowledge(m,n, capacity, Dt, Kch, Kdis, UB_x,UB_y,PriceImp, PriceEx,SoEmin, SoEmax, Bch_prev, Bdis_prev, SoEprev,Pprod, Pcons, obj_fct='min_cost')



    Timestep = [None] *n*m
    Prosumer = [None] *n*m
    for i in range(0,m):
        k+= 1
        p=1
        for j in range(i*n, (i+1)*n):
            Timestep[j] = k
            Prosumer[j] = p
            p+= 1

    Production = (np.reshape(Pprod, (1,n*m)))[0] #reshape? 
    Consumption = (np.reshape(Pcons , (1,n*m)))[0]
    SurplusDeficit = Pprod - Pcons
    SurplusOrDeficit = (np.reshape(SurplusDeficit,(1,n*m) ))[0]
    StateOfEnergy = (np.reshape(Soe, (1,n*m)))[0]
    Charge_Battery = (np.reshape(Bcharge, (1,n*m)))[0]
    Discharge_Battery = (np.reshape(Bdischarge, (1,n*m)))[0]

    #Charge_Battery = Bch.get()
    #Discharge_Battery = Bdis.get()
    df = pandas.DataFrame(data={"Timestep": Timestep, "Prosumer": Prosumer, "Production": Production, "Consumption": Consumption, "SurplusOrDeficit": SurplusOrDeficit,
                                "StateOfEnergy": StateOfEnergy, "Charge_Battery": Charge_Battery, "Discharge_Battery": Discharge_Battery})
    df.to_csv("/home/jovyan/work/SeptemberFinal/results_Model_1/InitB0_ModelPerfect_Prosumers_City_Learn_.csv", sep=',',index=False)



def save_results_MG(Pprod,Pcons,Soe,Bcharge,Bdischarge,imp,exp,PriceImp=0.13,PriceEx=0.10, n = 9, m = 24):
### Microgrid data ###
    #m= 24
    Timesteps = [None] *m
    MGprod = [None] *m
    MGpcons = [None] *m
    MG_SurplusOrDeficit = [None] *m
    MGexport = [None] *m
    MGimport = [None] *m
    MGcharge = [None] *m
    MGdischarge = [None] *m
    MGsoe = [None] *m
    MGcost_profit = [None] *m
    s = 0
    for i in range(0,m):
        s+=1
        Timesteps[i] = s
        MGprod[i] = Pprod[i].sum() #Total MG production for every timestep
        MGpcons[i] = Pcons[i].sum() #Total MG consumption for every timestep
        MG_SurplusOrDeficit[i] = MGprod[i] - MGpcons[i] #MG surplus or deficit for every time step
        MGimport[i] = imp[i] #Total MG import for every timestep
        MGexport[i] = exp[i] #Total MG export for every timestep
        MGcharge[i] = Bcharge[i].sum() #Total MG Battery charge for every timestep
        MGdischarge[i] = Bdischarge[i].sum() #Total MG Battery discharge for every timestep
        MGsoe[i] = Soe[i].sum() #Total MG Battery SOE for every timestep
        MGcost_profit[i] = PriceImp*MGimport[i] - PriceEx *MGexport[i]
        #Add total cost/profit

    df = pandas.DataFrame(data={"Timestep": Timesteps,  "MG_Production": MGprod, "MG_Consumption": MGpcons, "MG_SurplusOrDeficit": MG_SurplusOrDeficit,
                                "MG_Export": MGexport, "MG_import": MGimport, 
                                 "MG_Charge_Battery": MGcharge, "MG_Discharge_Battery": MGdischarge, "MG_StateOfEnergy": MGsoe,
                                 "MGcost_profit": MGcost_profit})
    df.to_csv("/home/jovyan/work/SeptemberFinal/results_Model_1/InitB0_Model_Perfect_MG_Results_City_learn_.csv", sep=',',index=False)