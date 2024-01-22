import numpy as np
#extract the dataframe containing the import and the export prices for m timesteps
#Customized Prices from the Nordpool
def Prices(filename= ""):

    """"
    prices = pd.read_csv('/home/amalnamm/work/SeptemberFinal/Nord_pool_prices/recalculated-nordic-system-price.csv')
    Price_imp_df = prices.iloc[408:432,0:4] #24 hours of prices from nord pool 
    #converting the dataframe to a numpy array
    Price_imp = Price_imp_df['System Price(Eur/MWh)'].to_numpy()
    l = Price_imp
    Price_exp = Price_imp
    Price_exp[0:5] = Price_imp[0:5] *2 #we want to import at night, no peak, less stress, charge vehicle or battery, 
    Price_exp[5:10] = Price_imp[5:10]/3 #prices of import start to increase due demand
    Price_exp[10:20] = Price_imp[10:20]/5 #price of import keep increasing due demand increase
    Price_exp[20:24] = Price_imp[20:24]*3 #
    Price_imp_df = prices.iloc[408:432,0:4] #24 hours of prices from nord pool 
    Price_imp = Price_imp_df['System Price(Eur/MWh)'].to_numpy()
    PriceEx =Price_exp/1000 #Price of exported power from the paper euro
    PriceImp = Price_imp/1000 #from EUR/MWh TO eur/kWh
    """
    PriceEx = np.array([0.23504   , 0.2362    , 0.23734   , 0.23424   , 0.23916   ,
       0.04096667, 0.04091667, 0.04666   , 0.06665   , 0.09820333,
       0.05998   , 0.059582  , 0.059984  , 0.059586  , 0.059986  ,
       0.059982  , 0.063818  , 0.065538  , 0.06379   , 0.061788  ,
       0.89988   , 0.89709   , 0.57639   , 0.41982   ])
    
    PriceImp = np.array([0.11752, 0.1181 , 0.11867, 0.11712, 0.11958, 0.1229 , 0.12275,
       0.13998, 0.19995, 0.29461, 0.2999 , 0.29791, 0.29992, 0.29793,
       0.29993, 0.29991, 0.31909, 0.32769, 0.31895, 0.30894, 0.29996,
       0.29903, 0.19213, 0.13994])
    
    #print(PriceEx)
    
    return PriceEx,PriceImp


#using city learn data
def InputParameters(filename, n = 9, m = 24): #9 buildings 24h
    #extract all the production and consumption values from the csv file
    #final : extracting nd.arrays for consumption and production for 24h
    
    #merged_f.to_csv('/home/jovyan/work/SeptemberFinal/City_Learn_data/Climate_Zone_1/Merged_Data.csv')
    merged_f = pd.read_csv('/Users/amalnammouchi/Documents/Research/LLMs/SGP-Chat/benchmark/application/Dataset/CityLearn/Merged_Data.csv')


    df_24h = merged_f.iloc[0:24,0:] #m=24
    d_consumption = df_24h.iloc[0:24,4:13] 
    d_production = df_24h.iloc[0:24,13:22]
    c1 = d_consumption.to_numpy()
    p1 = d_production.to_numpy()
            
    return p1,c1 #,s1


def main():
    #set the input parameters and data
    battery_capacity = np.array([140,80,50,75,50,30,40,30,35]) #maximum amount of electrical energy that the battery can store (kWh)
    #randnums = np.array([40,64,10,45,32,20,16,10,30]) #initial SoE (kWh)
    randnums = np.array([0,0,0,0,0,0,0,0,0])
    m = 24
    n =9 
    
    #Pprod, Pcons, n, m = InputParameters( n1 = 8 , filename= "aggregatedData.csv", n=250, m=12) #the input csv file contains data about 250 prosumers for 12 tiesteps. we use n1 prosumers for m timesteps
    Pprod, Pcons= InputParameters(filename= "/Users/amalnammouchi/Documents/Research/LLMs/SGP-Chat/benchmark/application/Dataset/CityLearn/Merged_Data.csv", n = 9, m=24) #the input csv file contains data about 250 prosumers for 12 tiesteps. we use n1 prosumers for m timesteps


    #PriceEx = 0.10 #Price of exported power from the paper euro
    #PriceImp = 0.13 #Price of imported power from the paper
    
    PriceEx,PriceImp= Prices()
    #Dt = 12*60  #12*60s
    Dt = 1 #24*1 #24h   A verifier avec A.T ou bien 1h


    #SoEmin = [1800]*m #minimum of SoE (Energy ws)
    #SoEmax= [4800]*m #maximum of SoE  (Energy ws)
    
    #SoEmin = np.array( [[28, 16, 10, 15, 10,  6,  8,  6,  7] for i in range(0,m)])  #minimum of SoE (Energy kWh) 20%
    SoEmin = np.array([[0,0,0,0,0,0,0,0,0] for i in range(0,m)])


    SoEmax= np.array([[112,  64,  40,  60,  40,  24,  32,  24,  28] for i in range(0,m)]) #maximum of SoE  (Energy kWh) 80%



    Bch_prev = [0, 0, 0,0,0,0,0,0,0,0] #Power(w) initialize Battery charge level to zero
    Bdis_prev = [0 , 0, 0,0,0,0,0,0,0] #Power(w) initialize battery discharge leverl to zero DO WE NEED THIS



    #SoEprev = np.array(randnums[0:n]) #i(Energy ws) initialize SoE to previous timestep values
    
    SoEprev = randnums #(Energy Kwh) initialize SoE to previous timestep values




    #capacity = 6000  #maximum capacity of the battery (Energy ws)

    #Kch = (0.8*capacity)/Dt #40% charging limit  Energy/time > Power
    #Kdis = (0.8*capacity)/Dt #40% discharging limit  Energy/time => Power
    
    Kch = np.array([[112,  64,  40,  60,  40,  24,  32,  24,  28] for i in range(0,m)])
    Kdis = np.array([[112,  64,  40,  60,  40,  24,  32,  24,  28] for i in range(0,m)])
    

    #upper and lower bounds
    UB_x = 10000000 #maximum import
    UB_y = 10000000 #maximum export
    
    
    #minimum cost strategy 
    #on n'a pas besoin de la variable capacity
    #obj_value,Pimport,Pexport,Bcharge,Bdischarge,Soe,soenext = solvePerfectKnowledge(m,n, capacity, Dt, Kch, Kdis, UB_x,UB_y,PriceImp, PriceEx,SoEmin, SoEmax, Bch_prev, Bdis_prev, SoEprev,Pprod, Pcons, obj_fct='min_cost')
    #minimum exchange strategy
    #obj_value,Pimport,Pexport,Bcharge,Bdischarge,Soe,soenext = solvePerfectKnowledge(m,n, capacity, Kch, Kdis, UB_x,UB_y,PriceImp, PriceEx,SoEmin, SoEmax, Bch_prev, Bdis_prev, SoEprev,Pprod, Pcons, obj_fct='min_exchange')
    
    
    #save_results_Prosumers(Pprod,Pcons,Soe,Bcharge,Bdischarge, n, m)
    #save_results_MG(Pprod,Pcons,Soe,Bcharge,Bdischarge,Pimport,Pexport,PriceImp,PriceEx, n, m)
    
    #return obj_value,Pimport,Pexport,Bcharge,Bdischarge,Soe,soenext

    


print("test")