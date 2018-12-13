# -*- coding: utf-8 -*-
"""
Created on Mon Jul  2 14:35:18 2018

@author: 628066
"""

import pandas as pd
import numpy as np
from datetime import datetime,timedelta


ots=pd.read_excel('Y:\\OA$\\Xinzhu\\2019 Spares\\OTS Data\\MQ OTS Events By Date Range.xlsx',skiprows=1)
#ots['start']=ots['OTS_DATETIME'].apply(lambda x:x.hour)
ots=ots.loc[ots['RGO_REASON_CODE']!='S']
ots=ots.dropna(subset=['RTS_DATETIME','OTS_DATETIME'])
ots['start']=ots['OTS_DATETIME'].apply(lambda x:x.replace(microsecond=0,second=0,minute=0))
ots['end']=ots['RTS_DATETIME'].apply(lambda x:x.replace(microsecond=0,second=0,minute=0)+timedelta(hours=1))
ots['dur']=ots['end']-ots['start']
ots['dur']=ots['dur'].apply(lambda x:x.days*24+x.seconds/3600)

df_new=pd.DataFrame()
for i in range(len(ots)):
    df=ots.iloc[i:i+1]
    reps=int(df['dur'].iloc[0])
    start=df['start'].iloc[0]
    df=df.loc[np.repeat(df.index.values,reps)].reset_index()
    for j in range(reps):
        df['start'].iloc[j]=start+timedelta(hours=j)
    df=df.reset_index()
    df_new=df_new.append(df)


# df.iat[0,0] --first row, first column value
    
df_new['date']=df_new['start'].apply(lambda x:x.date())
df_new['hour']=df_new['start'].apply(lambda x:x.hour)
df=df_new[['A/C','STATION_CODE','RGO_REASON_CODE','date','hour','Fleet Code']]
df.columns=['AC','STA','CDE','sitDate','HrByHr','FLEET']

filename='Y:\\OA$\\Xinzhu\\2019 Spares\\OTS Data\\MQ OTS Events By Date Range.xlsx'
sheet_name='clean'
writer = pd.ExcelWriter(filename, engine='openpyxl')
df.to_excel(writer,sheet_name,index=False)
writer.save()
