################################################
#####      1.2  Data Preparation 2         #####
################################################

import os
import zipfile
import pandas as  pd
import pickle5
import yfinance as yf
import sys
import numpy as np

##### Set working directory
###############################################
os.getcwd()
os.chdir('.\\Data')
os.getcwd()


##### Load data
#####################################################
data = []
with open('./data_t.pkl','rb') as file:
    data = pickle5.load(file)
data = pd.DataFrame(data)

##### Add extra variables
#####################################################

##### Add country of origin
#####################################################

print("Extract Sector data")
l = []
for j in range(2009,2021):
    for i in range(1,5):
        l.append(str(j)+"q"+str(i))
l.pop(0)
l.pop(len(l)-1)
i=0
data_s = pd.DataFrame()
data_s2 = []

for d in l:
    print("Extracting peiod ", d)
    zip = zipfile.ZipFile(d+str(".zip"))
    file = zip.read('sub.txt')
    file1 = file.decode("utf-8", errors='ignore')
    file2 = file1.split('\n')
    
    for n in range(len(file2)-1):
        if n==0:
            if i==0:
                data_s2.append([file2[n].split('\t')[i] for i in [1,4]])
        else:
             data_s2.append([file2[n].split('\t')[i] for i in [1,4]])
    i+=n+1

data_s = data_s.append(data_s2)
new_header = data_s.iloc[0] #grab the first row for the header
data_s = data_s[1:] #take the data less the header row
data_s.columns = new_header #set the header row as the df header
data_s = data_s[data_s['cik']!=""].drop_duplicates('cik').reset_index(drop=True)

data_s[['cik']] = data_s[['cik']].astype(int)
data[['cik']] = data[['cik']].astype(int)

# merge to main data
data = pd.merge(data,data_s,on='cik',how='left') 

##### Get economic variables from Federal reserve data: https://www.quandl.com/
#####################################################

# Extract minimum and maximum dates
#min_dte = data['date'].min()
#max_dte = data['date'].max()

# extract macroeconimics
def extract_econ():
    import quandl
    quandl.ApiConfig.api_key = 'yWdUgsKPUi1ES-hKzGSe'
    min_dte = pd.Timestamp("2007-12-31")
    max_dte = pd.Timestamp("2020-12-31")
    
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
econ, econ2 = extract_econ()

# Align dates in the main data (add / deduct month to match quarter ends)
for i in range(data.shape[0]):
    if data.loc[i,'date'].month in [2,5,8,11]:
        data.loc[i,'date'] = data.loc[i,'date']+pd.DateOffset(months=1)+pd.offsets.MonthEnd(0)
    if data.loc[i,'date'].month in [1,4,7,10]:
        data.loc[i,'date'] = data.loc[i,'date']+pd.DateOffset(months=-1)+pd.offsets.MonthEnd(0)
dates = data.date.dt.month.unique()
# Drop duplicates (some Names have different spelling and appear twice (WORLDs INC & WORLDS.COM INC))
# drop duplicates with more missing values
dups =data[data.duplicated(subset=['cik','date'], keep=False)]
dups.loc[:,['miss']] = dups.apply(lambda x: x.count(), axis=1)
dup_keep = dups.groupby(['cik','date'])['miss'].idxmax()
dup_drop = dups.loc[~dups.index.isin(dup_keep)].index
data1 = data.loc[~data.index.isin(dup_drop)]

# merge to main data
data1 = pd.merge(data1,econ2,left_on='date',right_on='Date',how='left').drop(['Date'],axis=1).reset_index(drop=True)


##### Add ticker and stock information
###############################################
companies = data1['cik'].unique() #6,683
# Load tickers
cik_ticker = pd.read_csv('./tickers.csv')

# Convert cik to numeric
data1.cik = data1['cik'].astype(int)

# Merge on ticker
tickers = pd.merge(data1[['date','cik']],cik_ticker, on='cik', how='inner')
tickers = tickers['ticker'].unique() # 5,296

# Extract history
#tickers = data1.ticker.unique()
tickers_df = pd.DataFrame()
to=len(tickers)
digits = len(str(to - 1))
delete = "\b" * (digits)
i=0
for tic in tickers:
    i+=1
    try:
        print("{0}{1:{2}}".format(delete, i, digits), end="")
        sys.stdout.flush()
        if len(yf.Ticker(tic).history(interval='1mo', period='max'))>4:
            hist = yf.Ticker(tic).history(interval='1mo', period='max')[['Close']].resample('M').mean()
            hist['CloseAvg'] = yf.Ticker(tic).history(interval='1d', period='max')[['Close']].resample('M').mean()
            hist['ticker'] = tic
            hist['cik'] = cik_ticker[cik_ticker.ticker==tic].cik.values[0]
            hist['date'] = hist.index.to_period('M').to_timestamp('M')
            hist.date = hist.date.dt.date
            hist = hist.reset_index(drop=True)
    #        for j in range(1,hist.shape[0]):
    #            hist.loc[j,'Ratio'] = hist.loc[j,'Close']/hist.loc[j-1,'Close'] - 1
            hist = hist.dropna()
            tickers_df = tickers_df.append(hist, ignore_index=True)
    except:
        pass
        
tickers2 = tickers_df.ticker.unique() #4,694
to_drop = tickers_df[tickers_df['Close']<0].ticker.unique()
# Drop duplicates
dup = tickers_df.groupby('cik')['ticker'].nunique()
dup = tickers_df[tickers_df.cik.
                 isin(dup[dup>1].index.values)].groupby(
                     ['cik','ticker'])['date'].nunique().reset_index()
dup_max = dup.groupby('cik')['date'].max().reset_index()
dup_keep = pd.merge(dup,dup_max,on=['cik','date'],how='inner')
dup_drop = dup[~dup.ticker.isin(dup_keep.ticker)]['ticker'] # subsidiaries
dup_drop2 = dup_keep.loc[~dup_keep.index.
                         isin(dup_keep['cik'].
                              drop_duplicates().index)]['ticker'] # comapnies traded on multiple markets
tickers_df2 = tickers_df[~tickers_df.ticker.isin(dup_drop.tolist()+dup_drop2.tolist())]
tickers_df2.loc[:,'date'] = pd.to_datetime(tickers_df2.date)

# merge history
data2 = pd.merge(data1,tickers_df2[['date','ticker','Close','CloseAvg','cik']], on=['date','cik'], how='inner')
#data2 = data2.dropna()
data2 = data2[~data2.ticker.isin(to_drop)]
data2.cik = data2.cik.astype(str)
companies = data2['cik'].unique() #4,227

# Some cik numers may be inherited by other companies
# Identify this cases by checking of the sector number (sic) has changed
# and amend their cik number to treat them as different companies
# (company names can't be used due to spelling variations)
cik_change_cnt = data2.groupby('cik')['sic'].nunique()[data2.groupby('cik')['sic'].nunique()>1]
cik_change_pairs = data2.groupby('cik')['sic'].unique()[data2.groupby('cik')['sic'].nunique()>1]

for co in list(cik_change_pairs.index):
    sec = list(cik_change_pairs[co])
#    print(sec)
    for secc in range(1,len(sec)):
        data2.loc[(data2.cik==co)&(data2.sic==sec[secc]),'cik'] = co + 'z'*secc
companies = data2['cik'].unique() # 4,790


data2['lClose'] = np.log(data2['Close'])
data2['lCloseAvg'] = np.log(data2['CloseAvg'])

# Keep co's with 5+ years of observations
period_cnt = data2.groupby('cik')['date'].count().reset_index()
data3 = data2[~data2.cik.isin(period_cnt.loc[period_cnt.date<20,'cik'])]
companies = data3['cik'].unique() #(10 - 1,868, 5 - 3113)

##### Save data
#####################################################

data2.to_pickle("./data00.pkl")
#data2 = pd.DataFrame(pickle5.load(open('./data00.pkl','rb')))
data3.to_pickle("./data0.pkl")

