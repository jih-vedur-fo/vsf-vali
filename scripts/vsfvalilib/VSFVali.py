import os
import numpy as np
from datetime import datetime, timedelta, timezone
from WRFDataCollection import WRFDataCollection
from WRFDataTS import WRFDataTS
from MeasDataTS import MeasDataTS
from Plotter import Plotter

class VSFVali:
    def __init__(self):
        self.verbose = False
        self.wrfdatafolder          = None
        self.wsdatafolder           = None
        self.fields                 = ["all"]
        self.startDate              = None
        self.endDate                = None
        self.wrflonlatorigo         = None
        self.wrfposition            = None
        self.wrfcoll                = None # WRFDataCollection
        self.wsts                   = None # MeasDataTS
        self.wsname                 = None #
        self.wsposition             = None #

    # def END
    #
    #=======================================================
    def setDataFolder(self, folderpath=None):
        if folderpath:
            if os.path.exists(folderpath):
                self.wrfdatafolder = folderpath
            else:
                raise FileNotFoundError(f"Data folder {folderpath} not found.")
        else:
            self.datafile = "default_datafile.nc"  # Placeholder for actual data file
        # if END
    # def END
    #
    #=======================================================
    def setWSDataFolder(self, folderpath=None):
        if folderpath:
            if os.path.exists(folderpath):
                self.wsdatafolder = folderpath
            else:
                raise FileNotFoundError(f"WS Data folder {folderpath} not found.")
        else:
            self.datafile = "default_datafile.nc"  # Placeholder for actual data file
        # if END
    # def END
    #
    #=======================================================
    def setFields(self, fields=["all"]):
        if fields:
            self.fields = fields
        else:
            self.fields = ["all"]
        # if END
    # def END
    #
    #=======================================================
    def setMeasurementLocation(self, location):
        # Set the location and position of the data
        if len(location)>=4 :
            self.wsname = location[0]
            self.wsposition = location[1:4]
            if self.verbose:
                print(f"Location set to: {location}")
            # if END
        else:
            raise ValueError("Location must be a name-lon-lat-height list. Currently: {}".format(location))
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
            self.startDate = dt
            self.endDate = dt + timedelta(days=1) # default = 1
        else:
            raise TypeError("DateTime must be a datetime object.")
        # if END
    # def END
    #
    #=======================================================
    def setDateTimeInterval(self, dt_start, dt_end):
        if isinstance(dt_start, datetime) and isinstance(dt_end, datetime):
            if dt_start < dt_end:
                self.startDate = dt_start.replace(tzinfo=timezone.utc)
                self.endDate = dt_end.replace(tzinfo=timezone.utc)
            else:
                raise ValueError("Start time must be before end time.")
        else:
            raise TypeError("Both start and end times must be datetime objects.")
    # def END
    #
    #=======================================================
    def loadWRFData(self):
        if not self.wrf_position:
            raise ValueError("WRF position is not set.")

        # Placeholder: Replace with actual data extraction logic
        self.wrfcoll = WRFDataCollection(self.wrfdatafolder,self.verbose)
        self.wrfcoll.setFields(self.fields)
        self.wrfcoll.setDateRange(self.datetime1,self.datetime2)
        self.wrfcoll.loadWRFData()
        print("WRF data loaded successfully.")
    # def END
    #
    #=======================================================
    def loadMeasurementData(self):
        self.wsts = MeasDataTS(self.wsdatafolder,self.verbose)
        self.wsts.setLocation([self.wsname]+self.wsposition)
        #self.wsts.setFields(self.fields)
        self.wsts.setDateRange(self.startDate,self.endDate)
        self.wsts.loadWSData()
        print("WRF data loaded successfully.")
    # def END
    #
    #=======================================================
    def compare(self, variable):
        if self.wrfcoll is None or self.meas_data is None:
            raise ValueError("Data has not been extracted for comparison.")

        # Placeholder: Replace with actual comparison logic
        print(f"Comparing {variable} between WRF data and measurement data.")
    # def END
    #
    #=======================================================
    def plot(self, variable):
        if self.wrfcoll is None or self.meas_data is None:
            raise ValueError("Data has not been extracted for plotting.")

        # Placeholder: Replace with actual plotting logic
        print(f"Plotting {variable} data.")
    # def END
    #
    #=======================================================
    def getDataSeries(self):
        self.ds = self.wrfcoll.getDataSeries()
    # def END
    #
    #=======================================================
    def plotMeasurementData(self):
        plotter = Plotter()
        ds = self.wsts.getDataSeries(self.fields)
        print(ds.getPointsCount())
        ds.p_blocking = True
        ds.plot()
        #plotter.plotDataSeries()
