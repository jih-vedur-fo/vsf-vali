import os
import numpy as np
from WRFDataTS import WRFDataTS

class WRFDataCollection:
    def __init__(self, basepath, verbose=False):
        """
        Initializes a WRFDataCollection instance.
        Iterates through subdirectories of `basepath`, creating a WRFDataTS object for each.

        :param basepath: The root directory containing subfolders with WRF data files.
        """
        self.verbose = verbose
        self.basepath = basepath
        self.wrfts = None  # Dictionary to store WRFDataTS objects with folder names as keys
        self.subfolderpaths = []  # List to store full paths of subfolders
        self.subfoldernames = []  # List to store only the names of subfolders

        if not os.path.isdir(basepath):
            raise ValueError(f"Invalid base path: {basepath}")

        self.loadSubfolders(self.verbose)

    def loadSubfolders(self,verbose):
        """
        Iterates through all subdirectories in basepath and initializes WRFDataTS for each.
        """
        wrfts = []
        for foldername in sorted(os.listdir(self.basepath)):

            folderpath = os.path.join(self.basepath, foldername)
            print("Loading folder : {}".format(folderpath))

            if os.path.isdir(folderpath):  # Ensure it's a directory
                self.subfolderpaths.append(folderpath)
                self.subfoldernames.append(foldername)

                try:

                    wrfts.append(WRFDataTS(folderpath,verbose))
                    #self.wrfts[foldername] = WRFDataTS(folderpath)
                    print(f"Loaded WRFDataTS for {foldername}")
                except Exception as e:
                    print(f"Failed to load WRFDataTS for {foldername}: {e}")
            # if END
        # for END
        self.wrfts = np.array(wrfts)
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
        return f"WRFDataCollection(basepath={self.basepath}, datasets={list(self.wrfts.keys())})"
