################################################
#####      2.1  Data Cleaning              #####
################################################

import os
import pandas as  pd
import numpy as np
import pickle
import matplotlib.pyplot as plt
import seaborn as sns

##### Load data
###############################################
os.getcwd()
os.chdir('.\\Data')
os.getcwd()

data = []
with open('./data0.pkl','rb') as file:
    data = pickle.load(file)
data = pd.DataFrame(data)

# Amend column formats
data['cik'] = data.cik.astype(str)
data['sic'] = data.sic.astype(str)
data['date'] = data['date'].dt.date

character = ['cik', 'date','name','ticker','sic','Office','Industry Title','countryba']
macroec = ['gdp','cpi','eir','unemployment','disp_inc','oil','ici']
numeric = [var for var in data.columns if var not in character]
companies = data['cik'].unique()

# sort data by cik, date
data = data.sort_values(['cik','date'])
data = data.reset_index(drop=True)

##### Summary
###############################################
summary = data.describe(include='all')
# Statistics by var
summary_num = pd.DataFrame()
summary_num['freq'] = data.notnull().sum()
summary_num['miss'] = data.isnull().sum()
summary_num['miss%'] = summary_num['miss']/(data.isnull().sum()+data.notnull().sum())
summary_num['unique'] = data.nunique()
summary_num['min'] = data.min()
summary_num['max'] = data.max()
#summary_num.to_csv("summary.csv")

# Chack negative values
check = data.loc[data[numeric[56]]<0,['cik','date',numeric[56]]]
obs = data.loc[data['cik']== '7039',['cik','date',numeric[28]]]


#### Amend some negative values
var = 'ACCOUNTSPAYABLECURRENT'
data.loc[(data['cik']== '65984') & (data[var]<0),[var]] = -1*data.loc[(data['cik']== '65984') & (data[var]<0),[var]]
data.loc[(data['cik']== '862651') & (data[var]<0),[var]] = -1*data.loc[(data['cik']== '862651') & (data[var]<0),[var]]
data.loc[(data['cik']== '1114208') & (data[var]<0),[var]] = -1*data.loc[(data['cik']== '1114208') & (data[var]<0),[var]]
data.loc[(data['cik']== '1223533') & (data[var]<0),[var]] = -1*data.loc[(data['cik']== '1223533') & (data[var]<0),[var]]

var = 'ACCOUNTSRECEIVABLENETCURRENT'
data.loc[(data['cik']== '1388180') & (data[var]<0),[var]] = -1*data.loc[(data['cik']== '1388180') & (data[var]<0),[var]]
data.loc[(data['cik']== '1443863') & (data[var]<0),[var]] = -1*data.loc[(data['cik']== '1443863') & (data[var]<0),[var]]
data.loc[(data['cik']== '1517130') & (data[var]<0),[var]] = -1*data.loc[(data['cik']== '1517130') & (data[var]<0),[var]]
data.loc[(data['cik']== '1680132') & (data[var]<0),[var]] = -1*data.loc[(data['cik']== '1680132') & (data[var]<0),[var]]

var = 'ACCRUEDLIABILITIESCURRENT'
data.loc[(data['cik']== '65984') & (data[var]<0),[var]] = -1*data.loc[(data['cik']== '65984') & (data[var]<0),[var]]
data.loc[(data['cik']== '1223533') & (data[var]<0),[var]] = -1*data.loc[(data['cik']== '1223533') & (data[var]<0),[var]]
data.loc[(data['cik']== '1559356') & (data[var]<0),[var]] = -1*data.loc[(data['cik']== '1559356') & (data[var]<0),[var]]

var = 'ASSETS'
data.loc[(data['cik']== '97517') & (data[var]<0),[var]] = -1*data.loc[(data['cik']== '97517') & (data[var]<0),[var]]
data.loc[(data['cik']== '40194') & (data[var]<0),[var]] = -1*data.loc[(data['cik']== '40194') & (data[var]<0),[var]]
data.loc[(data['cik']== '1093683') & (data[var]<0),[var]] = -1*data.loc[(data['cik']== '1093683') & (data[var]<0),[var]]

var = 'ASSETSCURRENT'
data.loc[(data['cik']== '40194') & (data[var]<0),[var]] = -1*data.loc[(data['cik']== '40194') & (data[var]<0),[var]]

var = 'CASHANDCASHEQUIVALENTSATCARRYINGVALUE'
data.loc[(data['cik']== '1554970') & (data[var]<0),[var]] = -1*data.loc[(data['cik']== '1554970') & (data[var]<0),[var]]

var_positive = ['ADDITIONALPAIDINCAPITAL','COMMONSTOCKVALUE', 'COMMONSTOCKPARORSTATEDVALUEPERSHARE', 'DEPRECIATION', 
                'INTERESTPAID', 'INVENTORYNET', 'LIABILITIESANDSTOCKHOLDERSEQUITY',
                'LIABILITIESCURRENT', 'OPERATINGLEASESFUTUREMINIMUMPAYMENTSDUE', 'OPERATINGLEASESFUTUREMINIMUMPAYMENTSDUECURRENT',
                'OPERATINGLEASESFUTUREMINIMUMPAYMENTSDUEINFOURYEARS', 'OPERATINGLEASESFUTUREMINIMUMPAYMENTSDUEINTHREEYEARS',
                'OPERATINGLEASESFUTUREMINIMUMPAYMENTSDUEINTWOYEARS', 'OTHERASSETSNONCURRENT', 'PAYMENTSTOACQUIREPROPERTYPLANTANDEQUIPMENT',
                'PREFERREDSTOCKPARORSTATEDVALUEPERSHARE', 'PREFERREDSTOCKVALUE', 'PROCEEDSFROMISSUANCEOFCOMMONSTOCK',
                'PROPERTYPLANTANDEQUIPMENTGROSS', 'PROPERTYPLANTANDEQUIPMENTNET', 'SHAREBASEDCOMPENSATION', 'STOCKISSUEDDURINGPERIODVALUENEWISSUES']
for var in var_positive:
    data.loc[(data[var]<0),[var]] = -1*data.loc[(data[var]<0),[var]]



##### Missing Data
#####################################################
summary = data.describe(include='all')

# Data frequency over time
freq = data.groupby(['date'])['cik'].nunique()
freq.plot(kind="bar", title='Data volume') # low volumes pre 2011 (very low pre 2009)

#### Drop columns: 
# 'value per share' (typically 0.01 by default, no additionall information) 
# LIABILITIESANDSTOCKHOLDERSEQUITY (same as ASSETS), 
# CASHANDCASHEQUIVALENTSPERIODINCREASEDECREASE (same as CASH)
data = data.drop(['COMMONSTOCKPARORSTATEDVALUEPERSHARE'],axis=1)
data = data.drop(['LIABILITIESANDSTOCKHOLDERSEQUITY'],axis=1)
data = data.drop(['CASHANDCASHEQUIVALENTSPERIODINCREASEDECREASE'],axis=1)

# Check for missing data
miss = pd.DataFrame()
miss['miss'] = data.isnull().sum()
miss['miss%'] = miss['miss']/(data.isnull().sum()+data.notnull().sum())
miss['missCo'] = data.groupby(['cik']).max().isnull().sum()
miss['missCo%'] = data.groupby(['cik']).max().isnull().sum() / data['cik'].nunique()

# drop obs with missing macroeconomics
data = data[data['gdp'].notnull()]

# Variables where missing values may be replaced with zeros 
zero_vals = ['INTERESTPAID','ADDITIONALPAIDINCAPITAL','PROCEEDSFROMISSUANCEOFCOMMONSTOCK',
             'SHAREBASEDCOMPENSATION','COMMITMENTSANDCONTINGENCIES',
             'STOCKISSUEDDURINGPERIODVALUENEWISSUES']

# Numeric variables excl macroec and zero_vals
numeric2 =[x for x in numeric[:57] if x not in zero_vals] # without macroeconomics and items with zero's replacements

#### Drop variables with 20%+ missing values by company
to_drop = miss[miss['missCo%']>0.2].reset_index()['index']
to_drop = to_drop[~to_drop.isin(zero_vals)]
data1 = data.drop(to_drop, axis=1).reset_index(drop=True)

numeric2 = [var for var in data1.columns if var not in character]
        
#### Replace missings with 0 where items can legally be missing for long periods
for var in zero_vals:
    data1[var] = data1[var].fillna(0)

#### Interpolate remaining missing values forward
for var in numeric2:
    print(var)
    for co in companies:
        if data1[data1['cik']==co][var].isnull().sum()>0:
            data1.loc[data1['cik']==co,var] = data1[data1['cik']==co][var].interpolate(method='linear', limit_direction ='forward')
miss['miss1'] = data1.isnull().sum()
miss['miss1%'] = miss['miss1']/(data1.isnull().sum()+data1.notnull().sum())


#### Interpolate remaining missing values backward
for var in numeric2:
    print(var)
    for co in companies:
        if data1[data1['cik']==co][var].isnull().sum()>0:
            data1.loc[data1['cik']==co,var] = data1[data1['cik']==co][var].interpolate(method='linear', limit_direction ='backward')
miss['miss2'] = data1.isnull().sum()
miss['miss2%'] = miss['miss2']/(data1.isnull().sum()+data1.notnull().sum())


#### Drop observations with missing key variables
data2 = data1[~data1.ASSETS.isna() & ~data1.STOCKHOLDERSEQUITY.isna() & ~data1.NETINCOMELOSS.isna()].copy()
miss['miss3'] = data2.isnull().sum()
miss['miss3%'] = miss['miss3']/(data1.isnull().sum()+data1.notnull().sum())

#### Derive missing values from non-missing where possible
# ASSETSCURRENT
data2.loc[data2.ASSETSCURRENT.isna() & (data2.ASSETS==0),'ASSETSCURRENT'] = 0
data2.loc[data2.ASSETSCURRENT.isna(),'ASSETSCURRENT'] = data2.loc[data2.ASSETSCURRENT.isna(),'CASHANDCASHEQUIVALENTSATCARRYINGVALUE']
data2.loc[data2.ASSETSCURRENT.isna(),'ASSETSCURRENT'] = data2.loc[data2.ASSETSCURRENT.isna(),'ASSETS'] - data2.loc[data2.ASSETSCURRENT.isna(),'PROPERTYPLANTANDEQUIPMENTNET']
# LIABILITIES
data2.loc[data2.LIABILITIES.isna(),'LIABILITIES'] = data2.loc[data2.LIABILITIES.isna(),'ASSETS'] - data2.loc[data2.LIABILITIES.isna(),'STOCKHOLDERSEQUITY']
data2.loc[data2.LIABILITIES.isna(),'LIABILITIES'] = data2.loc[data2.LIABILITIES.isna(),'LIABILITIESCURRENT']
# PROPERTYPLANTANDEQUIPMENTNET
data2.loc[data2.PROPERTYPLANTANDEQUIPMENTNET.isna(),'PROPERTYPLANTANDEQUIPMENTNET'] = data2.loc[data2.PROPERTYPLANTANDEQUIPMENTNET.isna(),'ASSETS'] - data2.loc[data2.PROPERTYPLANTANDEQUIPMENTNET.isna(),'ASSETSCURRENT']
# OPERATINGINCOMELOSS
data2.loc[data2.OPERATINGINCOMELOSS.isna(),'OPERATINGINCOMELOSS'] = data2.loc[data2.OPERATINGINCOMELOSS.isna(),'NETINCOMELOSS']

miss['miss4'] = data2.isnull().sum()
miss['miss4%'] = miss['miss4']/(data1.isnull().sum()+data1.notnull().sum())

#### Set remaining missing to zero
data2 = data2.fillna(0)

#miss.reset_index(inplace=True)

data1.to_pickle("./data1.pkl")
data2.to_pickle("./data2.pkl")
#data2 = pd.DataFrame(pickle.load(open('./data2.pkl','rb')))


##### Outliers
#####################################################
freq = data2.groupby(['date'])['cik'].nunique() # low volumes pre 2009/6/30, also likely to be a low quality data
data3 = data2[data2['date']>=pd.Timestamp('2009-06-30')].copy()
data3[['ASSETS']].plot.density()

numeric2 = [var for var in data3.columns if var not in character+macroec]


# Box plots
font = {'family' : 'Tahoma',
        'weight' : 'normal',
        'size'   : 6}

plt.rc('font', **font)

plt.figure(0)
plots=[]
l = 0
for i in range(4):
    for j in range(5):
        ax = plt.subplot2grid((4,5), (i,j))
        ax.boxplot(data3[numeric2[l]])
        ax.set_title(numeric2[l][:12], fontsize=6.5, pad=3, loc='right')
#        ax.title.set_position([.5,.5])
        ax.tick_params(axis='both', which='major', labelsize=6,direction="in", pad=-13)
        l+=1
plt.show()

# Identify top 0.1% multivariate outliers with Isolation Forest
from sklearn.ensemble import IsolationForest

X = data3.loc[:,numeric2].dropna()

clf = IsolationForest(max_samples=500, contamination=0.001, random_state=1)
preds = clf.fit_predict(X)
outif = data3[preds<1]

### The outlier observations appear to have legal values. It is mostly very large companies
# such as GE, Pfizer, Exxon, WalMart, Apple, etc.

numeric = [var for var in data3.columns if var not in character+macroec]
### Boxplots
var = 7
sns.boxplot(data=data3, x='date', y=numeric[var])
check = data3.loc[data3[numeric[var]]==max(data3[numeric[var]]), ['cik','name','date',numeric[var]]]
check = data3.nlargest(5,numeric[var])[['cik','Office','name','date',numeric[var]]]
check = data3.nsmallest(1,numeric[var])[['cik','Office','name','date',numeric[var]]]
obs = data3[data3['cik']=='1136893']
# 0 - AdditionalPaidInCapital - the outlier is a legal value (AMERI METRO issued more stocks)
# 1,2 - Assets - outliers are General Electric
# 3 - CashValue - wrong values, added extra 6 zeros
data3.loc[data3.nlargest(2,numeric[3]).index.values,[numeric[3]]] = data3.nlargest(2,numeric[3])[[numeric[3]]]/(10**6)
# 4 - Commitments - outliers American Airline - Liabilities subject to compromise
# 5 - CommonStockValue - outlier Petrobras, apper to be a legal entry
# 6 - InterestPid - outlier LLEnergy, 6 extra zeros
data3.loc[data3.nlargest(3,numeric[6]).index.values,[numeric[6]]] = data3.nlargest(3,numeric[6])[[numeric[6]]]/(10**6)
# 7 - Liabilities - outliers are General Electric
# 8 - LiabilitiesCurrent - outliers are General Electric
# 9 - CashFromFinAct - outlier LLEnergy, 6 extra zeros
data3.loc[data3.nlargest(12,numeric[9]).index.values,[numeric[9]]] = data3.nlargest(12,numeric[9])[[numeric[9]]]/(10**6)
# 10 - CashFromInvAct - outlier LLEnergy, 6 extra zeros
data3.loc[data3.nsmallest(4,numeric[10]).index.values,[numeric[10]]] = data3.nsmallest(4,numeric[10])[[numeric[10]]]/(10**6)
# 11 - CashFromOprAct - outlier LLEnergy, 6 extra zeros
data3.loc[data3.nlargest(12,numeric[11]).index.values,[numeric[11]]] = data3.nlargest(12,numeric[11])[[numeric[11]]]/(10**6)
# 14 - ProceedsFromStock - outlier LLEnergy, 6 extra zeros
data3.loc[data3.nlargest(3,numeric[14]).index.values,[numeric[14]]] = data3.nlargest(3,numeric[14])[[numeric[14]]]/(10**6)
# 15,16 - Property, RetainedEarnings - higher values for EXXON MOBILE
# 19 - StockIssued - outlier Fidedlity Nat Inf - worldpay acquisition

# Save final data
data3.to_pickle("./data.pkl")


