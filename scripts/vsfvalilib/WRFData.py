import netCDF4 as nc
import numpy as np
from datetime import datetime


class WRFData:
    #====================================================
    def __init__(self, filename=None, verbose=False, fields=["all"]):
        """
        Constructor for WRFData class.
        :param filename: Optional filename of the NetCDF file to load.
        :param fields: List of fields to load from the NetCDF file. Default is ["all"].
        """
        self.verbose = verbose

        self.filename = filename
        self.fhandle = None
        self.fields = fields
        self.loaded_data = {}

        self.times = None
        self.times_loaded = False
        self.times_unit = None

        self.xtime = None
        self.xtime_loaded = False
        self.xtime_unit = None

        self.itimestep = None
        self.itimestep_loaded = False
        self.itimestep_unit = None

        self.t2 = None
        self.t2_loaded = False
        self.t2_unit = None

        self.slp = None
        self.slp_loaded = False
        self.slp_unit = None


        self.u10 = None
        self.u10_loaded = False
        self.u10_unit = None

        self.v10 = None
        self.v10_loaded = False
        self.v10_unit = None

        self.rainnc = None
        self.rainnc_loaded = False
        self.rainnc_unit = None

        self.snownc = None
        self.snownc_loaded = False
        self.snownc_unit = None

        self.rainnx = None
        self.rainnx_loaded = False
        self.rainnx_unit = None

        self.snownx = None
        self.snownx_loaded = False
        self.snownx_unit = None

        if self.filename:
            self.loadFile(self.filename)
    # def END
    #
    #====================================================
    # Returns the number of datapoint in this dataset.
    def getDPCount(self):
        #return len(self.times)
        return 1

    # def END
    #
    #====================================================
    def displayInfo(self):
        for dimension in self.fhandle.dimensions.values():
            print(dimension)
        for variable in self.fhandle.variables.values():
            print(variable)
    # def END
    #
    #====================================================
    def loadFile(self, filename):
        """
        Loads a NetCDF file and retrieves the specified fields.
        :param filename: Path to the NetCDF file.
        """
        try:
            self.fhandle = nc.Dataset(filename, mode='r')
            if self.verbose:    print(f"Successfully loaded {filename}")

            self.loadTimes()

            if "t2" in self.fields or "all" in self.fields:
                self.t2, self.t2_unit, self.t2_loaded = self.loadField("T2")

            if "slp" in self.fields or "all" in self.fields:
                self.slp, self.slp_unit, self.slp_loaded = self.loadField("T2")

            if "u10" in self.fields or "all" in self.fields:
                self.u10, self.u10_unit, self.u10_loaded = self.loadField("U10")

            if "v10" in self.fields or "all" in self.fields:
                self.v10, self.v10_unit, self.v10_loaded = self.loadField("V10")

            if "rainnc" in self.fields or "all" in self.fields:
                self.rainnc, self.rainnc_unit, self.rainnc_loaded = self.loadField("RAINNC")

            if "snownc" in self.fields or "all" in self.fields:
                self.snownc, self.snownc_unit, self.snownc_loaded = self.loadField("SNOWNC")



        except Exception as e:
            print(f"Error loading file {filename}: {e}")
    # def END
    #====================================================
    def loadField(self, field):
        """
        Loads a specific field from the NetCDF file if it exists.
        :param field: Name of the field to load.
        """
        res = False
        if self.fhandle is None:
            print("Error: No fhandle loaded. Use loadFile() first.")
            return None, None, False

        if field in self.fhandle.variables:
            varx = self.fhandle.variables[field]
            val = self.fhandle.variables[field][:]

            unit = varx.getncattr("units") if "units" in varx.ncattrs() else None
            res = True

            if self.verbose: print(f"Successfully loaded field: {field} ({unit}, {val.shape})")
        else:
            print(f"Error: Field '{field}' not found in the fhandle.")
            val, unit = None, None
        return val, unit, res
    # def END
    #====================================================
    def loadTimes(self):
        time_var = self.fhandle.variables["Times"]  # "Times" is usually the time variable in WRF output

        # Convert time (WRF stores it as character array)
        time_strings = ["".join(t) for t in time_var[:].astype(str)]

        self.times = [datetime.strptime(t, "%Y-%m-%d_%H:%M:%S") for t in time_strings]
        self.times = np.array(self.times, dtype="datetime64")
        self.times_loaded = True
        self.times_unit = "UTC"

        self.xtime, self.xtime_unit, self.xtime_loaded = self.loadField("XTIME")
        self.itimestep, self.itimestep_unit, self.itimestep_loaded = self.loadField("ITIMESTEP")
    # def END
