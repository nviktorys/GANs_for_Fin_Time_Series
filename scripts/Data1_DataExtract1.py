################################################
#####       1.1 Initial Data Extract       #####
################################################

import os
import zipfile
import pandas as  pd
import pickle

##### Set working directory
###############################################
os.getcwd()
os.chdir('.\\Data')
os.getcwd()

##### Extract Financial Statements data
###############################################
# Create list of all datafile names
l = []
for j in range(2009,2021):
    for i in range(1,5):
        l.append(str(j)+"q"+str(i))
l.pop(0)
l.pop(len(l)-1)

# Extract Financial Statements data
i=0
data1 = pd.DataFrame()
data2 = []
for d in l:
    print("Extracting period: ", d)
    zip = zipfile.ZipFile(d+str(".zip"))
    file = zip.read('num.txt')
    file1 = file.decode("utf-8", errors='ignore')
    file2 = file1.split('\n')
    
    for n in range(len(file2)-1):
        if n==0:
            if i==0:
                data2.append(file2[n].split('\t'))
        else:
            data2.append(file2[n].split('\t'))
    i+=n+1

data1 = data1.append(data2)
new_header = data1.iloc[0] #grab the first row for the header
data1 = data1[1:] #take the data less the header row
data1.columns = new_header #set the header row as the df header
 
##### Extract Sector data
###############################################
print("Extract Sector data")
i=0
data_s = pd.DataFrame()
data_s2 = []
for d in l:
    print("Extracting period ", d)
    zip = zipfile.ZipFile(d+str(".zip"))
    file = zip.read('sub.txt')
    file1 = file.decode("utf-8", errors='ignore')
    file2 = file1.split('\n')
    
    for n in range(len(file2)-1):
        if n==0:
            if i==0:
                data_s2.append([file2[n].split('\t')[i] for i in [0,1,2,3,25,26,27,33]])
        else:
            data_s2.append([file2[n].split('\t')[i] for i in [0,1,2,3,25,26,27,33]])
    i+=n+1

data_s = data_s.append(data_s2)
new_header = data_s.iloc[0] #grab the first row for the header
data_s = data_s[1:] #take the data less the header row
data_s.columns = new_header #set the header row as the df header

# filter to companies with populated sectors;
data_s2 = data_s[(data_s.sic!='') & (data_s.fy!='')]

data_s2 = data_s2.drop(['form','fy'],axis=1)
data_s2 = data_s2.drop_duplicates()

data_s2.name.nunique() # 16,541 unique companies

data_s2['sic'] = data_s2['sic'].astype(int)

sector_name = pd.read_csv('SIC_sectors.csv')
data_s2 = pd.merge(data_s2,sector_name,left_on='sic',right_on='sic',how='left')

# Drop Fin sector
data_s2 = data_s2[(data_s2.Office!='Office of Finance') & (data_s2.Office!='Office of Structured Finance')]
data_s2.name.nunique() # 14,720 unique companies


##### Merge sectors to the main data
#####################################################
print("Merge sectors to the main data")

data3 = pd.merge(data1,data_s2,left_on='adsh',right_on='adsh',how='inner') # N obs - 80,491,550
print(data3.cik.nunique()) # N companies - 11,561
print(data3.tag.nunique()) # N variab,es - 1,316,149
print(data1.memory_usage(index=True).sum()) # 7.4 Gb
del [data1, data2, data_s2, data_s]

##### Drop observations, filter data
#####################################################
print("Drop observations")
print(data3.dtypes)


# Convert columns formats
print("Convert formats")
data3['value'] = data3['value'].replace(r'^\s*$', 0, regex=True) # replace missing values with 0
data3['value'] = data3['value'].astype(float)
data3[['qtrs','cik','sic']] = data3[['qtrs','cik','sic']].apply(pd.to_numeric,errors='coerce')
data3['ndate'] = data3['ddate'].astype(int)
data3['date'] = pd.to_datetime(data3[data3.ndate <= 20200930]['ddate'], format='%Y%m%d') # remove dates outside of data range
data3['period'] = pd.to_datetime(data3['period'])

# Filter data
print("Select values in USD")
print("Limit observations to a 1 year outcome")
print("Keep only us-gaap reporting variables")
data3 = data3[(data3.uom == 'USD') & (data3.qtrs <= 4) & (data3.version.str.slice(stop=7) == "us-gaap")] # N obs - 63,334,962 (56,558,609)

print(data3.cik.nunique()) # N companies - 11,110
print(data3.tag.nunique()) # N variables - 8,555
print(data3.memory_usage(index=True).sum()) # 9.1 Gb

# Add ticker column
ticker = data3['instance'].str.split('-').to_list()
ticker2 = []
for i in range(data3.shape[0]):
    ticker2.append(ticker[i][0])
data3['ticker'] = ''
data3['ticker'] = ticker2

data3.tag = data3.tag.apply(lambda x: x.upper())

# Summarise by variable and date (some values are split by contribution of investors and other dependent companies)
#data3['value2'] = data3.groupby(['adsh', 'cik', 'tag', 'qtrs', 'ddate'])['value'].transform('sum').round(2) # N obs - 63,334,962
data3 = data3[data3['coreg']=='']
#data3['value2'] = ''
#data3['value2'] = data3['value']
data3 = data3.drop(['adsh','ddate','ndate','uom','version','footnote','instance','coreg'],axis=1).drop_duplicates().reset_index(drop=True) # 
# Take the latest submitted values
#data3 = data3.reset_index(drop=True)
data4 = data3.reset_index()
data4.loc[data4['period'].isnull(),['period']] = pd.Timestamp('2020-06-30') # replace missing dates
data4 = data4.iloc[data4.groupby(['cik','date','tag','qtrs'])['period'].agg(pd.Series.idxmax)]
data3.to_pickle("./data3.pkl")

# Variables may be reported for multiple time periods / quarters
# Keep only most common combination of varaible-qtrs to reduce number of parameters
vars_qtrs_cnt = pd.DataFrame(data3.groupby(['tag','qtrs'])['value'].count().reset_index())
idx = vars_qtrs_cnt.groupby(['tag'])['value'].transform(max) == vars_qtrs_cnt['value']
var_qtr = vars_qtrs_cnt[idx]
#var_qtr.to_pickle("./var_qtr.pkl")

data4 =  pd.merge(data3,var_qtr.drop(['value'],axis=1),left_on=['tag','qtrs'],right_on=['tag','qtrs'],how='inner') # N obs - 40,648,284 (33,135,008)

print("Keep most common combination of varaible-qtrs")
print(data4.cik.nunique()) # N companies - 11,105 (11,090)
print(data4.tag.nunique()) # N variables - 8,555 (8,529)
print(data4.dtypes)
print(data4.memory_usage(index=True).sum()) # 6.5 Gb (3,3 Gb)

#data3 = data3.drop(['adsh','ddate','ndate','value','uom','version','footnote','instance','date'],axis=1).drop_duplicates().reset_index(drop=True) # 
#data3.to_pickle("./data3.pkl")
del [data3]

# Keep data collected on submission date
#data4 = data4[data4.date==data4.period] # N obs - 18,525,264 (15,983,076)
# Drop extra columns and duplicated values (after summarising the value)
#data4 = data4.drop(['adsh','ddate','qtrs','ndate','value','coreg','uom','version','footnote','instance','date'],axis=1).drop_duplicates().reset_index(drop=True) # 
data4 = data4.drop(['qtrs','period','ticker'],axis=1).drop_duplicates().reset_index(drop=True) # 
# for duplicated submissions (corrections) take maximum value
data4 = pd.DataFrame(data4.groupby(['cik','date','name','sic','Office','Industry Title','tag'])['value'].max().reset_index())  #  N obs - 16,053,642

print("Filter submission dates, drop extra columns")
print(data4.cik.nunique()) # N companies - 11,009 (11,092)
print(data4.tag.nunique()) # N variables - 8,413 (8,529)
print(data4.dtypes)
print(data4.memory_usage(index=True).sum()) # 1.5 Gb

# Select key variables and keep only those companies that have them populated
companies = data4[data4['tag'].isin(['ASSETS','NETINCOMELOSS','STOCKHOLDERSEQUITY'])].groupby(['cik', 'tag'])['value'].count().reset_index()
companies = companies.pivot(index='cik',columns='tag',values='value')
companies = companies.dropna().reset_index()
data4 = data4[data4['cik'].isin(companies.cik)] # N obs - 14,856,007 (14,725,812)

print("Filter companies with key variables populated")
print(data4.cik.nunique()) # N companies - 9,583 (9,588)
print(data4.tag.nunique()) # N variables - 8,350 (8,457)
print(data4.memory_usage(index=True).sum()) # 1.6 Gb

# Remove variables with low volume
vars_cnt = data4['tag'].value_counts()
vars_co_cnt = data4.groupby(['tag'])['cik'].nunique()
# Drop variables with less than 5,000 companies
vars_cnt_keep = vars_cnt[vars_co_cnt>5000].index
data5 = data4[data4['tag'].isin(vars_cnt_keep)] # N obs - 18,837,950
# Drop companies with less than 2 years of data
co_cnt = data5['cik'].value_counts()
co_period = data5.groupby(['cik'])['date'].nunique()
co_keep = co_cnt[co_period>=8].index
data5 = data5[data5['cik'].isin(co_keep)] # N obs - 5,936,933

print("Drop variables with low volume")
print(data5.cik.nunique()) # N companies - 7,540 (8,862)
print(data5.tag.nunique()) # N variables -54 (57)
print(data5.memory_usage(index=True).sum()) # 0.4 Gb


# !!! Some names and tickers are misspled or changed over time
# CIK may be associated with multiple company names through time


data_t = data5.pivot(index=['cik','date','name','sic','Office','Industry Title'],columns='tag',values='value').reset_index() # 

##### Save data
#####################################################

data5.to_pickle("./data5.pkl")
data_t.to_pickle("./data_t.pkl")


#data3 = data3.drop(['adsh','ddate','qtrs','ndate','value','coreg','uom','version','footnote','instance','date'],axis=1).drop_duplicates().reset_index(drop=True) # 
#data3.to_pickle("./data3.pkl")
data4.to_pickle("./data4.pkl")








