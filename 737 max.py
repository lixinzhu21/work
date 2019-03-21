# -*- coding: utf-8 -*-
"""
Created on Tue Mar 19 16:44:33 2019

@author: 628066
"""

import pandas as pd
import numpy as np 
import math
import teradata
from datetime import datetime,timezone,timedelta,date


tim=pd.read_excel('C:\\Users\\628066\\Desktop\\AA UA WN 737 MAX Mar 14 to Mar 31.xlsx',parse_dates=['DATE'])

username,password='628066','Movie789'
udaExec = teradata.UdaExec (appName="test", version="1.0",logConsole=False)  #good for ops_flight_leg and OAG
session=udaExec.connect(method="odbc",dsn="Terdata PROD 01", 
                        username=username,password=password, autocommit=True,transactionMode="Teradata")
query="""
SELECT	OPERAT_CARRIER_CD, OPERAT_FLIGHT_NBR, SCHD_DEP_DT, SCHD_DEP_AIRPRT_IATA_CD,		ARVL_AIRPRT_IATA_CD,
		SCHD_EQUP_TYPE_CD,
		ACTL_EQUP_TYPE_CD,
		EQUIP_CHANGE_IND,
		OPERAT_AIRCFT_ID,
		OPERAT_AIRCFT_CHANGE_IND,
		SCHD_LEG_ARVL_TMS,
		ACTL_LEG_ARVL_TMS,
		ARVL_DELAY_STATUS_CD,
		ARVL_DELAY_DETL_CD,
		SCHD_LEG_DEP_TMS,
		ACTL_LEG_DEP_TMS,
		DEP_DELAY_STATUS_CD,
		DEP_DELAY_DETL_CD



FROM	PROD_AIRPORT_OPERATIONS_VWS.OAG_FLIGHT_STATUS
WHERE OPERAT_CARRIER_CD IN ('AA','UA','WN')
AND SCHD_DEP_DT BETWEEN ? AND ?
AND CURR_STATUS_IND='Y'

"""

oag=pd.read_sql_query(query,session,params=["2019-03-14","2019-03-19"])
oag['SCHD_DEP_DT']=oag['SCHD_LEG_DEP_TMS'].apply(lambda x:x.date())
oag=oag.sort_values(by=['SCHD_DEP_DT','OPERAT_CARRIER_CD','OPERAT_FLIGHT_NBR'],ascending=True).reset_index()
oag['OPERAT_FLIGHT_NBR']=oag['OPERAT_FLIGHT_NBR'].apply(lambda x:x[1:] if x.find('0')==0 else x)
oag['OPERAT_FLIGHT_NBR']=oag['OPERAT_FLIGHT_NBR'].apply(lambda x:x[1:] if x.find('0')==0 else x)
oag['OPERAT_FLIGHT_NBR']=oag['OPERAT_FLIGHT_NBR'].apply(lambda x:x.strip())
tim=tim.loc[tim['DATE']<=date(2019, 3, 19)]
tim['DATE']=tim['DATE'].apply(lambda x:x.date())
tim['FLT_NUM']=tim['FLT_NUM'].apply(lambda x:str(x))


final=pd.merge(tim,oag,how='left',left_on=['DATE','AIRLINE','FLT_NUM','ORIG','DEST'],right_on=['SCHD_DEP_DT','OPERAT_CARRIER_CD','OPERAT_FLIGHT_NBR','SCHD_DEP_AIRPRT_IATA_CD','ARVL_AIRPRT_IATA_CD'])
final['DEP_DELAY_STATUS_CD']=np.where(final['DEP_DELAY_STATUS_CD'].isnull(),'delete',final['DEP_DELAY_STATUS_CD'])
final['status']=final['DEP_DELAY_STATUS_CD'].apply(lambda x: 'CX' if x=='CX   ' else('delete' if x=='delete' else 'OP'))





x=final.groupby(['DATE','AIRLINE','status'])['DATE'].agg('count').unstack().fillna(0).reset_index()
#y=final.groupby(['DATE','AIRLINE'])['delete'].agg('sum')
#x=x.join(y).reset_index()
