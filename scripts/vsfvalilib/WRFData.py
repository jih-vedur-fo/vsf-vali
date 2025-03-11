import netCDF4 as nc
import math
import numpy as np
from datetime import datetime


class WRFData:
    def __init__(self, filename=None, fields=["all"]):
        """
        Constructor for WRFData class.
        :param filename: Optional filename of the NetCDF file to load.
        :param fields: List of fields to load from the NetCDF file. Default is ["all"].
        """
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


        self.u10 = None
        self.u10_loaded = False
        self.u10_unit = None


        if self.filename:
            self.loadFile(self.filename)
    # def END
    #====================================================

    # ===================================================
    # displayInfo()::
    # Displays data on the nc fhandle
    #
    def displayInfo(self):
        for dimension in self.fhandle.dimensions.values():
                print(dimension)
        for variable in self.fhandle.variables.values():
            print(variable)
    # def END
    #====================================================

    def loadFile(self, filename):
        """
        Loads a NetCDF file and retrieves the specified fields.
        :param filename: Path to the NetCDF file.
        """
        try:
            self.fhandle = nc.Dataset(filename, mode='r')
            print(f"Successfully loaded {filename}")

            self.loadTimes()

            if "t2" in self.fields or "all" in self.fields:
                self.t2, self.t2_unit, self.t2_loaded = self.loadField("T2")

        except Exception as e:
            print(f"Error loading file {filename}: {e}")
        # try END
    # def END
    #
    #====================================================
    def loadFileX(self, filename):
        """
        Loads a NetCDF file and retrieves the specified fields.
        :param filename: Path to the NetCDF file.
        """
        try:
            self.fhandle = nc.Dataset(filename, mode='r')
            print(f"Successfully loaded {filename}")



            if "all" in self.fields:
                self.loaded_data = {var: self.fhandle.variables[var][:] for var in self.fhandle.variables}
            else:
                for field in self.fields:
                    if field in self.fhandle.variables:
                        self.loaded_data[field] = self.fhandle.variables[field][:]
                    else:
                        print(f"Warning: Field '{field}' not found in {filename}")
        except Exception as e:
            print(f"Error loading file {filename}: {e}")
        # try END
    # def END
    #
    #====================================================
    def loadField(self, field):
        """
        Loads a specific field from the NetCDF file if it exists.
        :param field: Name of the field to load.
        """
        res = False
        if self.fhandle is None:
            print("Error: No fhandle loaded. Use loadFile() first.")
            return

        if field in self.fhandle.variables:
            varx = self.fhandle.variables[field]
            val = self.fhandle.variables[field][:]

            if "units" in varx.ncattrs():
                unit = varx.getncattr("units")
            else:
                unit = None
            # if END
            res = True

            print("Successfully loaded field: {} ({}, [{}])".format(field,unit,val.shape))
        else:
            print(f"Error: Field '{field}' not found in the fhandle.")
        return val, unit, res
    # def END
    #
    #====================================================
    def loadFieldX(self, field):
        """
        Loads a specific field from the NetCDF file if it exists.
        :param field: Name of the field to load.
        """
        if self.fhandle is None:
            print("Error: No fhandle loaded. Use loadFile() first.")
            return

        if field in self.fhandle.variables:
            self.loaded_data[field] = self.fhandle.variables[field][:]
            print(f"Successfully loaded field: {field}")
        else:
            print(f"Error: Field '{field}' not found in the fhandle.")
    # def END
    #====================================================

    def loadTimes(self):
        time_var = self.fhandle.variables["Times"]  # "Times" is usually the time variable in WRF output

        # Convert time (WRF stores it as character array)
        time_strings = ["".join(t) for t in time_var[:].astype(str)]

        # Print the first few time steps
        #print("WRF Time Steps:")
        self.times = []
        for t in time_strings[:]:  # Print only first 5 to keep output manageable
            self.times.append(datetime.strptime(t, "%Y-%m-%d_%H:%M:%S"))
            #print(t)
        self.times=np.array(self.times, dtype="datetime64")
        self.times_loaded = True
        self.times_unit = "UTC"
        #print(self.times)

        self.xtime, self.xtime_unit, self.xtime_loaded = self.loadField("XTIME")
        #print(self.xtime)

        self.itimestep, self.itimestep_unit, self.itimestep_loaded = self.loadField("ITIMESTEP")
        #print(self.itimestep)


# Example usage:
# wrf = WRFData("example.nc", ["temperature", "pressure"])
# wrf.loadFile("another_file.nc")
# wrf.loadField("humidity")
