import os
import numpy as np
from datetime import datetime, timedelta
from WRFDataTS import WRFDataTS
from DataSeries import DataSeries

class WRFDataCollection:
    def __init__(self, basepath, verbose=False):
        """
        Initializes a WRFDataCollection instance.
        Iterates through subdirectories of `basepath`, creating a WRFDataTS object for each.

        :param basepath: The root directory containing subfolders with WRF data files.
        """
        self.verbose = verbose
        self.basepath = basepath  # The folder just above 2025/01/27
        self.dirlist = [] # list of folder containg dateset to be loaded.
        self.datafields = ["all"]  # Ensure all data fields are loaded.
        self.modelruns = ["00","06","12","18"]
        self.wrfts = []
        self.subfolderpaths = []  # List to store full paths of subfolders
        self.subfoldernames = []  # List to store only the names of subfolders

        if not os.path.isdir(basepath):
            raise ValueError(f"Invalid base path: {basepath}")

        #self.loadSubfolders(self.verbose)
    # def END
    #
    #=======================================================
    def loadSubfolders(self, verbose):
        """
        Iterates through all subdirectories in basepath and initializes WRFDataTS for each.
        """
        wrfts = []
        if self.dirlist == []: # That is, if no list is already created.
            self.dislist = sorted(os.listdir(self.basepath))
        # if END
        #
        for foldername in self.dirlist:

            folderpath = os.path.join(self.basepath, foldername)
            print("Loading folder : {}".format(folderpath))

            if os.path.isdir(folderpath):  # Ensure it's a directory
                self.subfolderpaths.append(folderpath)
                self.subfoldernames.append(foldername)

                try:
                    wrfts.append(WRFDataTS(folderpath, verbose,self.datafields))
                    print(f"Loaded WRFDataTS for {foldername}")
                except Exception as e:
                    print(f"Failed to load WRFDataTS for {foldername}: {e}")
            else:
                print("WARNING: {} is not a found folder...".format(folderpath))

            # if END
        # for END
        self.wrfts = np.array(wrfts)
    # def END
    #
    #=======================================================
    def setDateRange(self, start_date, end_date):
        self.startDate = start_date.replace(tzinfo=UTC)
        self.endDate   = end_date.replace(tzinfo=UTC)
    # def END
    #
    #=======================================================
    def loadWRFData(self):
        """
        Loads data for a date range (exclusive of the end date).

        :param start_date: Start date string in the format 'YYYY-MM-DD'.
        :param end_date: End date string in the format 'YYYY-MM-DD' (exclusive).
        """
        try:
            print("Start datetime: {}".format(start_date))
            sStartDate = datetime.strftime(start_date, "%Y/%m/%d/")
            print("Start date  : {}".format(sStartDate))
            sEndDate = datetime.strftime(end_date, "%Y/%m/%d/")
            print("End date    : {}".format(sEndDate))
            current_date = start_date
            while current_date < end_date:
                for item in self.modelruns:
                    folder_path =  os.path.join(self.basepath,datetime.strftime(current_date, "%Y/%m/%d/"),item)
                    #folder_path = os.path.join(self.basepath, current.strftime("%Y"), current.strftime("%m"), current.strftime("%d"))
                    #print(folder_path)
                    if os.path.isdir(folder_path):
                        print(f"Adding folder to load list from: {folder_path}")
                        self.dirlist.append(folder_path)
                    else:
                        print(f"This is not a folder:  {folder_path}")
                    # if END

                # for END
                current_date += timedelta(days=1)
        except Exception as e:
            print(f"Error loading data for date range {start_date} to {end_date}: {e}")
        # try END
        self.loadSubfolders(True)
    # def END
    #
    #=======================================================
    def get_data_set(self, index):
        """
        Retrieves the WRFDataTS object for a given subfolder.
        :param foldername: The name of the subfolder.
        :return: WRFDataTS instance or None if not found.
        """
        return self.wrfts[index]
    # def END
    #
    #=======================================================
    def list_data_sets(self):
        """
        Returns a list of all loaded dataset names.
        """
        return list(self.subfoldernames)
    # def END
    #
    #=======================================================
    def setFields(self, fields=["all"]):
        if fields:
            self.datafields = fields
        else:
            self.datafields = ["all"]
        # if END
    # def END
    #
    #=======================================================
    def getDataSeries(self):
        ds = DataSeries()
        x = self.wrfts[0].mjd
        y =  [ self.wrfts[0].t2[:,100,100], self.wrfts[0].t2[:,105,105], self.wrfts[0].t2[:,110,110], self.wrfts[0].t2[:,115,115] ]
        ds.addData(x,y)
        ds.plot(title="T2", xlabel="Time", ylabel="Measurement")
    # def END
    #
    #=======================================================
    def __repr__(self):
        return f"WRFDataCollection(basepath={self.basepath}, datasets={list(self.subfoldernames)})"
    # def END
    #
    #=======================================================
