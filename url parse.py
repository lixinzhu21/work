# -*- coding: utf-8 -*-
"""
Created on Wed Dec 19 09:49:14 2018

@author: 628066
"""


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime,timezone,timedelta

df=pd.read_csv('Y:\\OA$\\Xinzhu\\DFW_GATE_to_Menglu.csv')
df=df.loc[df['carrier']=='AA']
df['Event Date']=df['Event Date'].apply(lambda x:datetime.strptime(x,"%Y-%m-%d"))
df=df.loc[(df['Event Date']>=datetime(2018,6,7)) & (df['Event Date']<datetime(2018,8,21)) ]
df['At Spot (inbound)']=df['At Spot (inbound)'].apply(lambda x:pd.Timestamp(x))
df['hour']=df['At Spot (inbound)'].apply(lambda x:x.hour)
f={'time diff':{'n':len,'mean':np.mean,'median':np.median,'25th':lambda x:np.percentile(x,25),'75th':lambda y:np.percentile(y,75),'90th':lambda x:np.percentile(x,90),'95th':lambda x:np.percentile(x,95)}}
stats=df.groupby(['hour']).agg(f).reset_index()


x="https://www.booking.com/searchresults.html?label=gen173nr-1FCAEoggI46AdIM1gEaLACiAEBmAExuAEGyAEM2AEB6AEB-AECiAIBqAID;sid=4e5d1c3f3b053d2d444569b1fcde4164;checkin_month=1&checkin_monthday=23&checkin_year=2019&checkout_month=1&checkout_monthday=24&checkout_year=2019&class_interval=1&dest_id=3791&dest_type=region&dtdisc=0&from_sf=1&group_adults=2&group_children=0&inac=0&index_postcard=0&label_click=undef&no_rooms=1&offset=0&postcard=0&raw_dest_type=region&room1=A%2CA&sb_price_type=total&shw_aparth=1&slp_r_match=0&src=index&src_elem=sb&ss=Interlaken&ss_all=0&ssb=empty&sshis=0&ssne=Interlaken&ssne_untouched=Interlaken&"
n=x.find("checkin")
x=x[n:]
temp=x.split("&")
para={}
for k in temp:
    y=k.split('=')
    if len(y)>=2:
        p=y[0]
        v=y[1]
        para[p]=v
        
l=[]
l.append(para)
pd.DataFrame(l)


    