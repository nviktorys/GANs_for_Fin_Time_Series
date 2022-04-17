################################################
#####      2.3  Data Exploration           #####
################################################

import os
import pandas as  pd
import numpy as np
import pickle5
import matplotlib.pyplot as plt
import seaborn as sns
import squarify

plt.style.use('classic')

##### Load data
###############################################
os.getcwd()
os.chdir('.\\Data')
os.getcwd()

data = []
with open('./dataf_interp1.pkl','rb') as file:
    data = pickle5.load(file)
data = pd.DataFrame(data)
data = data.reset_index(drop=True)

# Create helper arrays
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
id = ['cik', 'date']
ind_vals = ['INTERESTPAID','PROCEEDSFROMISSUANCEOFCOMMONSTOCK',
             'SHAREBASEDCOMPENSATION',
             'STOCKISSUEDDURINGPERIODVALUENEWISSUES']
numeric = [var for var in data.columns if var not in character]
numeric2 = [var for var in data.columns if var not in character+zero_vals+macroec]

# Add grouped sic
# group sic - https://siccode.com/page/structure-of-sic-codes
data.sic = data.sic.astype('int')
#conditions = [(data.sic<=900),(data.sic<=1400),
#              (data.sic<=1700),(data.sic<=2800),
#              (data.sic<=2900),(data.sic<=3700),
#              (data.sic<=3900),(data.sic<=4900),
#              (data.sic<=5100),(data.sic<=5900),
#              (data.sic<=6700),(data.sic<=7300),
#              (data.sic<=7900),(data.sic<=9900),
#              (data.sic>9900)]
conditions = [(data.sic< 1000),(data.sic< 1500),
              (data.sic< 1800),(data.sic< 2300),
              (data.sic< 2800),(data.sic< 2900),
              (data.sic< 3700),(data.sic< 4000),
              (data.sic< 5000),(data.sic< 5200),
              (data.sic< 6000),(data.sic< 6800),
              (data.sic< 7900),(data.sic< 8400),
              (data.sic<=9900),(data.sic>9900)]
#groups = ['Agriculture','Mining','Construction','Manufacturing1','Manufacturing2',
#          'Manufacturing3','Manufacturing4','Transport','Wholesale','Retail',
#          'Finance','Services1','Services2','Administration','Other']
groups = ['Agriculture','Mining','Construction','Manufacturing1','Manufacturing2',
          'Manufacturing3','Manufacturing4','Manufacturing5','Transport',
          'Wholesale','Retail','Finance','Services1','Services2','Administration',
          'Other']
data['sicg'] = np.select(conditions, groups)
sicg = data['sicg'].unique()
data.sic = data.sic.astype('str')

#### Summary
######################################################
summary = data.describe()
#summary.to_csv("summary.csv")
# All vars
summary_num = pd.DataFrame()
summary_num['freq'] = data.notnull().sum()
summary_num['miss'] = data.isnull().sum()
summary_num['miss%'] = summary_num['miss']/(data.isnull().sum()+data.notnull().sum())
summary_num['unique'] = data.nunique()
summary_num['min'] = data.min()
summary_num['max'] = data.max()
#summary_num.to_csv("summary.csv")
# Numeric
summary = data[numeric].describe()


# Data frequency over time
freq = data.groupby(['date'])['cik'].nunique()
freq.plot(kind="bar", fontsize=8) 
plt.title('Data volume', fontsize=12) 
plt.show()

# Categorical
summary_char = data[character].describe()
summary_char2 = data[character].apply(lambda x: x.value_counts()).T.stack()
#summary_char.to_csv("summary.csv")

# Categotical cnt
# Country
country_cnt = data.groupby(['countryba'])['cik'].nunique().sort_values(ascending=False)
squarify.plot(country_cnt, label=country_cnt.index, alpha=0.4, 
              text_kwargs={'fontsize':10})
plt.axis('off')
plt.show()
# Sector
sic_cnt = data.groupby(['sic','Office'])['cik'].nunique().sort_values(ascending=False).reset_index()
Office = data.Office.unique()
conditions = [(sic_cnt.Office==Office[0]),(sic_cnt.Office==Office[1]),
              (sic_cnt.Office==Office[2]),(sic_cnt.Office==Office[3]),
              (sic_cnt.Office==Office[4]),(sic_cnt.Office==Office[5])]
colors = ['green','purple','orange','brown','blue','red']
sic_cnt['color'] = np.select(conditions, colors)

squarify.plot(sic_cnt.cik, label=sic_cnt.sic, alpha=0.4, 
              text_kwargs={'fontsize':10}, color=sic_cnt.color)
plt.axis('off')
plt.show()
#sic_cnt.to_csv("summary.csv")
# Freqs by Office
sector_freq = data['Office'].value_counts('cik')


def plot_categorical(df,var):
    from textwrap import wrap
    sector_freq = df[var].value_counts('cik')
    sns.set(style="darkgrid")
    sns.barplot(x= sector_freq.index, y =sector_freq.values, alpha=0.9)
    plt.tick_params(axis='x', which='major', pad=10, labelrotation=-55)
    plt.title('Frequency Distribution by sector')
    labels = ['\n'.join(wrap(l,12)) for l in pd.Series(sector_freq.index.values)]
    plt.xticks(list(range(0,len(sector_freq))),labels)
    plt.ylabel('Percent of comapnies', fontsize=12)
    plt.xlabel('Sector', fontsize=12)
    plt.show()
plot_categorical(data,'Office')
plot_categorical(data,'sicg')



#### Plot Data
######################################################

# Plot freqs by sector
fig, axes = plt.subplots(2,3, figsize=(15,5), sharex='col', sharey='row')
for i,ax in enumerate(axes.flatten()):
    freq_sec = data[data['Office']==sectors[i]].groupby(['date'])['cik'].nunique()
    freq_sec.plot(kind='bar',title=sectors[i], ax=ax)
    
clarity_color_table = pd.crosstab(index=data["date"], 
                          columns=data["Office"])
clarity_color_table.plot(kind="bar", 
                 figsize=(8,8),
                 stacked=True)

### Sample plots over time
var = 45 # 1, 12, 
plt.figure(figsize=(5.5, 5.5))
plt.plot('date',numeric[var], data=data.loc[data['cik']==companies[300],['date', numeric[var]]], linestyle='-', marker='*', color='b')
plt.plot('date',numeric[var], data=data.loc[data['cik']==companies[500],['date', numeric[var]]], linestyle='-', marker='*', color='r')
plt.plot('date',numeric[var], data=data.loc[data['cik']==companies[1300],['date', numeric[var]]], linestyle='-', marker='*', color='g')
plt.plot('date',numeric[var], data=data.loc[data['cik']==companies[2300],['date', numeric[var]]], linestyle='-', marker='*', color='y')
plt.legend([co_names.iloc[300,1],co_names.iloc[500,1],co_names.iloc[1300,1],co_names.iloc[2300,1]], loc=1, fontsize=8)
plt.title(numeric[var])
#plt.ylabel('Amount in $')
plt.ylabel('Ratio')
plt.xlabel('Years')

### Sample scatter plots 
for i in range(len(numeric)):
    x = data.loc[:,numeric[14]]**(1/9)
    y = data.loc[:,numeric[15]]**(1/9)
    #sns.scatterplot(x=x,y=y,hue=data.Office,legend=False)
    plt.scatter(x=x,y=y,marker='.', s=3)
    plt.xlabel(x.name)
    plt.ylabel(y.name)
    plt.show()
    
co=9
co=983
x = data.loc[data.cik==companies[co],numeric[33]]
y = data.loc[data.cik==companies[co],numeric[13]]**(1/9)
plt.scatter(x=x,y=y,marker='.', s=40)
plt.title(data.loc[data.cik==companies[co],'name'].tolist()[-1])
plt.xlabel(x.name)
plt.ylabel(y.name)
plt.show()

groups = data[[x,y,'Office']].groupby(['Office'])
for name, group in groups:
    plt.plot(group[x], group[y], marker="o", linestyle="", label=name, ms=2)
plt.xlabel(x)
plt.ylabel(y)
plt.legend()
# pairplots



##### Correlations, Pairplots
###############################################
# Convert num vars to **(1/9)
dv = ['Close', 'CloseAvg',  'lClose', 'lCloseAvg']
numeric3 = [var for var in data.columns if var not in 
            character+zero_vals+macroec+dv]
data2 = data.copy()
for var in numeric3:
    data2[var] = np.float_power(abs(data[var]), 1./9)*np.sign(data[var])


# Correlation matrix
labels = ['Depreciation', 'Additional Capital', 'Assets', 'Current Assets', 
          'Cash', 'Commitments', 'Common Stock', 'Tax allowence', 'EPS',
          'EPS diluted', 'Tax benefit', 'Interest paid', 'Liabilities',
          'Liabilities Current', 'Cash-finance', 'Cash-Invest', 'Cash-Operat',
          'Net Income', 'Operating Income', 'Payments due', 'Payments in 3y',
          'Payments in 2y', 'Common stock issue', 'Property gross', 
          'Property net', 'Retained Earnings', 'Share compensation', 'Equity',
          'Stock neew issue', 'Close', 'CloseAvg',  'lClose', 'lCloseAvg',
          'gdp', 'cpi', 'eir', 'unemployment', 'disp_inc', 'oil', 'ici', 
          'CurrentRatio', 'CashRatio', 'DebtRatio', 'DebtToEquity', 
          'ReturnOnAssets', 'ReturnOnEquity']
corr = data[numeric].corr()
corr = data2[numeric].corr()
plt.matshow(corr)
plt.yticks(range(len(numeric)), labels)
plt.tick_params(axis='both', which='major', labelsize=6)
cb = plt.colorbar(aspect=20,pad=.02)
cb.ax.tick_params(labelsize=7)
plt.clim(-1,1)
plt.show()
#corr.to_csv("summary.csv")

#Correlation by sector
sic = np.sort(data2['sic'].astype('int').unique()).astype('str')
sic_cnt = data.groupby(['sic'])['cik'].nunique().sort_values(ascending=False)
#sic_cnt.to_csv("summary.csv")

# Correlation by Office
vars = ['Office', sectors]
vars = ['sic', sic]
vars = ['sicg', sicg]
for i in range(len(vars[1])):
    corr = data2.loc[data2[vars[0]]==vars[1][i],numeric].corr()
    plt.matshow(corr)
    plt.yticks(range(len(numeric)), labels)
    plt.tick_params(axis='both', which='major', labelsize=6)
    plt.title(vars[1][i])
    cb = plt.colorbar(aspect=20,pad=.02)
    cb.ax.tick_params(labelsize=7)
    plt.clim(-1,1)
    plt.show()


# Sample plots
###############

# scatter plots with median value
def plots_s(data,vars,es,transf=1,by="",lgd=False):
    if len(by)>0:
        data_temp = data[['date',by]].copy()
        data_temp = data_temp.drop_duplicates()
        data_temp = data_temp.set_index(['date',by])
        for var in vars:
            data_temp[var] = data.groupby([data['date'],data[by]])[[var]].median()
            for e in es:        
                data_temp[e] = data.groupby([data['date'],data[by]])[[e]].median()
                sns.scatterplot(data=data_temp, x=var,y=data_temp[e]**(transf), hue=by, legend=lgd)
                plt.show()
    else:
        data_temp = pd.DataFrame()
        data_temp['date'] = data['date'].unique()
        data_temp = data_temp.set_index('date')
        for var in vars:
            data_temp[var] = data.groupby([data.date])[[var]].median()
            for e in es:        
                data_temp[e] = data.groupby([data.date])[[e]].median()
                sns.scatterplot(data=data_temp, x=var,y=data_temp[e]**(transf))
                plt.show()

# distribution plots
def plots_d(data,var,group="", lgd=False):
    if len(group)>0:
        sns.displot(data, x=var, hue=group, kind="kde", fill=True, legend=lgd)
    else:
        sns.displot(data, x=var, kind="kde", fill=True)


# Scatterplots
plots_s(data,['lCloseAvg'],[numeric[40]],transf=1/9)
plots_s(data,['CloseAvg'],numeric,by='Office')
plots_s(data,['CloseAvg'],numeric)
plots_s(data.loc[(data.Office==sectors[5]),:],['Close'],[numeric[17]])
plots_s(data.loc[(data.Office==sectors[3]),:],['Close'],numeric)
plots_s(data,['Close'],numeric,by='Office')
plots_s(data,['CloseAvg'],['gdp'])
plots_s(data,['lClose'],['gdp'])
plots_s(data,['lCloseAvg'],['gdp'])
#plots_s(data,['ASSETS'],['gdp'],by='Office')
#plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)


# Distributions
df=data2
plots_d(df,'ASSETS','Office',lgd=True)
plots_d(df,'NETINCOMELOSS','Office')
plots_d(df,'STOCKHOLDERSEQUITY','Office')
plots_d(df,'CurrentRatio','Office')
plots_d(df,'ReturnOnEquity','Office')
plots_d(df,'CloseAvg','Office')
plots_d(df,'lCloseAvg','Office')


# Save transformed vars
data2 = data2.drop(['sicg'],axis=1)
data2.to_pickle("./dataf_interp2.pkl") # rerun












