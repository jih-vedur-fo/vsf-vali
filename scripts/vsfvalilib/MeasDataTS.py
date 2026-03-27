import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta, timezone

class MeasDataTS:
    #=======================================================
    def __init__(self, basepath=None, verbose=False):
        # Initialize the MeasDataTS object
        self.basepath = basepath
        self.verbose = verbose
        self.locationname = None # String, e.g. Havn or Mykines
        self.locationposition = None # List of [Lon, Lat, Height]
        self.data = None

        # Individual variables
        self.datetime = None
        self.ws = None
        self.wd = None
        self.ws10 = None
        self.wsmax = None
        self.t2min = None
        self.t2avg = None
        self.t2max = None
        self.dpt2 = None
        self.prec = None
        self.rh = None
        self.pqff = None
        self.cloud = None
        self.sun = None

        # Variable names and units
        self.datetime_name = None
        self.datetime_unit = None
        self.ws_name = None
        self.ws_unit = None
        self.wd_name = None
        self.wd_unit = None
        self.ws10_name = None
        self.ws10_unit = None
        self.wsmax_name = None
        self.wsmax_unit = None
        self.t2min_name = None
        self.t2min_unit = None
        self.t2avg_name = None
        self.t2avg_unit = None
        self.t2max_name = None
        self.t2max_unit = None
        self.dpt2_name = None
        self.dpt2_unit = None
        self.prec_name = None
        self.prec_unit = None
        self.rh_name = None
        self.rh_unit = None
        self.pqff_name = None
        self.pqff_unit = None
        self.cloud_name = None
        self.cloud_unit = None
        self.sun_name = None
        self.sun_unit = None
        if self.verbose:
            print(f"Initialized MeasDataTS with basepath: {self.basepath}")
        # if END
    # def END
    #
    #=======================================================
    def setDateRange(self, start_date, end_date):
        # Set the date range for loading data
        self.startDate = start_date.replace(tzinfo=timezone.utc)
        self.endDate = end_date.replace(tzinfo=timezone.utc)
        if self.verbose:
            print(f"Date range set to: {self.startDate} to {self.endDate}")
        # if END
    # def END
    #
    #=======================================================
    def setLocation(self, location):
        # Set the location and position of the data
        if len(location)>=4 :
            self.locationname = location[0]
            self.locationposition = location[1:4]
            if self.verbose:
                print(f"Location set to: {location}")
            # if END
        else:
            raise ValueError("Location must be a name-lon-lat-height list. Currently: {}".format(location))
        # if END
    # def END
    #
    #=======================================================
    def loadWSData(self):
        # Load weather station data
        self.listAllFiles()
        self.selectFiles()
        self.loadData()
    # def END
    #
    #=======================================================
    def listAllFiles(self):
        # List and store all files found in the basepath folder
        if self.basepath is None:
            raise ValueError("Basepath not set.")
        # if END
        self.basepathfiles = []
        for root, _, files in os.walk(self.basepath):
            for file in files:
                if file.endswith(".csv"):
                    file_path = os.path.join(root, file)
                    self.basepathfiles.append(file_path)
                # if END
            # for END
        # for END
        self.basepathfiles.sort()
        if self.verbose:
            print(f"Found {len(self.basepathfiles)} files in basepath.")
        # if END
    # def END
    #
    #=======================================================
    def selectFiles(self):
        # Select files with matching location name and date range
        self.datafiles = []
        for file_path in self.basepathfiles:
            try:
                print("Looking at file: {}".format(file_path))
                file_name = os.path.basename(file_path)
                location, year, month, _ = file_name.split('_')
                filedate_YM = datetime(int(year), int(month), 1, tzinfo=timezone.utc) + timedelta(seconds=1)
                startDate_YM = datetime(int(self.startDate.year), int(self.startDate.month), 1, tzinfo=timezone.utc)
                endDate_YM = startDate_YM.replace(day=1, month=(startDate_YM.month % 12) + 1, year=startDate_YM.year + (startDate_YM.month // 12))
                if location == self.locationname:
                    if startDate_YM <= filedate_YM <= endDate_YM:
                        self.datafiles.append(file_path)
                        if self.verbose:
                            print(f"Selected file: {file_path}")
                        # if END

                    # if END
                # if END
            except ValueError:
                raise ValueError("Filename format incorrect. Expected format: Location_YYYY_MM_h.csv")
            # try END
        # for END
        if self.verbose:
            print(f"Total selected files: {len(self.datafiles)}")
        # if END
    # def END
    #
    #=======================================================
    def loadData(self):
        # Load data from selected files and filter by date range
        data_frames = []
        for file_path in self.datafiles:
            print("File: {}".format(file_path))
            df = pd.read_csv(file_path, encoding='ISO-8859-1')
            # Extract column names and units from the first two rows
            column_names = df.columns
            units = df.iloc[0]
            df = df[1:]
            df.columns = column_names
            if self.verbose:
                print(f"Loaded file: {file_path} with columns: {list(column_names)}")
            # if END
            df['datetime'] = pd.to_datetime(df['Tíð'], format='%Y%m%d%H', utc=True)
            df = df[(df['datetime'] >= self.startDate) & (df['datetime'] <= self.endDate)]
            data_frames.append(df)
        # for END
        if data_frames:
            self.data = pd.concat(data_frames, ignore_index=True)
            if self.verbose:
                print("Data successfully loaded from selected files.")
            # if END
        else:
            raise ValueError("No data found within the specified date range.")
        # if END
        column_names = self.data.columns
        units = self.data.iloc[0]
        self.data = self.data[1:]
        variables = ['datetime', 'ws', 'wd', 'ws10', 'wsmax', 't2min', 't2avg', 't2max', 'dpt2', 'prec', 'rh', 'pqff', 'cloud', 'sun']
        for var, col_name, unit in zip(variables, column_names, units):
            setattr(self, var, self.data[col_name].to_numpy())
            setattr(self, f"{var}_name", col_name)
            setattr(self, f"{var}_unit", unit)
        # for END
        if self.verbose:
            print("Data loaded and variables mapped successfully.")
        # if END
    # def END
    #
    #=======================================================
    def getDataSeries(self, field_names):
        # Get a DataSeries object containing data for the specified fields
        from DataSeries import DataSeries

        if not isinstance(field_names, list):
            raise ValueError("Field names must be provided as a list.")
        # if END
        datetime = self.datetime
        data = []
        names = []
        units = []
        for field_name in field_names:
            # Handle aliases
            if field_name=="t2": field_name="t2avg"

            if hasattr(self, field_name):
                values = getattr(self, field_name)
                name = getattr(self, f"{field_name}_name", field_name)
                unit = getattr(self, f"{field_name}_unit", "unknown")
                data.append(values)
                names.append(name)
                units.append(unit)
            else:
                raise ValueError(f"Field '{field_name}' not found in the data.")
            # if END
        # for END
        ds = DataSeries(datetime,data)
        ds.setNames("time",names)
        ds.setUnits("datetime",units)

        return ds
    # def END
