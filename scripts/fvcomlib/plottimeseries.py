# plottimeseries.py - Extract Sim Data (ESD) for FVCOM
# Tested for version FVCOM 5.0.1 (intel)
# Build: ifvcom501.wd.lag (@fvcom-u18-skeid)
# VSF 2024
# Jari í Hjøllum, Knud Simonsen
#
# This scripts extracts data from a nc file and into a csv file.
# Edit:
# inbasepath  : The path of the input file.
# datafile    : The filename of the input file.
# outbasepath : The path of the output file.
# outcsvfile  : The filename of the output file.
# separator   : The separator (one character) separating the data columns.
#
#========CONSTANTS - DO NOT CHANGE==============================================
#--------VERSION----------------------------------------------------------------
VERSION         = "1.1"
#========IMPORT=================================================================
import os
import array as arr # importing "array" for array creations
import sys
sys.path.insert(1, '../scripts/')
import fvcomlibio as io
import fvcomlibutil as u
from fvcomgrid import FVCOMGrid
from fvcomdata import FVCOMData
#========CONSTANTS - DO NOT CHANGE==============================================
#--------VERSION----------------------------------------------------------------
VERSIONSTRING   = "PlotTimeSeries v. {} by Jari í Hjøllum, 2025".format(VERSION)
THISFILESTRING  = "This file was generated at {}".format(u.generateNowTime())
#========Verbose/Debugging output===============================================
VERBOSE = True
#========FILES - DO CHANGE==============================================
#===INPUT FILES===
inbasepath        = "../output/"
datafile          = "far2024-12-01.nc"
outbasepath       = "./"
outcsvfile        = "out.dat"
outpngfile        = "out.png"
separator         = " " # columnseparator space ( ), comma (,), semicolon (;), tab (\t)
#========AUTOMATED - DO NOT CHANGE==============================================
indatafilefull      = inbasepath+datafile
outcsvfilefull      = outbasepath+outcsvfile
outpngfilefull      = outbasepath+outpngfile
#========PRINT==================================================================
print(VERSIONSTRING)
if (VERBOSE):
    print("Data file     : {}".format(indatafilefull))
    print("Out file      : {}".format(outcsvfilefull))
#========PROGRAM==================================================================
    d = FVCOMData()
    d.loadFile(indatafilefull)
    d.setPlotBlocking(False)
    d.setPlotAGG(True)
    d.getData([152620,152621,152622],['velocity','u','v'],[0,1,2,3,4,5,6,7,8,9])
    #d.getData([152621,152622],['velocity','u','v'],[0])
    #d.getData([152621],['velocity'],[0,1,2,3])
    #d.getData([152621],['velocity'],[0])
    d.setPlotSize(12,12)
    d.exportcsv(outcsvfilefull,separator)
    print("Time size: {}.".format(d.d_datatitle.shape))
    print("Data size: {}.".format(d.d_datahandle.shape))
    print("Data[0] size: {}.".format(len(d.d_datahandle[0])))
    print("Data[1] size: {}.".format(len(d.d_datahandle[1])))
    d.p_showlegend=True


    d.p_ylabel="Speed u, v (m/s)"
    d.p_xlabel="MJD"
    d.plotScatter()
    d.saveplot(outpngfilefull)




