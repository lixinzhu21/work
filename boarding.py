# -*- coding: utf-8 -*-
"""
Created on Wed Apr 17 17:14:26 2019

@author: 628066
"""
import teradata
import pandas as pd

username,password='MOSSASOPAAPP10','WLsNiXJ4'
udaExec = teradata.UdaExec (appName="test", version="1.0",logConsole=False) 
session=udaExec.connect(method="odbc",system='edtdpAP1', username=username,password=password, autocommit=True,transactionMode="Teradata")

query="""
SELECT A.*,LF,SOB,EOB,D0,DPT_VAR
FROM 
(SELECT SCHD_LEG_DEP_DT,FLT_NUM,SKD_DEST,CHECKIN_TO_TARGET,PAX_TRAVEL_TYPE_CD,
Count(*) AS NUM
FROM PROD_FATSYS_SNBX_DB.PAX_CHECKIN_LIST
WHERE SKD_ORIG='DFW'
AND ACT_FLEET='321'
AND SCHD_LEG_DEP_DT BETWEEN '2019-03-01' AND '2019-03-31'
AND SKD_ORIG_ENREGION=11 AND SKD_DEST_ENREGION=11
GROUP BY SCHD_LEG_DEP_DT,FLT_NUM,SKD_DEST,CHECKIN_TO_TARGET,PAX_TRAVEL_TYPE_CD
) AS A 
JOIN
(SELECT SCHD_LEG_DEP_DT,FLT_NUM,SKD_DEST,
Sum(CASE WHEN PAX_CHECKIN_TMS<=TARGET_TMS-INTERVAL '35' MINUTE THEN 1 ELSE 0 END) AS SOB,
Sum(CASE WHEN PAX_CHECKIN_TMS>TARGET_TMS-INTERVAL '10' MINUTE THEN 1 ELSE 0 END) AS EOB,
Avg(LF) AS LF,
AVG(D0) AS D0,
AVG(DPT_VAR) AS DPT_VAR
FROM PROD_FATSYS_SNBX_DB.PAX_CHECKIN_LIST
WHERE SKD_ORIG='DFW'
AND ACT_FLEET='321'
AND SCHD_LEG_DEP_DT BETWEEN '2019-03-01' AND '2019-03-31'
AND SKD_ORIG_ENREGION=11 AND SKD_DEST_ENREGION=11
GROUP BY SCHD_LEG_DEP_DT,FLT_NUM,SKD_DEST
) AS B
ON A.SCHD_LEG_DEP_DT=B.SCHD_LEG_DEP_DT
AND A.FLT_NUM=B.FLT_NUM
AND A.SKD_DEST=B.SKD_DEST
WHERE SOB>0 AND DPT_VAR<60
"""

df=pd.read_sql_query(query,session)

# missing value for pax type, 2% of total pax
df[pd.isnull(df['PAX_TRAVEL_TYPE_CD'])]
df[~df.PAX_TRAVEL_TYPE_CD.isin (['E','F','P','S'])]['NUM'].sum()
df=df.dropna(subset=['PAX_TRAVEL_TYPE_CD'])


import numpy as np
df['EOB_IND']=np.where(df.EOB>0,'N','Y')

##check abnormal flights,start on time, end too late
temp=df[df.CHECKIN_TO_TARGET<-30]
check1=pd.DataFrame(temp.groupby(['SCHD_LEG_DEP_DT','FLT_NUM','SKD_DEST']).NUM.sum()).reset_index()
check1=check1[check1.NUM>20]
#51 flights,2721 flights total

##start too early 
temp2=df[df.CHECKIN_TO_TARGET>60]
check2=pd.DataFrame(temp2.groupby(['SCHD_LEG_DEP_DT','FLT_NUM','SKD_DEST']).NUM.sum()).reset_index()
check2=check2[check2.NUM>20]
#47 flights

check=pd.concat([check1,check2],axis=0)
check=check.drop(['NUM'],axis=1)
check['find']='Y'

df=df.merge(check,how='left',left_on=['SCHD_LEG_DEP_DT','FLT_NUM','SKD_DEST'],right_on=['SCHD_LEG_DEP_DT','FLT_NUM','SKD_DEST'])
df=df[pd.isnull(df.find)]
df=df.drop(['find'],axis=1)

#df.groupby(['CHECKIN_TO_TARGET','PAX_TRAVEL_TYPE_CD']).NUM.sum().unstack().fillna(0).plot(kind='bar',stacked=True)
x=pd.DataFrame(df.groupby(['EOB_IND','CHECKIN_TO_TARGET','PAX_TRAVEL_TYPE_CD']).NUM.sum().unstack().fillna(0)).reset_index()
x=x[(x['CHECKIN_TO_TARGET']>=-10)&(x['CHECKIN_TO_TARGET']<=40)]
x['CHECKIN_TO_TARGET']=x['CHECKIN_TO_TARGET'].astype(int)

import seaborn as sns
import matplotlib.pyplot as plt

def stack(*args,**kwargs):  
    df=kwargs.pop('data')
    df.drop(['EOB_IND'],axis=1)
    ax=df.set_index(['CHECKIN_TO_TARGET']).plot(kind='bar',stacked=True,ax=plt.gca())
    ax.invert_xaxis()
 
p=sns.FacetGrid(x,col='EOB_IND',sharex=False)
p.map_dataframe(stack) 
p.axes[0,0].set_ylabel('total pax boarding')
p.axes[0,0].set_xlabel('Minute to Target time')
p.axes[0,1].set_xlabel('Minute to Target time') 
p.fig.legend(('E','F','P','S'),loc='best')
p.fig.suptitle('DFW 321 March 2019 flights start boarding ontime')


def lf(x):
    if x<75:
       return 1
    elif x<80:
       return 2
    elif x<85:
        return 3
    elif x<90:
        return 4
    elif x<95:
        return 5
    elif x<100:
        return 6
    else:
        return 7

df['LF_bucket']=df['LF'].apply(lf)
ldic=dict({1:'<75',2:'75-79',3:'80-84',4:'85-89',5:'90-94',6:'95-99',7:'99+'})


y=pd.DataFrame(df.groupby(['EOB_IND','LF_bucket','CHECKIN_TO_TARGET','PAX_TRAVEL_TYPE_CD']).NUM.sum().unstack().fillna(0)).reset_index()
y=y[(y['CHECKIN_TO_TARGET']>=-10)&(y['CHECKIN_TO_TARGET']<=40)&(y['EOB_IND']=='N')]
y['CHECKIN_TO_TARGET']=y['CHECKIN_TO_TARGET'].astype(int)

f=pd.DataFrame(df[df['EOB_IND']=='N'].groupby(['LF_bucket','SCHD_LEG_DEP_DT','FLT_NUM','SKD_DEST']).NUM.sum()).reset_index().groupby(['LF_bucket']).NUM.count()
fdic=dict(zip(f.keys(),f))

plt.style.use('ggplot')
fig=plt.figure()
for i in range(1,8):
    plt.subplot(4,2,i)
    y[y['LF_bucket']==i].drop(['EOB_IND','LF_bucket'],axis=1).set_index(['CHECKIN_TO_TARGET']).div(fdic[i]).plot(kind='bar',stacked=True,ax=plt.gca(),title='LF:{}'.format(ldic[i]))
    ax=plt.gca()
    ax.invert_xaxis()
    ax.set_xlabel('Minute to Target time')
    ax.set_ylabel('avg pax')
    #ax.set_xlim([-10,45])
fig.suptitle('DFW 321 March 2019 flights SOB=Y, EOB=N')
#plt.tight_layout()
#plt.subplots_adjust(left=None,bottom=None,right=None,top=None,wspace=None,hspace=None)
