# extractsimdata.py - Extract Sim Data (ESD) for FVCOM
# Tested for version FVCOM 5.0.1 (intel)
# VSF 2024
# Jari í Hjøllum, Knud Simonsen
# Version 1.7 11-06-2024
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
VERSION         = "1.7"
#========IMPORT=================================================================
import os
import array as arr # importing "array" for array creations
import fvcomlibio as io
import fvcomlibutil as u
from fvcomgrid import FVCOMGrid
from fvcomdata import FVCOMData
#========CONSTANTS - DO NOT CHANGE==============================================
#--------VERSION----------------------------------------------------------------
VERSIONSTRING   = "ExtractSimData v. {} by Jari í Hjøllum, 2024".format(VERSION)
THISFILESTRING  = "This file was generated at {}".format(u.generateNowTime())
#========Verbose/Debugging output===============================================
VERBOSE = True
#========FILES - DO CHANGE==============================================
#===INPUT FILES===
inbasepath        = "/home/jarih/Data/data2_internal/Data/fvcom/remotemachines/fvcom-u18/UttariLandgrunnur/ulg0005/output/"
datafile          = "ulg0005_run05.nc"
outbasepath       = "./"
outcsvfile        = "out.dat"
separator         = " " # columnseparator space ( ), comma (,), semicolon (;), tab (\t)
#========AUTOMATED - DO NOT CHANGE==============================================
indatafilefull      = inbasepath+datafile
outcsvfilefull      = outbasepath+outcsvfile
#========PRINT==================================================================
if (VERBOSE):
    print("Data file     : {}".format(indatafilefull))
    print("Out file      : {}".format(outcsvfilefull))
#========PROGRAM==================================================================
    d = FVCOMData()
    d.loadFile(indatafilefull)
    d.getData([21,42],['u','v'])
    d.exportcsv(outcsvfilefull,separator)

