import os
import numpy as np
from datetime import datetime, timedelta
from WRFDataTS import WRFDataTS

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
        self.wrfts = None  # Dictionary to store WRFDataTS objects with folder names as keys
        self.subfolderpaths = []  # List to store full paths of subfolders
        self.subfoldernames = []  # List to store only the names of subfolders

        if not os.path.isdir(basepath):
            raise ValueError(f"Invalid base path: {basepath}")

        #self.loadSubfolders(self.verbose)
    # def END

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
                    wrfts.append(WRFDataTS(folderpath, verbose))
                    print(f"Loaded WRFDataTS for {foldername}")
                except Exception as e:
                    print(f"Failed to load WRFDataTS for {foldername}: {e}")
            # if END
        # for END
        self.wrfts = np.array(wrfts)
    # def END

    def load_date_range(self, start_date, end_date):
        """
        Loads data for a date range (exclusive of the end date).

        :param start_date: Start date string in the format 'YYYY-MM-DD'.
        :param end_date: End date string in the format 'YYYY-MM-DD' (exclusive).
        """
        try:
            print("Start datetime: {}".format(start_date))
            start = datetime.strftime(start_date, "%Y/%m/%d/")
            print("Start string  : {}".format(start))
            end = datetime.strftime(end_date, "%Y/%m/%d/")
            print("End string   : {}".format(end))
            current_date = start_date
            while current_date < end_date:
                for item in ["00","06"]:
                    folder_path =  os.path.join(self.basepath,datetime.strftime(current_date, "%Y/%m/%d/"),item)
                    #folder_path = os.path.join(self.basepath, current.strftime("%Y"), current.strftime("%m"), current.strftime("%d"))
                    print(folder_path)
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

    def get_data_set(self, index):
        """
        Retrieves the WRFDataTS object for a given subfolder.
        :param foldername: The name of the subfolder.
        :return: WRFDataTS instance or None if not found.
        """
        return self.wrfts[index]

    def list_data_sets(self):
        """
        Returns a list of all loaded dataset names.
        """
        return list(self.subfoldernames)

    def __repr__(self):
        return f"WRFDataCollection(basepath={self.basepath}, datasets={list(self.subfoldernames)})"
