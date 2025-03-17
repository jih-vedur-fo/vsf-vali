import os
import numpy as np
from datetime import datetime, timezone
import WRFDataCollection
from WRFDataTS import WRFDataTS
from WRFDataTS import VSFVali

WRF_Havn = [62.02305205116182, -6.764374619983715, 55 ]
VS_Havn = [62.02305205116182, -6.764374619983715, 55 ]
VS_Akraberg = [61.39419041133272, -6.679475703300813, 89.6]



dt_utc = datetime(2024, 12, 24, 13, 24, 15, tzinfo=timezone.utc)
dt_utc1 = datetime(2024, 12, 24, 0, , 0, tzinfo=timezone.utc
dt_utc2 = datetime(2024, 12, 25, 0, , 0, tzinfo=timezone.utc)


vali = vsfVali()
vali.setDatafile()

vali.setMeasPosition(VS_Havn)
vali.setWRFPosition(WRF_Havn)
vali.setDateTime(dt_utc) # default delta time is 1 day
vali.setDateTimeInterval(dt_utc1,dt_utc2)
vali.extractWRFData()
vali.extractMeasData("Havn")
vali.compare("t2")
vali.plot("t2")


