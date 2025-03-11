# lagconvert.py
# LAG data converter for TecPlot 
# Input files are FVCOM _lag files in .nc-format.
# Only tested for:
#      - FVCOM 5.0.1 (intel, ifvcom.wd.river.lag @fvcom-u18-skeid)
#
# COSUrFI 2024
# All rights reserved, Jari í Hjøllum, Knud Simonsen.
# Version 1.3 29-04-2024
#
#========IMPORT===================================================================
import os
import array as arr # importing "array" for array creations
import netCDF4
import numpy as np
import fvcomlibio as io
import fvcomlibutil as u

#========INIT===================================================================
#--------CASE-------------------------------------------------------------------
casename            = "tse"
#--------FILES------------------------------------------------------------------
basepath        = "../output/"
fromfile        = "tse0001_run02_lag.nc" #Input file, LAG-data in .ncformat, for conversion.
tofile          = "tse0001_run02_lag.dat" #Output file for NetCDF generation
#-------- CONVERSION SETTINGS---------------------------------------------------
timeoffset      = 0 # If necessary to subtract an time offset, set it here.
#-------- ON SCREEN OUTPUT------------------------------------------------------
verbose = True # True/False. If the output to screen should be verbose.
#--------PROGRAM START----------------------------------------------------------

fromfilefull = basepath+fromfile
tofilefull=basepath+tofile
#ds = netCDF4.Dataset(fromfilefull)
ds = io.getNetCDF4file(fromfilefull,verbose) 
time=ds.variables['time']
time=np.subtract(time,timeoffset)
x=ds.variables['x']
y=ds.variables['y']
z=ds.variables['z']
n=time.size
nx = len(x[0])
ny = len(x[0])
nz = len(x[0])
if (verbose==True):
    print("== File info: ==")
    print("Filename (from)        : {}".format(fromfilefull))
    print("Filename (to)          : {}".format(tofilefull))
    print("Number of time steps   : {}".format(n))
    print("Number of x time steps : {}".format(len(x)))
    print("Size of x-element      : {}".format(len(x[0])))
    print("Number of y time steps : {}".format(len(y)))
    print("Size of y-element      : {}".format(len(y[0])))
    print("Number of y time steps : {}".format(len(z)))
    print("Size of x-element      : {}".format(len(z[0])))

#Init the output string array    
ss = [] # Array of strings to be joined later
ss.append("VARIABLES = \"x\",\"y\",\"z\"\n")
          

#Add data to output array
for i in range(n):
    ss.append("ZONE I={}, F=BLOCK, SOLUTIONTIME={}\n".format(nx,time[i]))
    t=[]
    xs=x[i]
    ys=y[i]
    zs=z[i]
    for j in range(nx):
      t.append("{}, ".format(xs[j]))
    t.append("\n")
    for j in range(ny):
      t.append("{}, ".format(ys[j]))
    t.append("\n")           
    for j in range(nz):
      t.append("{}, ".format(zs[j]))
    t=("".join(t)).strip()
    t = u.replaceLastChar(t,"\n")
    ss.append(t)
    ss.append("\n")
          
          
          

s="{}".format("".join(ss))
io.writeFile(tofilefull,s)
print("Output successfully written to file {}".format(tofilefull))




 

