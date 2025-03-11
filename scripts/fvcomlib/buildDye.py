# buildwindECMWF.py
# ECMWF inpurt forcing generator for FVCOM
# VSF 2024
# Jari í Hjøllum
# Version 1.0 15-01-2025
#
#========IMPORT===================================================================
import os
import math
import array as arr # importing "array" for array creations
import fvcomlibio as io
import fvcomlibutil as u
import sys
import fvcomlibecmwf as ecmwf
import datetime as dt
from fvcomgrid import FVCOMGrid
from netCDF4 import Dataset
import numpy as np
from fvcomgribmap import FvcomGribMap
import fvcomgribmap as fgm
#========CONSTANTS - DO NOT EDIT====================================================
Version         = "1.0 (19-02-2025)"
VersionString   = "BuildDye v. {} by Jari í Hjøllum".format(Version)
ThisFileString  = "This file was generated at {}".format(u.generateNowTime())

nargs = len(sys.argv)
cmdparams = []
params = []
for i in range(nargs):
    cmdparams.append(sys.argv[i])
# for i END
if len(cmdparams)>1:
        params=u.parse_kv_pairs(cmdparams[1])
# if END

DEBUG = False
runnmlfile      = ""
dyelocations    = 1
dyesiglays      = "all" # Values, either levels, e.g. "1,2,3,4....10, or "all"
dyenodes        = "5000" # either single value or list of values "5000, 5001, 5002": Like: dyenodes="5000,50001,50002"
dyecoords       = "0,-1000", # either single pair or a number of pairs, "0,-1000,50,-1000,100,-1000" which is then converted into nodes.
dyeconc         = 1

if ("debug" in params):            DEBUG            = bool(int(params["debug"]))
if ("runnmlfile" in params):       runnmlfile       = params["runnmlfile"]
if ("dyelocations" in params):     dyelocations       = params["dyelocations"]
if ("dyesiglays" in params):       dyesiglays       = params["dyesiglays"]
if ("dyenodes" in params):         dyenodes       = params["dyenodes"]
if ("dyecoords" in params):        dyecoords       = params["dyecoords"]
if ("dyeconc" in params):          dyeconc       = params["dyeconc"]
...


# Open FVCOM initial conditions NetCDF file
filename = "casename_ini.nc"
nc = Dataset(filename, 'r+')

# Check if dye variable exists, otherwise create it
if 'dye_01' not in nc.variables:
    dye_var = nc.createVariable('dye_01', 'f4', ('time', 'siglay', 'node'))
    dye_var.long_name = "Dye concentration"
    dye_var.units = "kg/m3"
else:
    dye_var = nc.variables['dye_01']

# Set dye concentration (example: surface release at nodes 100-200)
dye_concentration = np.zeros((1, nc.dimensions['siglay'].size, nc.dimensions['node'].size))
dye_concentration[:, 0, 100:200] = 1.0  # Apply dye at the surface layer

# Write to NetCDF
dye_var[:] = dye_concentration
nc.close()
print("Dye initial conditions updated.")
