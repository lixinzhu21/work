# -*- coding: utf-8 -*-
"""
Created on Sat Mar 17 16:39:54 2018

@author: 628066
"""

import pandas as pd
import numpy as np
import seaborn as sns
sns.set_style("darkgrid")
import matplotlib.pyplot as plt

df=pd.read_excel('C:\\Users\\628066\\Desktop\\dca.xlsx',sheetname='ALL')
code=pd.read_excel('C:\\Users\\628066\\Desktop\\dca.xlsx',sheetname='DLY_CD')
code['DELAY_REASON_CD']=code['DELAY_REASON_CD'].apply(lambda x:x.replace(" ",""))
goal=pd.read_excel('C:\\Users\\628066\\Desktop\\dca.xlsx',sheetname='GOAL')
goal=goal.set_index(['GOAL_TYPE','MTH_NUM','Y_DATE','METRIC'])['GOAL'].unstack().reset_index()


df['AIRLINE']=df['AIRLINE'].apply(lambda x:'OH' if x=='16' else ('PT' if x=='17' else x))   
df=df.loc[df['CANCELED']==0]
variable=['Y_DATE','MTH_NUM','M_DATE','AIRLINE_TYPE','PAD_TYPE']


df['PAD_TYPE']=df['DPT_GATE'].apply(lambda x:'PAD' if x=='35X' else 'NON-PAD')


def funcalc(df,station,variable=[],RS=0):
    if RS!=0:
        df=df.loc[df['RS_IND']==1]
    else:
        df=df
    
    df['AIRLINE_TYPE']=df['AIRLINE'].apply(lambda x:'ML' if x in (['AA','US']) else 'RG')
    origin=df.loc[df['SKD_ORIG']==station]
    dest=df.loc[df['SKD_DEST']==station]
    fx=pd.DataFrame()
    for i in range(1,9):
        origin['DLY_CD']=origin['DLY_CD'+str(i)]
        origin['MIN']=origin['DLY_MIN'+str(i)]/origin['DPT_VAR']
        origin['CHARGE']=origin['MIN'].apply(lambda x: min(max(x,0),1))
        temp=origin[['DLY_CD','CHARGE']+variable]
        temp=temp.dropna()
        temp=temp.groupby(['DLY_CD']+variable).agg({'CHARGE':'sum'}).reset_index()
        if len(fx)==0:
            fx=temp
        else:
            fx=pd.merge(fx,temp,how='outer',on=['DLY_CD']+variable)
    fx=fx.set_index(['DLY_CD']+variable)
    fx_agg=fx.sum(axis=1).reset_index().rename(columns={0:'CHARGE'})
    if len(variable)!=0:
        tot=origin.groupby(variable).agg({'ACT_OPS':'sum'}).reset_index().rename(columns={'ACT_OPS':'TOT'})
        fx_agg=pd.merge(fx_agg,tot,how='outer',on=variable)
    else:
        fx_agg['TOT']=origin['ACT_OPS'].sum()
    fx_agg['PCT']=fx_agg['CHARGE']/fx_agg['TOT']*100
    fx=pd.merge(fx_agg,code,how='left',left_on=['DLY_CD'],right_on=['DELAY_REASON_CD'])
    fx=fx.groupby(['DELAY_REASON_GROUP_NM']+variable).agg({'CHARGE':'sum','TOT':'max'}).reset_index()
    fx['PCT']=fx['CHARGE']/fx['TOT']*100
    fx=fx.set_index(variable+['TOT','DELAY_REASON_GROUP_NM'])['PCT'].unstack().reset_index()
    
    pfm=pd.pivot_table(origin,index=variable,values=['D0','T0','RS0','B0'],aggfunc=np.mean).reset_index().rename(columns={'B0':'OUT_B0'})
    pfm2=pd.pivot_table(dest,index=variable,values=['A0','D0','B0'],aggfunc=np.mean).reset_index().rename(columns={'B0':'IN_B0','D0':'IN_D0'})
    pfm=pd.merge(pfm,pfm2,how='outer',on=variable)
    pfm=pd.merge(pfm,goal,how='left',left_on=['Y_DATE','MTH_NUM','AIRLINE_TYPE'],right_on=['Y_DATE','MTH_NUM','GOAL_TYPE'])
    
    a={'metric':pfm,'fx_dly_cd':fx_agg,'fx':fx}
    return(a)
        
 
a=funcalc(df,'DCA',variable)
sns.factorplot(x='MTH_NUM',y='D0_x',col='PAD_TYPE',data=a['metric'],kind='point')
sns.pointplot('MTH_NUM','D0_x',hue='PAD_TYPE',data=a['metric'],palette='Set2')

def stacked(xlabel,**kwargs):

     data=kwargs.pop("data")
     data=data[variable+[ 'CUSTOMER SERVICE/AIRPORT SERVICE','MAINTENANCE/DAMAGE',
       'FLIGHT CREW/CREW SCHEDULING', 'OPERATIONS/LOAD PLANNING','ATC/WEATHER', 'MISCELLANEOUS',
       'LATE ARRIVING EQUIPMENT'
         ] ]
     data.set_index(['Y_DATE','MTH_NUM']).plot(kind='bar',stacked=True,ax=plt.gca())
     plt.xticks(rotation=0)
     plt.xlabel(xlabel)

     
   
          
x=sns.FacetGrid(a['fx'],col='PAD_TYPE')
x.map_dataframe(stacked,'time')
#x.axes[0,0].set_xlabel('time')
#x.axes[0,1].set_xlabel('time')
#x.axes[0,0].set_ylabel('%')
x.fig.legend(('CS','MT','FC','OP','ATWX','MI','EQ'),loc='best',ncol=7)



