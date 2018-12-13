# -*- coding: utf-8 -*-
"""
Created on Fri Aug 18 09:42:54 2017

@author: ob300
"""

import sqlalchemy 
import pandas as pd
from pandasql import sqldf 
import pickle 

fsengine=sqlalchemy.create_engine("mssql+pyodbc://ob300:P@ssword@123@cdsalphasqldb.database.windows.net/Acadia?driver=SQL+Server")

def loaddata(x):
    asql=""" SELECT  
a.TruckID,
a.FileID,
a.abs_time_15000ms,
a.P_APC_i_ImaTrim_15000ms, 
a.P_APC_r_ImaTrimGain_15000ms
FROM tblMatData a 
Where a.TruckID = ?"""
    bsql=""" SELECT  
b.TruckID,
b.FileID,
b.abs_time_1000ms,
b.APC_qr_Cmd_1000ms,
b.H_APC_hp_Deviation_1000ms,
b.H_APC_qr_KiTerm_1000ms, 
b.CBM_Indicated_Trq_Fuel_1000ms, 
b.CBM_Indicated_Trq_Cmd_1000ms,
b.Coolant_Temperature_1000ms, 
b.P_APC_i_ImaTrim_1000ms,
b.P_APC_r_ImaTrimGain_1000ms
FROM tblMatData_1000 b
Where b.TruckID = ?"""
    csql=""" SELECT  
c.TruckID,
c.FileID,
c.abs_time_200ms,
c.APC_hp_Cmd_200ms,
c.APC_hp_Fdbk_200ms,
c.Engine_Speed_200ms
FROM tblMatData_200 c
Where c.TruckID = ?"""
    dsql=""" SELECT  
d.TruckID,
d.FileID,
d.abs_time,
d.Ambient_Air_Tmptr
FROM tblMatData_0 d
Where d.TruckID = ?"""
    a=pd.read_sql_query(asql,con=fsengine,params=[x])
    b=pd.read_sql_query(bsql,con=fsengine,params=[x])
    c=pd.read_sql_query(csql,con=fsengine,params=[x])
    d=pd.read_sql_query(dsql,con=fsengine,params=[x])
    q=""" select a.*, b.*,c.*, d.* from  a JOIN b on
a.TruckID = b.TruckID and
a.FileID = b.FileID and
a.abs_time_15000ms between (b.abs_time_1000ms - 0.0001667) and (b.abs_time_1000ms + 0.0001667)
JOIN c on
a.TruckID = c.TruckID and
a.FileID = c.FileID and 
a.abs_time_15000ms between (c.abs_time_200ms - 0.00000229) and (c.abs_time_200ms + 0.00000229)
JOIN d on
a.TruckID = d.TruckID and
a.FileID = d.FileID and
a.abs_time_15000ms between (d.abs_time - 0.0001667) and (d.abs_time + 0.0001667)"""

    t=sqldf(q,locals())
    return(t)


with open("t2","wb") as pickle_out:
    pickle.dump(t2,pickle_out,protocol=4)
with open("t2","rb") as pickle_in:
    truck1=pickle.load(pickle_in)

 