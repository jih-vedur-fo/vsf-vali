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
from gribdata import GRIBData
import numpy as np
from fvcomgribmap import FvcomGribMap
import fvcomgribmap as fgm
#========CONSTANTS - DO NOT EDIT====================================================
Version         = "1.0 (15-01-2025)"
VersionString   = "BuildWindECMWF v. {} by Jari í Hjøllum".format(Version)
ThisFileString  = "This file was generated at {}".format(u.generateNowTime())
#========CONSTANTS - YOU MAY EDIT===================================================================
# --- WHILE TESTING SET THIS TRUE ---
DEBUG = False # Only generates data for 20 cells. Use while debugging
#DEBUG = True # Only generates data for 20 cells. Use while debugging
# --- GIVE MORE OUTPUT ---
VERBOSE = True # True / False
TEXTRA = 0.1
TimeFloatStrMask = "{:.4f}"
WindFloatStrMask = "{:.4f}"
#========INIT===================================================================
#========CMDLINEPARAMS==========================================================
Mode = "simple"
nargs = len(sys.argv)
cmdparams = []
params = []
for i in range(nargs):
    print(sys.argv[i])
#========================================================
if (sys.argv[1] == "-csv"):
    Mode = "csv"
    CSVFilename    = sys.argv[2]
    print("CSV mode. Input file : {}".format(CSVFilename))
#==========================================================
if (sys.argv[1].lower() == "-ecmwf"):
    Mode = "ecmwf"
    print("ECMWF mode.")

    for i in range(nargs):
        cmdparams.append(sys.argv[i])
    if len(cmdparams)>2:
        params=u.parse_kv_pairs(cmdparams[2])

#========CMDLINEPARAMS==========================================================

#--------CASE-------------------------------------------------------------------
casename            = "san"
#--------FILES------------------------------------------------------------------
basepath        = "../saninp/"
gridfile        = "fvcom_lgr_san_grd.dat" #Input file, grid, for NetCDF generation
headerfile      = "buildwindECMWF_base.cdl" #Input file, NetCDF header, for NetCDF header  -- DO NOT CHANGE LIGHTLY!!!
heatingfile     = "buildwindECMWF_base_heating.cdl" #Input file, NetCDF header, for NetCDF header  -- DO NOT CHANGE LIGHTLY!!!
windfile        = "fvcom_lgr_san_wnd.cdl" #Output file for NetCDF generation
ncwindfile      = "fvcom_lgr_san_wnd.nc" #Output file for NetCDF generation
saveimages      = 0 #
heatingactive   = 0 # Generate Heating Forcing into the nc-file


#========WIND SETUP===================================================================
TimeUnit    = 'day' # Unit of T. Can be changed. Must be either 'hour' or 'day' or 'second'
# TN Number of programmed time steps. First and last should be determined by T0 and T9.
TN          = 97
# T0 This is the first time value.
#    Take care to let his be in units of TimeUnit.
T0          = 60636
# T9 This is the last value. Make sure it is in the far future, long
#    after the simulatlion is done.
#    Take care to let his be in units of TimeUnit.
T9          = 60640
# T_ZERO Must be either 'MJD', 'MJD_2000' or 'MJD_2023. MJD is recommended.
T_ZERO      = "MJD"
# TIME_ZONE Use either 'none' or 'UTC' here. 'none' is recommended.
TIME_ZONE   = 'none'
timestepsperday = 24


if ("basepath" in params):         basepath         = params["basepath"]
if ("gridfile" in params):         gridfile         = params["gridfile"]
if ("headerfile" in params):       headerfile       = params["headerfile"]
if ("windfile" in params):         windfile         = params["windfile"]
if ("ncwindfile" in params ):      ncwindfile       = params["ncwindfile"]
if ("TN" in params ):              TN               = float(params["TN"])
if ("T0" in params ):              T0               = float(params["T0"])
if ("T9" in params ):              T9               = float(params["T9"])
if ("timestepsperday" in params ): timestepsperday  = float(params["timestepsperday"])
if ("saveimages" in params ):      saveimages       = int(params["saveimages"])
if ("heatingactive" in params ):   heatingactive    = int(params["heatingactive"])



#--------AUTOMATED---------------------------------------------------------------
gridfilefull    = u.addFileToPath(basepath,gridfile)
headerfilefull  = headerfile # Should be in same path as this py file.
heatingfilefull = heatingfile # Should be in same path as this py file.
windfilefull    = u.addFileToPath(basepath,windfile) # Output file
ncwindfilefull  = u.addFileToPath(basepath,ncwindfile) # Output NC file

fromDateTime=u.MJD2datetime(T0)
toDateTime=u.MJD2datetime(T9)
gd = GRIBData()
gd.loadData(fromDateTime, toDateTime, 58, 66, -18, 0.5)
