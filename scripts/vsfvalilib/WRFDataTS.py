import os
from WRFData import WRFData
import numpy as np
import vsfvalilib as u

class WRFDataTS:
    def __init__(self, folderpath, verbose = False):
        self.verbose = verbose
        self.folderpath = None
        self.filenames = []
        self.fullfilenames = []
        # TS Data fields
        self.datapointscount = -1
        self.times       = None
        self.times_unit  = None
        self.mjd         = None
        self.mjd_unit    = None
        self.t2          = None
        self.t2_unit     = None
        self.u10         = None
        self.u10_unit    = None
        self.v10         = None
        self.v10_unit    = None
        self.rainph      = None  # 1-hour rain = rainp3h / 3
        self.rainph_unit = None
        self.rainnc      = None  # rainnc from data file
        self.rainnc_unit = None
        self.snowph      = None  # 1-hour snow = snowp3h / 3
        self.snowph_unit = None
        self.snownc      = None  # snownc from data file
        self.snownc_unit = None


        self.folderpath = folderpath
        self.fullfilenames, self.filenames = self.listFolder()
        self.wrfs = self.loadDataSets(False)

        self.calcDeltaFields() # Must come before produce time series
        self.produceTimeSeries()
        if self.verbose: self.print_field_info()


    def print_field_info(self):
        """Prints info for each field: mean, min, max, and shape in a structured format."""
        fields = [
            "times", "mjd", "t2", "u10", "v10",
            "rainph", "rainnc",
            "snowph", "snownc"
        ]

        print(f"{'Field':<10} {'Mean':>25} {'Min':>25} {'Max':>25} {'Shape':>15} {'Unit':>10}")
        print("=" * 120)

        for field in fields:
            data = getattr(self, field, None)
            unit = getattr(self, f"{field}_unit", "")

            # Handle datetime64 fields (format without milliseconds)
            if isinstance(data, np.ndarray) and np.issubdtype(data.dtype, np.datetime64):
                shape = str(data.shape)
                min_val = str(np.min(data))[:19]  # Trim milliseconds
                max_val = str(np.max(data))[:19]  # Trim milliseconds
                mean_val = "-"  # Mean doesn't make sense for datetime64
                print("{:10s} {:>25s} {:>25s} {:>25s} {:>15s} {:>10s}".format(
                    field, mean_val, min_val, max_val, shape, unit
                ))
                continue  # Skip numerical calculations for datetime64

            # Ensure data is numeric before computing statistics
            if isinstance(data, np.ndarray) and data.size > 0 and np.issubdtype(data.dtype, np.number):
                mean_val = np.mean(data)
                min_val = np.min(data)
                max_val = np.max(data)
                shape = str(data.shape)
                print("{:10s} {:25.2f} {:25.2f} {:25.2f} {:>15s} {:>10s}".format(
                    field, mean_val, min_val, max_val, shape, unit
                ))
            else:
                print("{:10s} {:>25s} {:>25s} {:>25s} {:>15s} {:>10s}".format(
                    field, "-", "-", "-", "-", unit
                ))


    def calcDeltaFields(self):
        self.calcDeltaField_RAINNC()
        self.calcDeltaField_SNOWNC()


    def calcDeltaField_RAINNC(self):
        last = 0
        field="RAINNX"
        for i in range(self.count()):
            self.wrfs[i].rainnx = self.wrfs[i].rainnc - last
            self.wrfs[i].rainnx_unit = "{}/h".format(self.wrfs[i].rainnc_unit)
            self.wrfs[i].rainnx_loaded = True
            last = self.wrfs[i].rainnc
        if self.verbose: print("Successfully calc'd field: {} ({}, {}x{})".format(field,self.wrfs[0].rainnx_unit,self.wrfs[0].rainnx.shape,self.count()))

    def calcDeltaField_SNOWNC(self):
        last = 0
        field="SNOWNX"
        for i in range(self.count()):
            self.wrfs[i].snownx = self.wrfs[i].snownc - last
            self.wrfs[i].snownx_unit = "{} h-1".format(self.wrfs[i].snownc_unit)
            self.wrfs[i].snownx_loaded = True
            last = self.wrfs[i].snownc
        if self.verbose: print("Successfully calc'd field: {} ({}, {}x{})".format(field,self.wrfs[0].snownx_unit,self.wrfs[0].snownx.shape,self.count()))


    def count(self):
        return len(self.wrfs)

    def initFieldArrays(self,initlen):
        self.times = np.array(initlen)

    # def END
    #
    #====================================================
    def listFolder(self):
        """
        Lists all files in the specified folder, sorts them by filename,
        and returns the sorted list.
        """
        if not os.path.isdir(self.folderpath):
            raise ValueError(f"Invalid folder path: {self.folderpath}")

        files = []
        fullfiles = []
        for f in os.listdir(self.folderpath):
            if os.path.isfile(os.path.join(self.folderpath, f)):
                files.append(f)
                ffn = os.path.join(self.folderpath, f)
                fullfiles.append(ffn)


            # if END
        # for END
        fullfiles = sorted(fullfiles)
        files = sorted(files)

        return fullfiles, files
    # def END
    #
    #====================================================
    def loadDataSets(self,verbose=2):
        if verbose==2: verbose = self.verbose
        wrfs = []
        for fn in self.fullfilenames:
            wrf = WRFData(fn,verbose)
            wrfs.append(wrf)
        # for END
        return wrfs
    # def END
    #
    #====================================================
    def produceTimeSeries(self):
        # Count number of data points
        ndp = 0
        for i in range(self.count()):
            ndp = ndp + self.wrfs[i].getDPCount()
        # for END
        self.datapointscount = ndp
        #
        n = 0
        #self.initFieldArrays(self.datapointscount)

        count = self.count()

        # Extract times and units
        times = []
        for i in range(count):
            for j in range(self.wrfs[i].getDPCount()):
                times.append(self.wrfs[i].times[j])
        self.times = np.array(times)
        self.times_unit = self.wrfs[0].times_unit if count > 0 else None

        # Convert times to MJD
        mjd = [u.datetime64ToMJD(t) for t in self.times]
        self.mjd = np.array(mjd)
        self.mjd_unit = "days since 1858-11-17"

        # Extract meteorological variables and their units
        t2 = []
        u10 = []
        v10 = []
        rainnc = []
        snownc = []
        rainph = []  # Now read from self.wrfs[i].rainnx
        snowph = []  # Now read from self.wrfs[i].snownx

        for i in range(count):
            for j in range(self.wrfs[i].getDPCount()):
                t2.append(self.wrfs[i].t2[j])
                u10.append(self.wrfs[i].u10[j])
                v10.append(self.wrfs[i].v10[j])
                rainnc.append(self.wrfs[i].rainnc[j])
                snownc.append(self.wrfs[i].snownc[j])
                rainph.append(self.wrfs[i].rainnx[j])  # Read 1-hour rainfall
                snowph.append(self.wrfs[i].snownx[j])  # Read 1-hour snowfall

        self.t2 = np.array(t2)
        self.t2_unit = self.wrfs[0].t2_unit if count > 0 else None

        self.u10 = np.array(u10)
        self.u10_unit = self.wrfs[0].u10_unit if count > 0 else None

        self.v10 = np.array(v10)
        self.v10_unit = self.wrfs[0].v10_unit if count > 0 else None

        self.rainnc = np.array(rainnc)
        self.rainnc_unit = self.wrfs[0].rainnc_unit if count > 0 else None

        self.snownc = np.array(snownc)
        self.snownc_unit = self.wrfs[0].snownc_unit if count > 0 else None

        # Directly read 1-hour precipitation/snowfall
        self.rainph = np.array(rainph)
        self.rainph_unit = self.wrfs[0].rainnx_unit if count > 0 else None  # Read unit from rainnx

        self.snowph = np.array(snowph)
        self.snowph_unit = self.wrfs[0].snownx_unit if count > 0 else None  # Read unit from snownx
    # def END


# Example usage:
# wrf = WRFDataTS("/path/to/folder")
# print(wrf.files)

