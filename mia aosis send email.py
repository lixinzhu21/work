# -*- coding: utf-8 -*-
"""
Created on Mon Apr  8 17:49:00 2019

@author: 628066
"""

from os import listdir
import datetime
import teradata
import pandas as pd 

date_list=listdir('C:\\Users\\628066\\Desktop\\oasis')
if len(date_list)==0:
    start_date=datetime.date(2019,4,1)
else:
     recent_date=max(list(map(lambda x:x.replace('.xlsx','').replace('.csv','').split(' ')[-1],date_list)))
     start_date=datetime.datetime.strptime(recent_date, '%Y-%m-%d').date()+datetime.timedelta(days=1)





query="""
WITH M AS 
(SELECT 
SCHD_FIRST_LEG_DEP_LCL_DT,
OPERAT_FLIGHT_NBR,
SCHD_LEG_DEP_AIRPRT_IATA_CD,
SCHD_LEG_ARVL_AIRPRT_IATA_CD,
Sum(SWAP) AS SWAP,
Min(CASE WHEN SWAP_NEW=1 THEN TM ELSE 1000000000000 END) AS LAST_SWAP,
Min(TM) AS MINS_TO_SCHD_DEP_QTY
FROM 
(SELECT 
SCHD_FIRST_LEG_DEP_LCL_DT,
OPERAT_FLIGHT_NBR,
SCHD_LEG_DEP_AIRPRT_IATA_CD,
SCHD_LEG_ARVL_AIRPRT_IATA_CD,
MINS_TO_SCHD_DEP_QTY AS TM,
CASE WHEN PREV_SUBFLEET_CD IN ('38A','38D')  THEN 'AD' WHEN PREV_SUBFLEET_CD IN ('38K','38M') THEN 'KM' ELSE  PREV_SUBFLEET_CD END AS PREV_SUBFLEET,
CASE WHEN SUB_FLEET_CD IN ('38A','38D')  THEN 'AD' WHEN SUB_FLEET_CD IN ('38K','38M') THEN 'KM' ELSE  SUB_FLEET_CD END AS SUBFLEET,
CASE WHEN PREV_SUBFLEET<>SUBFLEET AND MINS_TO_SCHD_DEP_QTY<=2880 THEN 1 ELSE 0 END AS SWAP,
CASE WHEN PREV_SUBFLEET<>SUBFLEET THEN 1 ELSE 0 END AS SWAP_NEW
FROM PROD_FLIGHT_OPS_COMBINED_VW.FLIGHT_LEG_TAIL_EVENT 
/*WHERE POST_FINAL_IND='Y' */
WHERE 
SCHD_LEG_DEP_LCL_DT BETWEEN ? AND DATE-1
AND SCHD_LEG_DEP_AIRPRT_IATA_CD='MIA'
) AS Q
GROUP BY SCHD_FIRST_LEG_DEP_LCL_DT,
OPERAT_FLIGHT_NBR,
SCHD_LEG_DEP_AIRPRT_IATA_CD,
SCHD_LEG_ARVL_AIRPRT_IATA_CD) 

SELECT	MKT_AIRLINE, AIRLINE,FLT_NUM, SKD_ORIG, SKD_DEST,
		SKD_FIRST_LEG_DPT_DATE,
CASE WHEN SKD_ORIG_ENREGION=11 AND SKD_DEST_ENREGION=11 THEN 'DOMESTIC' ELSE 'INTL' END AS INTL_DOM, SEATS,LF,ONBRD_REV_PAX,ONBRD_NREV_PAX,
		ACT_ORIG,
		ACT_DEST,
		SKD_OPS,
		ACT_OPS,
		CASE WHEN SKD_SUBFLEET IN ('38A','38D') THEN '737A/D' 
		ELSE '737K/M' END AS SKD_EQ,
		SKD_SUBFLEET,
		CASE WHEN ACT_SUBFLEET IN ('38A','38D') THEN '737A/D' 
		ELSE '737K/M' END AS ACT_EQ,
		ACT_SUBFLEET,
		CASE WHEN AVAIL_TURN<=MOGT THEN 'Y' ELSE 'N' END AS ON_MOGT,
		TURN_IND,T0,
		D0,DPT_VAR,
		ACT_TAIL,
SWAP AS SWAP_IN_D48HR, 
CASE WHEN LAST_SWAP=1000000000000 THEN NULL ELSE LAST_SWAP END AS LAST_SWAP_TO_DPT_MIN,
MINS_TO_SCHD_DEP_QTY AS LAST_TAIL_ASSIGN_TO_DPT_MIN,
DLY_CD0,DLY_CD1,DLY_CD2,DLY_CD3,DLY_CD4,DLY_CD5,DLY_CD6,DLY_CD7,
DLY_MIN0,DLY_MIN1,DLY_MIN2,DLY_MIN3,DLY_MIN4,DLY_MIN5,DLY_MIN6,DLY_MIN7

FROM	PROD_FLIGHT_OPS_COMBINED_VW.OPS_FLIGHT_LEG AS OPS  LEFT JOIN M 
ON 
OPS.SKD_FIRST_LEG_DPT_DATE=M.SCHD_FIRST_LEG_DEP_LCL_DT AND 
OPS.SKD_ORIG=M.SCHD_LEG_DEP_AIRPRT_IATA_CD AND 
OPS.SKD_DEST=M.SCHD_LEG_ARVL_AIRPRT_IATA_CD AND 
OPS.FLT_NUM=M.OPERAT_FLIGHT_NBR 
WHERE SKD_FIRST_LEG_DPT_DATE BETWEEN ? AND DATE-1
AND OPS_ANALYSIS_IND = 1 
AND OP_STATUS NOT = 'G'
AND SKD_SUBFLEET LIKE '38%'
AND ACT_SUBFLEET LIKE '38%'
AND SKD_ORIG='MIA'
ORDER BY SKD_FIRST_LEG_DPT_DATE, FLT_NUM 

"""

try:
    username,password='MOSSASOPAAPP10','WLsNiXJ4'
    udaExec = teradata.UdaExec (appName="test", version="1.0",logConsole=False) 
    session=udaExec.connect(method="odbc",system='edtdpAP1', username=username,password=password, autocommit=True,transactionMode="Teradata")
    df=pd.read_sql_query(query,session,params=[str(start_date),str(start_date)])
    if start_date==datetime.datetime.now().date()-datetime.timedelta(days=1):
        title=str(datetime.datetime.now().date()-datetime.timedelta(days=1))
    else:
        title=str(start_date)+" to "+str(datetime.datetime.now().date()-datetime.timedelta(days=1))
    df.to_csv('C:\\Users\\628066\\Desktop\\oasis\\MIA OASIS '+title+'.csv', index=False)
    
    import win32com.client
    o = win32com.client.Dispatch("Outlook.Application")
    Msg = o.CreateItem(0)    
    Msg.To = "suzanne.williamson@aa.com"
    Msg.CC = "shawn.morris@aa.com; baiyu.yang@aa.com"
    Msg.Subject = "MIA 737 oasis "+title
    Msg.Body = """Hi,
Please see attached file.

Thanks,
Xinzhu """
    attachment1 = 'C:\\Users\\628066\\Desktop\\oasis\\MIA OASIS '+title+'.csv'
    Msg.Attachments.Add(attachment1)
    Msg.Send()

except:
    import win32com.client
    o = win32com.client.Dispatch("Outlook.Application")
    Msg = o.CreateItem(0) 
    Msg.To = "xinzhu.li@aa.com;"
    Msg.Subject = "MIA 737 oasis failed"
    Msg.Send()
    
    