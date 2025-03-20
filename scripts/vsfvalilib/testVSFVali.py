import os
import numpy as np
from datetime import datetime, timezone
import WRFDataCollection
from WRFDataTS import WRFDataTS
from VSFVali import VSFVali
import Locations as l

wrfdatafolder = "/opt/vsfvali/data/wrf/area2/"
vsdatafolder = ""







dt_utc = datetime(2024, 12, 24, 13, 24, 15, tzinfo=timezone.utc)
dt_utc1 = datetime(2024, 12, 24, 0, 0, 0, tzinfo=timezone.utc)
dt_utc2 = datetime(2024, 12, 31, 0, 0, 0, tzinfo=timezone.utc)
#                        XLONG       XLAT
WRFPosLonLatOrigo = [-7.92926025, 61.21746826, 0, "deg", "deg", "m"] # Lon, Lat, H
WRFPosLonLatUlt   = [-6.02639771, 62.56379318, 0] # Lon, Lat, H
WRFPosXYOrigo     = [-49.26634490, -89.69662377, 0] # X, Y, H
WRFPosXYUlt       = [50.23365510, 59.80337623, 0] # X, Y, H


vali = VSFVali()
vali.setDataFolder(wrfdatafolder)
vali.setWRFLonLatOrigo(WRFPosLonLatOrigo)
vali.setDateTimeInterval(dt_utc1,dt_utc2)


vali.setMeasPosition(l.VS_Havn_Wind)
vali.setWRFPosition(l.WRF_Havn)
vali.setDateTime(dt_utc) # default delta time is 1 day
vali.setDateTimeInterval(dt_utc1,dt_utc2) # default delta time is 1 day
print("loadWRDData...")
vali.loadWRFData()
vali.extractMeasData("Havn")
vali.compare("t2")
vali.plot("t2")


