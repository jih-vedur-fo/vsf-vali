# fvcomlibio.py
# Wind generator for FVCOM 4.3 (Only works for 4.3 at this stage)
# COSUrFI 2024
# Jari í Hjøllum, Knud Simonsen
# Version 1.3 29-05-2024
#==================================================================
import netCDF4
#
# Reads a text file line by line.
def getFileContent(fn):
    s=""
    file1 = open(fn,'r')
    Lines = file1.readlines()
    for line in Lines:
        s=s+line
    return s
#
#
# Loads and returns the full dataset for a NetCDF4 file.
def getNetCDF4file(fn, printinfo=True):
    ds = netCDF4.Dataset(fn)
    if (printinfo==True):
        list(ds.variables)
    return ds
#
#
# Writes a text string to a file.
def writeFile(fn,s):
    f = open(fn, "w")
    f.write(s)
    f.close()
    
