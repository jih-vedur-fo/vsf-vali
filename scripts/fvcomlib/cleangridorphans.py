#!/home/jarih/miniconda3/bin/python

# cleangridorphans.py - Clean Grid Orphans (GCO) for FVCOM
# Tested for version FVCOM 5.0.1 (intel)
# Build: ifvcom501.wd.lag (@fvcom-u18-skeid)
# COSUrFI 2024
# Jari í Hjøllum, Knud Simonsen
# Version 1.7 11-06-2024
#========CONSTANTS - DO NOT CHANGE==============================================
#--------VERSION----------------------------------------------------------------
VERSION         = "1.7"
#========IMPORT=================================================================
import os
import array as arr # importing "array" for array creations
import fvcomlibio as io
import fvcomlibutil as u
from fvcomgrid import FVCOMGrid
#========CONSTANTS - DO NOT CHANGE==============================================
GCOSUFFIX = "_gco"
#--------VERSION----------------------------------------------------------------
VERSIONSTRING   = "CleanGridOrphans v. {} by Jari í Hjøllum, 2024".format(VERSION)
THISFILESTRING  = "This file was generated at {}".format(u.generateNowTime())
#========Verbose/Debugging output===============================================
VERBOSE = True
#===============================================================================
#===============================================================================
#========INIT===================================================================
#--------CASE-------------------------------------------------------------------
wcasename            = "nor"
#--------FILES------------------------------------------------------------------
#===INPUT FILES===
inbasepath        = "../norinp/"
#inbasepath        = "./"
gridfile        = "fvcom_noroyar_grd.dat"
#corfile         = "fvcom_foulgr1_cor.dat" # Use this option if you want to manually enter the 
#depfile         = "fvcom_foulgr1_dep.dat" # Use this option if you want to manually enter the 
#obcfile         = "fvcom_foulgr1_obc.cdl" # Use this option if you want to manually enter the 
#riverfile       = "fvcom_foulgr1_river.cdl" # Use this option if you want to manually enter the
#rivernmlfile    = "fvcom_foulgr1_river.nml" # Use this option if you want to manually enter the 
#spgfile         = "fvcom_foulgr1_spg.dat" # Use this option if you want to manually enter the 
#tidefile        = "fvcom_foulgr1_tide.cdl" # Use this option if you want to manually enter the 
corfile         = gridfile.replace("_grd.dat","_cor.dat")  # Use this option if the file obey the pattern _grd, _cor_, _dep, _tide, _river
depfile         = gridfile.replace("_grd.dat","_dep.dat")  # Use this option if the file obey the pattern _grd, _cor_, _dep, _tide, _river
obcfile         = gridfile.replace("_grd.dat","_obc.dat")  # Use this option if the file obey the pattern _grd, _cor_, _dep, _tide, _river
riverfile       = gridfile.replace("_grd.dat","_river.cdl")  # Use this option if the file obey the pattern _grd, _cor_, _dep, _tide, _river
rivernmlfile    = gridfile.replace("_grd.dat","_river.nml")  # Use this option if the file obey the pattern _grd, _cor_, _dep, _tide, _river
spgfile         = gridfile.replace("_grd.dat","_spg.dat")  # Use this option if the file obey the pattern _grd, _cor_, _dep, _tide, _river
tidefile        = gridfile.replace("_grd.dat","_tide.cdl")  # Use this option if the file obey the pattern _grd, _cor_, _dep, _tide, _river

#===OUTPUT FILES===
outbasepath        = "../norinp_cgo/"
gridfileout        = gridfile.replace("_grd.dat","_grd_cgo.dat")  # Use this option if the file obey the pattern _grd, _cor_, _dep, _tide, _river
corfileout         = gridfile.replace("_grd.dat","_cor_cgo.dat")  # Use this option if the file obey the pattern _grd, _cor_, _dep, _tide, _river
depfileout         = gridfile.replace("_grd.dat","_dep_cgo.dat")  # Use this option if the file obey the pattern _grd, _cor_, _dep, _tide, _river
obcfileout         = gridfile.replace("_grd.dat","_obc_cgo.dat")  # Use this option if the file obey the pattern _grd, _cor_, _dep, _tide, _river
riverfileout       = gridfile.replace("_grd.dat","_river_cgo.cdl")  # Use this option if the file obey the pattern _grd, _cor_, _dep, _tide, _river
rivernmlfileout    = gridfile.replace("_grd.dat","_river_cgo.nml")  # Use this option if the file obey the pattern _grd, _cor_, _dep, _tide, _river
spgfileout         = gridfile.replace("_grd.dat","_spg_cgo.dat")  # Use this option if the file obey the pattern _grd, _cor_, _dep, _tide, _river
tidefileout        = gridfile.replace("_grd.dat","_tide_cgo.cdl")  # Use this option if the file obey the pattern _grd, _cor_, _dep, _tide, _river
orphanfileout      = gridfile.replace("_grd.dat","_orp_cgo.dat")
orphantxtfileout   = gridfile.replace("_grd.dat","_orp_cgo.txt")

#lagfilecdl      = "ulg_lag_init.cdl" #Output cdl file for NetCDF generation
#lagfilenc       = "ulg_lag_init.nc" #Output NetCDF file
#========LAG SETUP==============================================================
#========CHECKS=================================================================
#========AUTOMATED - DO NOT CHANGE==============================================
gridfilefull      = inbasepath+gridfile
corfilefull       = inbasepath+corfile
depfilefull       = inbasepath+depfile
obcfilefull       = inbasepath+obcfile
riverfilefull     = inbasepath+riverfile
rivernmlfilefull  = inbasepath+rivernmlfile
spgfilefull       = inbasepath+spgfile 
tidefilefull      = inbasepath+tidefile

gridfileoutfull       = outbasepath+gridfileout
corfileoutfull        = outbasepath+corfileout
depfileoutfull        = outbasepath+depfileout
obcfileoutfull        = outbasepath+obcfileout
riverfileoutfull      = outbasepath+riverfile
rivernmlfileoutfull   = outbasepath+rivernmlfileout
spgfileoutfull        = outbasepath+spgfileout
tidefileoutfull       = outbasepath+tidefileout
orphanfileoutfull     = outbasepath+orphanfileout
orphantxtfileoutfull  = outbasepath+orphantxtfileout
#========PRINT==================================================================
if (VERBOSE):
    print("Grid file     : {}".format(gridfilefull))
    print("Coriolis file : {}".format(corfilefull))
    print("Depth file    : {}".format(depfilefull))
    print("OBC file      : {}".format(obcfilefull))
    print("River file    : {}".format(riverfilefull))
    print("River NML file: {}".format(rivernmlfilefull))
    print("Sponge file   : {}".format(spgfilefull))
    print("Tide file     : {}".format(tidefilefull))
#========PROGRAM==================================================================
    d = FVCOMGrid()
    d.loadGridFile(gridfilefull)
    d.loadCorFile(corfilefull)
    d.loadDepFile(depfilefull)
    d.loadSpgFile(spgfilefull)
    d.loadObcFile(obcfilefull)
    d.loadTideCdlFile(tidefilefull)
    d.loadRiverNmlFile(rivernmlfilefull)
    # ==============================================
    # === If you want find orphans ... lengthly! ===
    #d.checkOrphanNodes()
    #d.writeOrphansTxtFile(orphantxtfileoutfull)
    #d.writeOrphanDictionary(orphanfileoutfull)
    # ==============================================
    # === If you want to load orphan list ==========
    d.readOrphanDictionary(orphanfileoutfull)
    # === ===
    # ==============================================
    d.reindexOrphans()
    d.writeGridFile(gridfileoutfull)
    d.writeCorFile(corfileoutfull)
    d.writeDepFile(depfileoutfull)
    d.writeSpgFile(spgfileoutfull)
    d.writeObcFile(obcfileoutfull)
    d.writeTideCdlFile(tidefileoutfull)
    d.buildTideNetcdfFile(tidefileoutfull)
    d.writeRiverNmlFile(rivernmlfileoutfull,GCOSUFFIX)
        
    print("End of program.")



