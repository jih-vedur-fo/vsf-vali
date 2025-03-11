# extractsimdata.py - Extract Sim Data (ESD) for FVCOM
# Tested for version FVCOM 5.0.1 (intel) (X)
# Build: ifvcom501.org (@vsf.calc1)
# COSUrFI 2024
# Jari í Hjøllum, Knud Simonsen
# Version 1.10 05-11-2024
#
# This scripts plots data from a nc file.
# Edit:
# datapath  : The path of the input file.
# datafile    : The filename of the input file.
#
#========CONSTANTS - DO NOT CHANGE==============================================
#--------VERSION----------------------------------------------------------------
VERSION         = "1.10 (05-11-2024)"
#========IMPORT=================================================================
import os
import array as arr # importing "array" for array creations
import fvcomlibio as io
import fvcomlibutil as u
from fvcomgrid import FVCOMGrid
from fvcomdata import FVCOMData
import sys
import matplotlib
import numpy as np


#========CONSTANTS - DO NOT CHANGE==============================================
#--------VERSION----------------------------------------------------------------
VERSIONSTRING   = "ExtractSimData v. {} by Jari í Hjøllum, 2024".format(VERSION)
THISFILESTRING  = "This file was generated at {}".format(u.generateNowTime())
VIDEOFORMAT = ".mov"
VIDEOFORMAT = ".mp4"
#========Verbose/Debugging output===============================================
VERBOSE = True
#========CMDLINEPARAMS==========================================================
cmdparams = []
RunMode = "simple"
nargs = len(sys.argv)
print("Parameters ({}): ".format(nargs))
for i in range(nargs):
    print(sys.argv[i])

if (sys.argv[1] == "-file"):
    RunMode = "file"
    print("RunMode : {}".format(RunMode))
    for i in range(nargs):
        cmdparams.append(sys.argv[i])

#========CMDLINEPARAMS==========================================================

#========FILES - DO CHANGE==============================================
var = ""
x0 = -1
x1 = -1
y0 = -1
y1 = -1
title = -1
lagdatafile = "lag_out.nc"

if (RunMode == "simple"):
    #===INPUT FILES===
    datapath        = "../output/"
    datafile          = "san_0001.nc"
    var               = "velocity"

if (RunMode == "file"):
    print("FILE mode.")
    datapath          = "../output/"
    datafile          = "san_0001.nc"
    imagepath         = "../output/img/"
    imagefilemask     = "san"
    moviefilemask     = "san"
    var               = "velocity"

    params=u.parse_kv_pairs(cmdparams[2])
    print(list(dict.fromkeys(params)))
    for y in params:
        print (y,':',params[y])
    print("=======")


    if ("datapath" in params):        datapath          = params["datapath"]
    if ("datafile" in params):        datafile          = params["datafile"]
    if ("imagepath" in params):       imagepath         = params["imagepath"]
    if ("imagefilemask" in params):   imagefilemask     = params["imagefilemask"]
    if ("moviefilemask" in params):   moviefilemask     = params["moviefilemask"]
    if ("var" in params):             var               = params["var"]
    if ("x0" in params):              x0                = float(params["x0"])
    if ("x1" in params):              x1                = float(params["x1"])
    if ("y0" in params):              y0                = float(params["y0"])
    if ("y1" in params):              y1                = float(params["y1"])
    if ("title" in params):           title             = params["title"]
    if ("lagdatafile" in params):     lagdatafile       = params["lagdatafile"]


    imagefile          = "{}{}".format(imagefilemask,"-{:04}.png") # Do Not touch
    movieimagefilemask = "{}{}".format(imagefilemask,"-%04d.png")  # Do Not touch
    moviefile         = "{}{}".format(moviefilemask,VIDEOFORMAT) # Do Not touch

    print("Run/Input parameters:")
    print("Data path (datapath)            : {}".format(datapath))
    print("Data file (datafile)            : {}".format(datafile))
    print("Image path (imagepath)          : {}".format(imagepath))
    print("Image file mask (imagefilemask) : {}".format(imagefilemask))
    print("Movie file mask (moviefilemask) : {}".format(moviefilemask))
    print("Variable (var)                  : {}".format(var))
    print("==================\nDerived parameters:")
    print("Image file       : {}".format(imagefile))
    print("MI file mask     : {}".format(movieimagefilemask))




#========AUTOMATED - DO NOT CHANGE==============================================
datafilefull      = datapath+"/"+datafile
imagefilefull     = imagepath+"/"+imagefile
moviefilefull     = imagepath+"/"+moviefile
lagdatafilefull   = datapath+"/"+lagdatafile
#========PRINT==================================================================
if (VERBOSE):
    print("Data file     : {}".format(datafilefull))

#========PROGRAM==================================================================
d = FVCOMData()
d.loadvars = d.getLoadVars(var)
d.loadFile(datafilefull,False)
d.loadLagFile(lagdatafilefull,False)
d.getPlotData(0,0)
d.setPlotBlocking(False)
#d.setPlotBlocking(True)
matplotlib.use("Agg")
d.setPlotSize(12,12)
# Bounds
if ( x0 != -1 and x1 != -1):
    d.p_xbounds = [x0, y1]
if ( y0 != -1 and y1 != -1):
    d.p_ybounds = [y0, y1]


iSigLayer = 0
#for i in range(0,3):
for iTimeStep in range(d.times):
#for i in range(94,97):
#for i in range(50,51):
    print("Plotting time step no. {}".format(iTimeStep))
    d.loadPlotData(iTimeStep,iSigLayer)
    tstr = "Tíð: {} (MJD: {:9.3f})".format(u.MJD2datetime(d.time[iTimeStep]),d.time[iTimeStep])
    print(tstr)
    print("Plotting variable: {}".format(var))
    d.setVectors([],[])
    d.setVariableName(var)
    match var:
        case "u":
            d.setContour(d.u,d.u_kind,d.u_bounds)
        case "uwind":
            d.setContour(d.uwind,d.uwind_kind,d.BEAUFORTSCALE)
        case "v":
            d.setContour(d.v,d.v_kind,d.v_bounds)
        case "vwind":
            d.setContour(d.vwind,d.vwind_kind,d.BEAUFORTSCALE)
        case "velocity":
            d.setContour(d.velocity,d.velocity_kind,d.velocity_bounds)
        case "velocityvector":
            d.setContour(d.velocity,d.velocity_kind,d.velocity_bounds)
            d.setVectors(d.u,d.v)
            d.setVectorDelta(3000,3000)
            #d.setVectorColor('#026fbd')
            d.setVectorScale(d.WATERVECTORSCALE)
        case "windvelocity":
            d.setContour(d.windvelocity,d.windvelocity_kind,d.BEAUFORTSCALE)
        case "windvelocityvector":
            d.setContour(d.windvelocity,d.windvelocity_kind, d.BEAUFORTSCALE)
            d.setVectors(d.uwind,d.vwind)
            d.setVectorDelta(10000,10000)
            #d.setVectorColor('#8f5003')
            d.setVectorScale(d.WINDVECTORSCALE)
        case "salinity":
            d.setContour(d.salinity,d.salinity_kind,[34.5, 35.2])
        case "temp":
            d.setContour(d.temp,d.temp_kind,d.temp_bounds)
        case "z":
            d.setContour(d.z,d.z_kind,d.z_bounds)
        case "zeta":
            d.setContour(d.z,d.z_kind,d.z_bounds)
        case "shortwave":
            d.setContour(d.shortwave,d.shortwave_kind,d.shortwave_bounds)
        case "netheatflux":
            d.setContour(d.netheatflux,d.netheatflux_kind,d.netheatflux_bounds)
        case "precip":
            d.setContour(d.precip,d.precip_kind,d.precip_bounds,d.precip_unit,"μm/h")
            #print("PRECIP {:10.10e}".format(np.max(d.p_contourdata)))
            #sys.exit()
        case "evap":
            d.setContour(d.evap,d.evap_kind,d.evap_bounds,d.evap_unit,"μm/h")
        case "dye":
            d.setContour(d.dye,d.dye_kind,d.dye_bounds,d.dye_unit,"kg/m3")
        case _:
            print("ERROR: Unknown or NON-implemented variable ({}). Check spelling or implement the new variable.\nValid options are: u, uwind, v, vwind, velocity, velocityvector, windvelocity, windvelocityvector, salinity, temp, z, zeta.".format(var))
    # match END
    #d.p_levels=np.linspace(33,35.15,11)
    d.plot()
    # X and Y limits, should be changed to using d.bounds.... TODO.
    # Plot title - Default: variable name
    if (title == -1 ):
        title = "{:10s}".format(var)
    d.p_plt.title(title)

    #d.showColorbar()

    # Write extra label:
    d.p_plt.text(d.p_plottingbounds[0]*0.99, d.p_plottingbounds[3]*1.01, tstr, fontsize = 12, horizontalalignment='left',     verticalalignment='bottom')

    #d.p_plt.text(-60000, 70000, tstr, fontsize = 12)
    os.system("mkdir -p {}".format(imagepath))
    d.saveplot(imagefilefull.format(iTimeStep))

GenerateMPEG = True
if (GenerateMPEG):
    if ( VIDEOFORMAT==".mp4" ) :
        cmd = "ffmpeg -y -framerate 3 -i {}/{} -codec png  -vcodec libx264 -crf 22 {}".format(imagepath,movieimagefilemask,moviefilefull) # If MPEG is desired
    else: #MOV
        cmd = "ffmpeg -y -framerate 3 -i {}/{} -codec png {}".format(imagepath,movieimagefilemask,moviefilefull)
    os.system(cmd)

#ffmpeg -i crn2024-10-27-%04d.png -codec png out.mov


