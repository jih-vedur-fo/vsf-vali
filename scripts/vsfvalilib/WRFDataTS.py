import os
from WRFData import WRFData

class WRFDataTS:
    def __init__(self, folderpath):
        self.folderpath = folderpath
        self.filenames = []
        self.fullfilenames = []
        self.fullfilenames, self.filenames = self.listFolder()
        self.wrfs = self.loadDataSets()
        self.calcDeltaFields()



    def calcDeltaFields(self):
        self.calcDeltaField_RAINNC()
        self.calcDeltaField_SNOWNC()


    def calcDeltaField_RAINNC(self):
        last = 0
        field="RAINNX"
        for i in range(self.count()):
            self.wrfs[i].rainnx = self.wrfs[i].rainnc - last
            self.wrfs[i].rainnx_unit = "{} / h".format(self.wrfs[i].rainnc_unit)
            self.wrfs[i].rainnx_loaded = True
            last = self.wrfs[i].rainnc
        print("Successfully calc'd field: {} ({}, {}x{})".format(field,self.wrfs[0].rainnx_unit,self.wrfs[0].rainnx.shape,self.count()))

    def calcDeltaField_SNOWNC(self):
        last = 0
        field="SNOWNX"
        for i in range(self.count()):
            self.wrfs[i].snownx = self.wrfs[i].snownc - last
            self.wrfs[i].snownx_unit = "{} / h".format(self.wrfs[i].snownc_unit)
            self.wrfs[i].snownx_loaded = True
            last = self.wrfs[i].snownc
        print("Successfully calc'd field: {} ({}, {}x{})".format(field,self.wrfs[0].snownx_unit,self.wrfs[0].snownx.shape,self.count()))





    def count(self):
        return len(self.wrfs)

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
    def loadDataSets(self):
        wrfs = []
        for fn in self.fullfilenames:
            wrf = WRFData(fn)
            wrfs.append(wrf)
        # for END
        return wrfs
    # def END

# Example usage:
# wrf = WRFDataTS("/path/to/folder")
# print(wrf.files)

