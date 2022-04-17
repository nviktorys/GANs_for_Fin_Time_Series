################################################
#####      2.2  Data Exploration           #####
################################################

import os
import pandas as  pd
import numpy as np
import pickle5
import matplotlib.pyplot as plt
import yfinance as yf
import sys


##### Load data
###############################################
os.getcwd()
os.chdir('.\\Data')
os.getcwd()

data = []
with open('./data.pkl','rb') as file:
    data = pickle5.load(file)
data = pd.DataFrame(data)

sectors = data['Office'].unique()
companies = data['cik'].unique()
co_names = data[['cik','name']].drop_duplicates(subset='cik')
character = ['cik', 'date','name','sic','Office','Industry Title','countryba']
zero_vals = ['ADDITIONALPAIDINCAPITAL','INTERESTPAID','PROCEEDSFROMISSUANCEOFCOMMONSTOCK',
             'SHAREBASEDCOMPENSATION','COMMITMENTSANDCONTINGENCIES',
             'STOCKISSUEDDURINGPERIODVALUENEWISSUES']
macroec = ['gdp','cpi','eir','unemployment','disp_inc','oil','ici']
ratios = ['CurrentRatio', 'CashRatio', 'DebtRatio', 'DebtToEquity',
          'ReturnOnAssets', 'ReturnOnEquity']

numeric2 = [var for var in data.columns if var not in character+zero_vals+macroec]

data = data.sort_values(['cik','date'])
data = data.reset_index(drop=True)

# extract macroeconimics
def extract_econ():
    import quandl
    quandl.ApiConfig.api_key = 'yWdUgsKPUi1ES-hKzGSe'
    min_dte = pd.Timestamp("2007-12-31")
#    max_dte = pd.Timestamp("2020-12-31")
    
    # GDP
    econ = quandl.get("FRED/GDP", start_date = min_dte, collapse='quarterly')
    econ.columns = ['gdp']
    # Consumer price index
    econ['cpi'] = quandl.get("FRED/CPIAUCSL", start_date = min_dte, collapse='quarterly')
    # effective federal rate
    econ['eir'] = quandl.get("FRED/DFF", start_date = min_dte, collapse='quarterly')
    # Unemployment
    econ['unemployment'] = quandl.get("FRED/UNRATE", start_date = min_dte, collapse='quarterly')
    # Real median household income
    econ['disp_inc'] = quandl.get("FRED/DSPIC96", start_date = min_dte, collapse='quarterly')
    # Crude oil prices (West Texas Intermediate)
    econ['oil'] = quandl.get("FRED/DCOILWTICO", start_date = min_dte, collapse='quarterly')
    # International commodities index
    econ['ici'] = quandl.get("RICI/RICI", authtoken="yWdUgsKPUi1ES-hKzGSe", start_date = min_dte, collapse='quarterly')
    
    econ = econ.reset_index()
    econ2 = pd.DataFrame()
    econ2['Date'] = econ['Date']
    # Derive macroeconomic yearly change ratios (to exclude seasonality)
    for var in econ.columns[1:]:
        for j in range(4,econ.shape[0]):
            econ2.loc[j,var] = econ.loc[j,var]/econ.loc[j-4,var] - 1
    econ2 = econ2.dropna().reset_index(drop=True)
    return econ, econ2

##### Interpolate missing quarters
###############################################
# Add missing observations where Qs are missing 
dates = pd.DataFrame(columns=['date'])
dates['date'] = data['date'].unique()
data1 = data.copy()
companies = data['cik'].unique()
i=0
for co in companies:
    i+=1
    if i%100 == 0:
        print(i)
    dates2 = dates[(dates['date']>=min(data.loc[data.cik==co,'date'])) & (dates['date']<=max(data.loc[data.cik==co,'date']))].copy()
    dates2.loc[:,'cik'] = co
    data1 = pd.merge(data1,dates2,left_on=['cik','date'],right_on=['cik','date'],how='outer').reset_index(drop=True)
data1 = data1.sort_values(['cik','date']).reset_index(drop=True)

# Interpolate to replace missing quarters
# Since dates have only been added inbetween, no need to loop by company
for var in numeric2:
    print(var)
    if data1[var].isnull().sum()>0:
        data1.loc[:,var] = data1.loc[:,var].interpolate(method='linear', limit_direction ='forward')
# Copy values for categorical variables
for var in character:
    print(var)
    for i in range(data1.shape[0]):
        if pd.isnull(data1.loc[i,var]):
            data1.loc[i,var] = data1.loc[i-1,var]

data1 = data1.fillna(0)
# Replace macroeconomics
econ, econ2 = extract_econ() # *** use function from DataExtract2
econ2['Date'] = econ2['Date'].dt.date
data1 = data1.drop(macroec,axis=1)
data1 = pd.merge(data1,econ2,left_on='date',right_on='Date',how='left').reset_index(drop=True)
data1 = data1.drop('Date',axis=1)

freq = data1.groupby(['date'])['cik'].nunique() # low volumes pre 2009/6/30, low data quality
freq.plot(kind="bar", title='Data volume') # low volumes pre 2011 (very low pre 2009)
data1 = data1[data1['date']<pd.Timestamp('2020-09-30')] # drop last month with 19 obs


##### Calculate financial ratios
###############################################
def calc_ratios(data):
    # Liquidity Ratios
    data['CurrentRatio'] = data['ASSETSCURRENT']/data['LIABILITIESCURRENT']
    data['CashRatio'] = data['CASHANDCASHEQUIVALENTSATCARRYINGVALUE']/data['LIABILITIESCURRENT']
    # Leverage ratios
    data['DebtRatio'] = data['LIABILITIES']/data['ASSETS']
    data['DebtToEquity'] = data['LIABILITIES']/data['STOCKHOLDERSEQUITY']
    # Profitability
    data['ReturnOnAssets'] = data['NETINCOMELOSS']/data['ASSETS']
    data['ReturnOnEquity'] = data['NETINCOMELOSS']/data['STOCKHOLDERSEQUITY']    
    data = data.replace([np.inf, -np.inf], 0) # replace nan,inf with zero
    return data

data1 = calc_ratios(data1)
data1 = data1.replace([np.inf, -np.inf], 0) # replace nan,inf with zero
data1 = data1.fillna(0)
numeric = [var for var in data1.columns if var not in character]
ratios = ['CurrentRatio', 'CashRatio', 'DebtRatio', 'DebtToEquity', 
          'ReturnOnAssets', 'ReturnOnEquity']

##### Save final dataset
###############################################
# Drop extra variables
data2 = data1.copy()
data2 = data2.drop(['ticker','Industry Title'],axis=1)
# Remove early data (low volumes) and Covid data
data2 = data2[(data1['date']>=pd.Timestamp('2009-12-31')) & 
              (data1['date']<=pd.Timestamp("2020-03-31"))]
# Drop companies with less than 5 years of data
period_cnt = data2.groupby('cik')['date'].count().reset_index().sort_values(by='date')
data2 = data2[~data2.cik.isin(period_cnt.loc[period_cnt.date<20,'cik'])]

data1.to_pickle("./dataf_interp0.pkl") # rerun
data2.to_pickle("./dataf_interp1.pkl") # rerun

for i in ratios+['Close','lClose','CloseAvg','lCloseAvg']:
    plt.scatter(data1.loc[:,"date"],data1.loc[:,i])
    plt.xlabel("Date")
    plt.ylabel(i)
    plt.show()


co=70
plt.plot(data1[data1.cik==companies[co]]['date'],data1[data1.cik==companies[co]]['lClose'])
plt.plot(data1[data1.cik==companies[co]]['date'],data1[data1.cik==companies[co]]['lCloseAvg'])
plt.legend(['lClose','lCloseAvg'])

data4 = data1.copy()
for i in ratios:
#    data4["l"+i] = np.log(data2[i])
    data4["l"+i] = data1[i]**(1/9)

lratios = ['lCurrentRatio', 'lCashRatio', 'lDebtRatio', 'lDebtToEquity',
       'lReturnOnAssets', 'lReturnOnEquity']
for i in lratios:
    plt.scatter(data4.loc[:,"date"],data4.loc[:,i])
    plt.xlabel("Date")
    plt.ylabel(i)
    plt.show()



