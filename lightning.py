# -*- coding: utf-8 -*-
"""
Created on Tue Dec 11 15:28:01 2018

@author: 628066
"""

import pandas as pd
from datetime import datetime,timedelta
import numpy as np
import teradata
import pickle
import matplotlib.pyplot as plt
import seaborn as sns
 
col_names=['Date (YYYY-MM-DD)','Time in UTC (hh:mm:ss)','Latitude','Longitude','Polarity (Positive or Negative) and Peak Current (kiloamps)',
           'Lightning type (C=Cloud ; G=Cloud-to-Ground)','Radial distance from airport centerpoint (miles)']

f=open('C:\\Users\\628066\\Desktop\\mia.txt','r').read()
f=f.replace('mi','').split()
f=np.array(f).reshape(int(len(f)/7),7)   
df=pd.DataFrame(f)
df.columns=col_names
df['Date (YYYY-MM-DD)']=df['Date (YYYY-MM-DD)'].apply(lambda x:datetime.strptime(x,'%Y-%m-%d'))
df['Time in UTC (hh:mm:ss)']=df['Time in UTC (hh:mm:ss)'].apply(lambda x:x.split('.')[0])
df['Time in UTC (hh:mm:ss)']=df['Time in UTC (hh:mm:ss)'].apply(lambda x:datetime.strptime(x, '%H:%M:%S'))
def add_time(x):
    return(x[0]+timedelta(hours=x[1].hour)+timedelta(minutes=x[1].minute))
df['time']=df[['Date (YYYY-MM-DD)','Time in UTC (hh:mm:ss)']].apply(add_time,axis=1)

with open("mia","wb") as pickle_out:
    pickle.dump(df,pickle_out,protocol=4)
with open("clt","rb") as pickle_in:
    df=pickle.load(pickle_in)



df['Radial distance from airport centerpoint (miles)']=pd.to_numeric(df['Radial distance from airport centerpoint (miles)'])
df=df.sort_values(by=['time'])
def calc(df,radius,types):
    df_new=df.loc[(df['Radial distance from airport centerpoint (miles)']<=radius)]
    df_new['filter']=df_new['Lightning type (C=Cloud ; G=Cloud-to-Ground)'].apply(lambda x:'y' if x in types else 'n')
    df_new=df_new.loc[df_new['filter']=='y']
    start=start_new=df_new['time'].iloc[0]
    df_new=df_new.append({'time':start+timedelta(days=100)},ignore_index=True)
    result=pd.DataFrame()
    for index,row in df_new.iterrows():
        if row['time']-start_new>timedelta(minutes=10):
            end=start_new+timedelta(minutes=10)
            result=result.append({'start':start,'end':end},ignore_index=True)
            start_new=row['time']
            start=row['time']
        else:
            start_new=row['time']
    result=result[['start','end']]
    result['length']=(result['end']-result['start'])/timedelta(minutes=1)
    result['year']=result['start'].apply(lambda x:x.year)
    result['month']=result['start'].apply(lambda x:x.month)
    result['hour']=result['start'].apply(lambda x:x.hour)
    return(result)





username,password='628066','Movie678'
udaExec = teradata.UdaExec (appName="test", version="1.0",logConsole=False)  #good for ops_flight_leg and OAG
session=udaExec.connect(method="odbc",dsn="Terdata PROD 01", 
                        username=username,password=password, autocommit=True,transactionMode="Teradata")
query="""
select SKD_FIRST_LEG_DPT_DATE,SKD_OUT,ACT_OUT,DPT_VAR,SKD_OUT_DATE_GMT,SKD_OUT_GMT,SKD_DPT_TMS,ORIG_IDL_GMT_VAR
from PROD_FLIGHT_OPS_COMBINED_VW.OPS_FLIGHT_LEG
WHERE OP_STATUS NOT ='G' AND OPS_ANALYSIS_IND=1 
and SKD_OPS=1
and SKD_ORIG=?
AND SKD_FIRST_LEG_DPT_DATE between ? and ?
"""
ops=pd.read_sql_query(query,session,params=["DFW","2013-09-14","2017-09-16"])
ops['year']=ops['SKD_OUT_DATE_GMT'].apply(lambda x:x.year)
ops['month']=ops['SKD_OUT_DATE_GMT'].apply(lambda x:x.month)
tot_ops=ops.groupby(['year','month']).size().reset_index(name='ops')
ops['SKD_OUT_GMT']=ops['SKD_OUT_GMT'].apply(lambda x:None if x is None else datetime.strptime(x, '%H:%M').time())
def add_utc(x):
    if x[1] is not None:
        return(pd.datetime.combine(x[0],x[1]))
    elif np.isnan(x[3])==0:
        return(x[2]+timedelta(hours=x[3]))
ops['gmt_out']=ops[['SKD_OUT_DATE_GMT','SKD_OUT_GMT','SKD_DPT_TMS','ORIG_IDL_GMT_VAR']].apply(add_utc,axis=1)
ops=ops.dropna(subset=['gmt_out'])
ncol=ops.shape[1]
#result['local_start']=result['start']-gap_utc    
#result['local_end']=result['end']-gap_utc   

    
ops=ops.iloc[:,:ncol]
result=calc(df,5,['G'])
for index,row in result.iterrows():
    ops['filter_'+str(index)]=np.where((ops['gmt_out']>=row['start'])&(ops['gmt_out']<=row['end']),1,0)
ops['filter']=ops.iloc[:,ncol:].max(axis=1)   


impact=ops.groupby(['year','month']).agg({'filter':sum}).reset_index()
tot_ops=pd.merge(tot_ops,impact, how='outer',left_on=['year','month'],right_on=['year','month'])





result_stat=pd.DataFrame({'year':[],'month':[]})

result=calc(df,3,['G'])
new=result.groupby(['year','month']).agg({'length':[sum,len]}).reset_index()
new.columns=['year','month','minutes','time']
result_stat=pd.merge(result_stat,new, how='outer',left_on=['year','month'],right_on=['year','month'])


result_stat=result_stat.sort_values(by=['year','month'])

result=calc(df,3,['G'])
result['type']='3G'
result2=calc(df,5,['G','C'])
result2['type']='5Gc'
result_all=result.append(result2)

fig = plt.figure(figsize=(20, 15))
for i in range(1,13):
    ax=fig.add_subplot(4,3,i)
    sns.countplot(x='hour',data=result_all.loc[result_all['month']==i],hue='type',hue_order=['5Gc','3G'])
    plt.title("month: %i" %i,fontsize=12)
    plt.xlabel('hour', fontsize=8)
    plt.tight_layout()
fig.suptitle("Count of ramp closure by month and hour")
fig.subplots_adjust(top=0.93)
plt.savefig('count.png')
    

fig = plt.figure(figsize=(20, 15))
for i in range(1,13):
    ax=fig.add_subplot(4,3,i)
    sns.barplot(x='hour',y='length',data=result_all.loc[result_all['month']==i],hue='type',hue_order=['5Gc','3G'],ci=None,estimator=sum)
    plt.title("month: %i" %i,fontsize=12)
    plt.xlabel('hour', fontsize=8)
    plt.tight_layout()
fig.suptitle("Total length of ramp closure by month and hour")
fig.subplots_adjust(top=0.93)
plt.savefig("length.png")