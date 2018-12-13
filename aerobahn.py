# -*- coding: utf-8 -*-
"""
Created on Wed Mar 28 16:51:50 2018

@author: 628066
"""

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime,timezone,timedelta
from dateutil import tz
import pickle
import os



def getdata(start,end):
    carrier={'AAL':'AA',
         'ENY':'MQ',
         'JIA':'OH',
         'RPA':'YX',
         'SKW':'OO'}
    link="http://aerobahnord.aa.com/DataDeliveryServlet/query/8f109dd41432179a392454ca267686d0/html/absolute/"+start+"T00:00:00.000-0500/"+end+"T23:59:00.000-0500"
    import requests
    x=requests.get(link, auth=('opsanalysis1', 'abc123')).text
    y=x.split('</tr>')
    col_name=y[0].split('<table>')
    col_name=col_name[1].replace('\n<th>','').replace('\n','').replace('<tr>','').split('</th>')
    y=y[1:]
    df=pd.DataFrame()
    for i in range(0,len(y)):
       t=pd.DataFrame(y[i].replace('\n<td>','').replace('\n','').replace('<tr>','').split('</td>')).transpose()
       df=df.append(t)
    df.columns=col_name
    df = df.iloc[:, :-1]
    df=df.loc[df['Operation']=='Arrival']
    df=df.loc[df['Carrier Group']=='American Airlines']
    df=df.loc[(df['Actual In']!='') & (df['Gate']!='') & (df['At Spot (inbound)']!='')& (df['Actual In']>=df['At Spot (inbound)'])&(df['Actual On']<=df['At Spot (inbound)'])]
    df['carrier']=df['Call Sign'].apply(lambda x: carrier[x[:3]])
    df['Actual In']=df['Actual In'].apply(lambda x:datetime.strptime(x, '%m/%d/%Y %H:%M:%S'))
    df['At Spot (inbound)']=df['At Spot (inbound)'].apply(lambda x:datetime.strptime(x, '%m/%d/%Y %H:%M:%S'))
    df['time diff']=df['Actual In']-df['At Spot (inbound)']
    df['time diff']=df['time diff'].apply(lambda x: x.seconds/60)
    df['Event Time']=df['Event Time'].apply(lambda x:datetime.strptime(x, '%m/%d/%Y %H:%M:%S'))
    df['Event Date']=df['Event Time'].apply(lambda x:x.replace(tzinfo=timezone.utc).astimezone(tz.gettz('America/Chicago')).date())
    
    return(df)


week="2018-W13"
df=pd.DataFrame()
x=datetime.strptime(week + '-1', "%Y-W%W-%w")
y=datetime.strptime(week + '-0', "%Y-W%W-%w")
x=x.strftime("%Y-%m-%d")
y=y.strftime("%Y-%m-%d")
df=df.append(getdata(x,y))
with open("%s"%week,"wb") as pickle_out:
    pickle.dump(df,pickle_out,protocol=4)
#df=pd.read_excel('C:\\Users\\628066\\Desktop\\AEROBAHN.xlsx',sheetname='AA ORD Spot Data')
#df=df.loc[df['Operation']=='Arrival']
#df=df.dropna(subset=['Actual In'])
#df['time difference']=df['time difference'].apply(lambda x: -100 if x<-1 else(0 if x<0 else x))
#df=df.loc[df['time difference']>=0]
#df['month']=df['Event Time'].apply(lambda x: x.month)
#df['day']=df['Event Time'].apply(lambda x: x.day)


data=pd.DataFrame()
for files in os.listdir(os.getcwd()):
    if files.startswith(('2017-W','2018-W')):
        with open("%s"%files,"rb") as pickle_in:
            data=data.append(pickle.load(pickle_in))

#data=data.loc[data['Gate']!='']
data.to_csv('ordaerobahn.csv',index=False)



gate_median=pd.pivot_table(data,index='Gate',values='time diff',aggfunc=np.median).reset_index().rename(columns={'time diff':'gate_md'})
def mm(df):
    x=np.percentile(df,25)
    y=np.percentile(df,50)
    new_df=df[(df>=x)&(df<=y)]
    if len(new_df)>0:
        re=np.mean(new_df)
    else: 
        re=np.mean(df)
    return(re)


f={'time diff':{'n':len,'mean':np.mean,'median':np.median,'25th':lambda x:np.percentile(x,25),'75th':lambda y:np.percentile(y,75),'ct_mean':mm}}
stats=data.groupby(['Gate','Spot']).agg(f).reset_index()
stats.columns=['Gate','Spot','count','mean','median','25th','75th','ct_mean']
stats=pd.merge(stats,gate_median,how='outer',on='Gate')
stats.to_csv('ordstats.csv',index=False)
test=getdata('2018-06-11','2018-06-17')
test.to_csv('//10.76.40.194/Tableau_Prd/Default/OperAna/test.csv',index=False)


plt.hist(df['time diff'],bins=100)

his,bin_edges=np.histogram(df['time difference'],bin)
fig,ax=plt.subplots()
ax.set_xticks([i for i,j in enumerate(his)])
ax.set_xticklabels(['{} - {}'.format(bin[i],bin[i+1]) for i,j in enumerate(his)])

bin=[0,5,9,14,19,100000000000]
#x=df['CARRIER'].unique()
x=[1,2,3]
dic={1:'Jan',2:'Feb',3:'Mar'}
sns.set_style("dark")
fig,ax=plt.subplots(nrows=1,ncols=3,figsize=(15,5))
t=np.array([0,0,0,0,0])
for i in range(0,3):
        
        y=df.loc[(df['CARRIER']=='OO') & (df['month']==x[i])]
        
     
        
        row=ax[i]
        his,bin_edges=np.histogram(y['time difference'],bin)

        row.bar(range(len(his)),his,label="ops")
        row.set_xticks([i for i,j in enumerate(his)])
        row.set_xticklabels(['0-4','5-9','10-14','15-19','20+'])
        row.set_title(dic[x[i]])
        row.set_xlabel('mins')
        handle1, label1 = row.get_legend_handles_labels()
        #row.legend(handle1,label1,loc='upper left')
        #row.set_ylabel('# of ops')
        pct=his/sum(his)*100
        cumulative=np.cumsum(his)/sum(his)*100
        row2=row.twinx()
        row2.plot(np.arange(0,5,1),cumulative,c='red',label='cumulative',marker='o')
        row2.set_ylim([85,100])
        handle2, label2 = row2.get_legend_handles_labels()

        pct=his/sum(his)*100
        cumulative=np.cumsum(his)/sum(his)*100
        t=np.vstack((t,pct))
        
        #row2.legend(handle2,label2)
plt.suptitle('OO Time between Spot and Gate 2018YTD')

plt.show() 
t=pd.DataFrame(t).iloc[1:]
        
        
    




