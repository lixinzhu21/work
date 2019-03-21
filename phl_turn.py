# -*- coding: utf-8 -*-
"""
Created on Tue Mar 19 15:37:59 2019

@author: 628066
"""

import pandas as pd
import numpy as np
import math 
df=pd.read_excel('C:\\Users\\628066\\Desktop\\TURN.xlsx',skiprows=10,header=None,index_col=None,sheet_name='AYR Checklist (ATW)',usecols=[1,2,7,8,9,10])
df.columns=['activity','department','flt_1','flt_2','flt_3','flt_4']
df=df.loc[df['activity'].notnull()]
activity_dict=dict(zip(df['activity'],df['department']))
df=df.drop(['department'],axis=1)

def tm(df):
    return(df.apply(lambda x:'{0:0>4}'.format(int(x)) if math.isnan(x)==0 else 0))  #standardize tim e
df['flt_1'],df['flt_2']=list(map(tm,[df['flt_1'],df['flt_2']]))
