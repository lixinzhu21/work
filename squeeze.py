# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import pandas as pd
import numpy as np
import math
from pandas import ExcelWriter 


def squeeze_fx(filename,sheet_name,duration='all',variable=[]):
    raw=pd.read_excel(filename, sheetname=sheet_name)
    raw['DLY']=raw['PCT_DLY']*raw['TOT_OPS']
    if duration=="all":
        list1=['Y_DATE','MTH_NUM']+variable
        list2=['FX_GROUP']+variable
        new1=pd.pivot_table(raw,values=['TOT_OPS'],index=list1,aggfunc=np.max).sum()
        new2=pd.pivot_table(raw,values=['DLY'],index=list2,aggfunc=np.sum)/float(new1)
        
    elif duration=='Q':
        raw['QT']=raw['MTH_NUM'].apply(lambda x:math.floor(x/3.0001)+1)
        list1=['Y_DATE','QT','MTH_NUM']+variable
        list2=['Y_DATE','QT']+variable
        list3=['Y_DATE','QT','FX_GROUP']+variable
        new1=pd.pivot_table(raw,values=['TOT_OPS'],index=list1,aggfunc=np.max)
        new1=new1.reset_index()
        new1=pd.pivot_table(new1,values=['TOT_OPS'],index=list2,aggfunc=np.sum)
        new2=pd.pivot_table(raw,values=['DLY'],index=list3,aggfunc=np.sum)
        new2=new2.reset_index(['FX_GROUP'])
        new2=pd.merge(new1,new2,left_index=True,right_index=True)
        new2['NEW_PCT']=new2['DLY']/new2['TOT_OPS']
        
    elif duration=='Y':
        list1=['Y_DATE','MTH_NUM']+variable
        list2=['Y_DATE']+variable
        list3=['Y_DATE','FX_GROUP']+variable
        new1=pd.pivot_table(raw,values=['TOT_OPS'],index=list1,aggfunc=np.max)
        new1=new1.reset_index()
        new1=pd.pivot_table(new1,values=['TOT_OPS'],index=list2,aggfunc=np.sum)
        new2=pd.pivot_table(raw,values=['DLY'],index=list3,aggfunc=np.sum)
        new2=new2.reset_index(['FX_GROUP'])
        new2=pd.merge(new1,new2,left_index=True,right_index=True)
        new2['NEW_PCT']=new2['DLY']/new2['TOT_OPS']
        
    else:
        new2="wrong,check!!!!"
    return(new2)
   



filename='C:\\Users\\628066\\Desktop\\OO ORD FOLLOWUP ANALYSIS.xlsx'
sheet_name='WEATHER_FX_NOTRANS'
df=squeeze_fx(filename,sheet_name,duration='Q',variable=['CAT'])
df=df.reset_index()
writer = pd.ExcelWriter(filename, engine='openpyxl')
writer.book=load_workbook(filename)
df.to_excel(writer,sheet_name,index=False)
writer.save()

