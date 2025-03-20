import os
import numpy as np
from datetime import datetime, timezone, timedelta
from WRFDataCollection import WRFDataCollection
from WRFDataTS import WRFDataTS

class VSFVali:
    def __init__(self):
        self.datafolder         = None
        self.wrflonlatorigo     = None
        self.meas_position = None
        self.wrf_position = None
        self.datetime = None
        self.datetime_interval = None
        self.wrfcoll= None # WRFDataCollection
        self.meas_data = None

    # def END
    #
    #=======================================================
    def setDataFolder(self, folderpath=None):
        if folderpath:
            if os.path.exists(folderpath):
                self.datafolder = folderpath
            else:
                raise FileNotFoundError(f"Data folder {folderpath} not found.")
        else:
            self.datafile = "default_datafile.nc"  # Placeholder for actual data file
        # if END
    # def END
    #
    #=======================================================
    def setMeasPosition(self, position):
        if len(position) >= 3:
            self.meas_position = position
        else:
            raise ValueError("Measurement position must have at least latitude, longitude and height.")
        # if END
    # def END
    #
    #=======================================================
    def setWRFLonLatOrigo(self, wrflonlatorigo):
        if len(wrflonlatorigo) >= 3:
            self.wrflonlatorigo = wrflonlatorigo
        else:
            raise ValueError("WRF position must have at least latitude, longitude and height.")
        # if END
    # def END
    #
    #=======================================================
    def setWRFPosition(self, position):
        if len(position) >= 3:
            self.wrf_position = position
        else:
            raise ValueError("WRF position must have at least latitude, longitude and height.")
        # if END
    # def END
    #
    #=======================================================
    def setDateTime(self, dt):
        if isinstance(dt, datetime):
            self.datetime1 = dt
            self.datetime2 = dt + timedelta(days=1) # default = 1
        else:
            raise TypeError("DateTime must be a datetime object.")
        # if END
    # def END
    #
    #=======================================================


    def setDateTimeInterval(self, dt_start, dt_end):
        if isinstance(dt_start, datetime) and isinstance(dt_end, datetime):
            if dt_start < dt_end:
                self.datetime1 = dt_start
                self.datetime2 = dt_end
            else:
                raise ValueError("Start time must be before end time.")
        else:
            raise TypeError("Both start and end times must be datetime objects.")

    def loadWRFData(self):
        if not self.wrf_position:
            raise ValueError("WRF position is not set.")

        # Placeholder: Replace with actual data extraction logic
        self.wrfcoll = WRFDataCollection(self.datafolder,True)
        print("load_date_range...")
        self.wrfcoll.load_date_range(self.datetime1,self.datetime2)
        print("WRF data loaded successfully.")

    def extractMeasData(self, location_name):
        if not self.meas_position:
            raise ValueError("Measurement position is not set.")

        # Placeholder: Replace with actual data extraction logic
        self.meas_data = WRFDataTS(self.datafolder, self.meas_position)
        print(f"Measurement data for {location_name} extracted successfully.")

    def compare(self, variable):
        if self.wrfcoll is None or self.meas_data is None:
            raise ValueError("Data has not been extracted for comparison.")

        # Placeholder: Replace with actual comparison logic
        print(f"Comparing {variable} between WRF data and measurement data.")

    def plot(self, variable):
        if self.wrfcoll is None or self.meas_data is None:
            raise ValueError("Data has not been extracted for plotting.")

        # Placeholder: Replace with actual plotting logic
        print(f"Plotting {variable} data.")
