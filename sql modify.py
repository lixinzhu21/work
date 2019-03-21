# -*- coding: utf-8 -*-
"""
Created on Tue Jan 29 14:33:14 2019

@author: 628066
"""
import teradata


try:
    username,password='MOSSASOPAAPP10','WLsNiXJ4'
    udaExec = teradata.UdaExec (appName="test", version="1.0",logConsole=False) 
    session=udaExec.connect(method="odbc",system='edtdpAP1', username=username,password=password, autocommit=True,transactionMode="Teradata")
    query1=""" delete PROD_FATSYS_SNBX_DB.PAX_CHECKIN all"""
    query2="""
insert into PROD_FATSYS_SNBX_DB.PAX_CHECKIN
SELECT 
		  b.AIRLINE
		, a.SCHD_LEG_DEP_DT AS DATE_
		, a.SCHD_OPMETAL_FLIGHT_NBR AS FLT_NUM
		, a.SCHD_LEG_DEP_AIRPRT_IATA_CD AS SKD_ORIG
		, b.SKD_DEST
		, a.PAX_CHECKIN_TMS
		, b.SKDOUT
		, b.ACTOUT
		, b.SKD_OUT
		, b.ACT_OUT
		, b.DPT_VAR
		, b.OP_DESC
		, d.OP_DESC AS UPL_OP_DESC
		, b.MOGT
		, b.AVAIL_TURN
		, b.UPLINE_SKD_DPT_DATE
		, b.UPLINE_FLT_NUM
		, b.UPLINE_ORIG
		, b.UPLINE_DEST
		, b.UPLINE_ACT_IN
		, b.ENPLAN_REV_PAX
		, b.ENPLAN_NREV_PAX
		, b.D0
		, b.T0
		, b.ACT_SUBFLEET AS SUBFLEET
		, b.DPT_GATE
		, b.DLY_CD0	
		, b.DLY_CD1	
		, b.DLY_CD2	
		, b.DLY_CD3	
		, b.DLY_CD4
		, b.SKD_ORIG_ENREGION
		, b.SKD_DEST_ENREGION
		, b.SKD_DPT_TMS	
		, b.ACT_DPT_TMS	
		, d.SKD_IN_TMS	AS UPL_SKD_IN_TMS
		, d.ACT_IN_TMS  AS UPL_ACT_IN_TMS
		, c.PAX_TRAVEL_TYPE_CD
		, c.PNR_LOCTR_ID
		, c.CUST_PNR_SEQ_ID
		, c.PAX_FIRST_NM
		, c.PAX_LAST_NM
		, a.CHECKIN_TRANS_TXT
		
	FROM 
		PROD_AIRPRT_CHECK_IN_VWS .FLIGHT_PAX_CHECKIN_HIST a 

	LEFT JOIN PROD_FATSYS_SNBX_DB.GZ_OPS_FLIGHT_LEG b
		 ON 
			 a.SCHD_LEG_DEP_DT = b.SKD_FIRST_LEG_DPT_DATE
		 AND a.SCHD_OPMETAL_FLIGHT_NBR = b.FLT_NUM
		 AND a.SCHD_LEG_DEP_AIRPRT_IATA_CD = b.ACT_ORIG

	LEFT JOIN PROD_AIRPRT_CHECK_IN_VWS.FLIGHT_PAX c
		 ON 
		  	 a.PNR_LOCTR_ID = c.PNR_LOCTR_ID
		 AND a.PNR_CHECKIN_PAX_SEQ_NBR = c.CUST_PNR_SEQ_ID
		 AND a.SCHD_LEG_DEP_DT = c.SCHD_LEG_DEP_DT 
		 AND a.SCHD_OPMETAL_FLIGHT_NBR = c.SCHD_OPMETAL_FLIGHT_NBR
		 AND a.SCHD_LEG_DEP_AIRPRT_IATA_CD = c.SCHD_LEG_DEP_AIRPRT_IATA_CD

	LEFT JOIN PROD_FATSYS_SNBX_DB.GZ_OPS_FLIGHT_LEG d
		 ON 
			 b.UPLINE_SKD_DPT_DATE = d.SKD_FIRST_LEG_DPT_DATE 
		 AND b.UPLINE_FLT_NUM = d.FLT_NUM
		 AND b.UPLINE_ORIG = d.ACT_ORIG
		 AND b.UPLINE_DEST = d.ACT_DEST
		 AND b.UPLINE_ACT_IN = d.ACT_IN


	WHERE 
		    a.SCHD_LEG_DEP_DT = DATE-1
		AND a.SCHD_LEG_DEP_AIRPRT_IATA_CD ='PHL'
	  	AND a.ONBRD_IND = 'Y'
	  	AND b.AIRLINE NOT IN ('AA')	
		AND b.OP_DESC = 'PS OP'
		AND b.OP_PRE_STATUS_DESC LIKE 'Planned%'
"""
    session.execute(query1)
    session.execute(query2)

except:
    print('shit!')
    