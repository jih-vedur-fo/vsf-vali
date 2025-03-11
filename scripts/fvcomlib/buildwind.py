# buildwind.py
# Wind generator for FVCOM
# VSF 2024
# Jari í Hjøllum
# Version 1.11 20-11-2024
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
Version         = "1.11 (20-11-2024)"
VersionString   = "BuildWind v. {} by Jari í Hjøllum, 2024".format(Version)
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
headerfile      = "buildwind_base.cdl" #Input file, NetCDF header, for NetCDF header  -- DO NOT CHANGE LIGHTLY!!!
windfile        = "fvcom_lgr_san_wnd.cdl" #Output file for NetCDF generation
ncwindfile      = "fvcom_lgr_san_wnd.nc" #Output file for NetCDF generation
saveimages      = 0 #


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


#--------AUTOMATED---------------------------------------------------------------
gridfilefull    = u.addFileToPath(basepath,gridfile)
headerfilefull  = headerfile # Should be in same path as this py file.
windfilefull    = u.addFileToPath(basepath,windfile) # Output file
ncwindfilefull  = u.addFileToPath(basepath,ncwindfile) # Output NC file
#========================================================================================
#========BEGIN OF SIMPLE=================================================================
#========================================================================================
if (Mode == "simple"):
    WindMax     = 10 # Wind speed in units of m/s
    # T In units of chosen unit. NB.: First element must have value less than starting value of simulation. Last after end of simulation.
    T = arr.array('d',[T0] + u.ramps([1/24,  4 - 1/24],[94]) +[T9-T0] )
    print("Length of T array           : {}".format(len(T)))
    # WindProfile In units of chosen unit.
    WindProfile = [0.0] +u.ramps([0.0,WindMax,0.0],[47,47]) + [0.0]
    print("Length of WindProfile array : {}".format(len(WindProfile)))
    # WindProfile = np.array(WindProfile)
    WindAngle = 162.4 # í mun til eystan
    WindAngle = [0.0] +u.ramps([0.0,90,0.0],[47,47]) + [0.0]
    print("Length of WindProfile array : {}".format(len(WindAngle)))

    #===AUTO BEGIN=================================================
    WAX = arr.array('d',[0]*TN ) # In units of WindMax
    WAY = arr.array('d',[0]*TN ) # In units of WindMax
    WX = arr.array('d',[0]*TN ) # In units of WindMax
    WY = arr.array('d',[0]*TN ) # In units of WindMax
    for i in range(TN):
        WAX[i] = -math.cos(WindAngle[i]/180*math.pi)# DO NOT CHANGE
        WAY[i] = -math.sin(WindAngle[i]/180*math.pi)# DO NOT CHANGE
    for i in range(TN):
        WX[i]=WAX[i]*WindProfile[i]
        WY[i]=WAY[i]*WindProfile[i]
    #===AUTO END===
#========================================================================================
#========END OF SIMPLE===================================================================
#========================================================================================

#========================================================================================
#========BEGIN OF CSV====================================================================
#========================================================================================
if (Mode == "csv"):
    # Open the file in read mode
    csvheaderlength=1
    n = 0
    d_date = []
    d_mjd = []
    d_windspeed = []
    d_winddir   = []
    #===Load =======================================
    with open(CSVFilename, 'r') as file:
        # Read each line in the file
        for line in file:
            line=line.strip()
            if (len(line)>0):
                n = n + 1
                print(line)
                if (n > csvheaderlength):
                    d = line.split(",")
                    d_date.append(d[0])
                    d_mjd.append(float(d[1]))
                    d_windspeed.append(float(d[2]))
                    d_winddir.append(float(d[3]))
    print("Loading wind file done.")

    #Find first time step
    print("Finding first time step...")
    i = 1
    w_istart = 0
    while (i < len(d_mjd) ):
        if (d_mjd[w_istart]>T0):
            print("ERROR: Start MJD in CSV larger than T0.[{} and {}]".format(d_mjd[w_istart],T0))
            sys.exit()
        # if END
        if (d_mjd[i] > T0 and (d_mjd[i-1] < T0)):
            w_istart=i-1
            print("Start MJD: {}".format(d_mjd[w_istart]))
        # if END
        i = i +1
    # while END


    #Find last time step
    print("Finding last time step...")
    i = w_istart
    w_iend = 0
    while (i < len(d_mjd) ):

        if (d_mjd[i] < T9):
            w_iend = i
            print("New end value found: {}".format(d_mjd[w_iend]))

        if (d_mjd[i] > T9 and d_mjd[i-1] < T9):
            print("Best value found: {}".format(d_mjd[w_iend]))
            break
        i = i +1
    # END while (i < len(d_mjd) ):

    #Adding additional end value if needed
    print("Checking if additional time is needed...")
    if (d_mjd[w_iend] < T9 ):
        d_mjd.append(T9+TEXTRA)
        d_windspeed.append(d_windspeed[w_iend])
        d_winddir.append(d_winddir[w_iend])
        w_iend = w_iend + 1
        print("Added new end record with MJD: {}.".format(d_mjd[w_iend]))
        print("Extra End MJD:   {}".format(d_mjd[w_iend]))

    #===Check wind directions=====================================================
    print("Checking wind direction values...")
    (d_winddir, nchanges) = u.correctWindDirection(d_winddir,w_istart,w_iend)
    print("Check done. {} changes made.".format(nchanges))




    #===Generate per hour steps=========================
    print("Generating time (default: per hour) steps ...")
    ts = [] # ime steps
    ws = [] # Wind speed
    wd = [] # Wind direction
    for i in range(w_istart,w_iend):
        nsteps = int((d_mjd[i+1] - d_mjd[i])*timestepsperday)
        print("From {} to {} in {} steps".format(d_mjd[i],d_mjd[i+1],nsteps))
        tmp = u.ramp(d_mjd[i],d_mjd[i+1],nsteps)
        ts.extend(tmp)
        tmp = u.ramp(d_windspeed[i],d_windspeed[i+1],nsteps)
        ws.extend(tmp)
        tmp = u.ramp(d_winddir[i],d_winddir[i+1],nsteps)
        wd.extend(tmp)



    #===Assign lists to arrays================================================
    T = arr.array('d',ts )
    TN = len(T)
    print("Length of T array           : {}".format(len(T)))
    print(["{:.2f}".format(x) for x in ts])
    # WindProfile In units of chosen unit.
    WindProfile = ws
    print("Length of WindProfile array : {}".format(len(WindProfile)))
    print(["{:.1f}".format(x) for x in ws])
    # WindProfile = np.array(WindProfile)
    WindAngle = 162.4 # í mun til eystan
    # Transform from North clockwise to East CounterClockwise
    for i in range(len(wd)):
        wd[i] = (-wd[i] + 90 )
    WindAngle = wd
    print("Length of WindProfile array : {}".format(len(WindAngle)))
    print(["{:.1f}".format(x) for x in wd])
    #===AUTO BEGIN=================================================
    WAX = arr.array('d',[0]*TN ) # In units of WindMax
    WAY = arr.array('d',[0]*TN ) # In units of WindMax
    WX = arr.array('d',[0]*TN ) # In units of WindMax
    WY = arr.array('d',[0]*TN ) # In units of WindMax
    for i in range(TN):
        WAX[i] = -math.cos(WindAngle[i]/180*math.pi)# DO NOT CHANGE
        WAY[i] = -math.sin(WindAngle[i]/180*math.pi)# DO NOT CHANGE
    for i in range(TN):
        WX[i]=WAX[i]*WindProfile[i]
        WY[i]=WAY[i]*WindProfile[i]
    #===AUTO END===



#sys.exit()
#========================================================================================
#========END OF CSV======================================================================
#========================================================================================

#========================================================================================
#========BEGIN OF ECMWF==================================================================
#========================================================================================
if (Mode == "ecmwf"):
    fromDateTime=u.MJD2datetime(T0)
    toDateTime=u.MJD2datetime(T9)
    gd = GRIBData()
    gd.loadData(fromDateTime, toDateTime, 58, 66, -18, 0.5)

    #(timesteps, lat, lon, x, y, mslp, gd.u10, v10, t2, c1, c2, c3) = ecmwf.get_ecmwf_FVCOMdata(fromDateTime, toDateTime,58, 66, -18, 0.5)
    #d_mjd = []
    #print("Converting datetime to MJD ...")
    #for i in range(len(timesteps)):
        #d_mjd.append(u.datetime2MJD(timesteps[i]))
        #print("{} -> {}".format(timesteps[i],d_mjd[i]))


    #Find first time step
    print("Finding first time step ...")
    i = 1
    w_istart = 0
    while (i < len(gd.mjd) ):
        if (gd.mjd[w_istart]>T0):
            print("ERROR: Start MJD in ECMWF larger than T0.[{} and {}]".format(gd.mjd[w_istart],T0))
            sys.exit()

        if (gd.mjd[i] > T0 and (gd.mjd[i-1] < T0)):
            w_istart=i-1
            print("Start MJD (temp): {}".format(gd.mjd[w_istart]))

        i = i +1
    # END while (i < len(gd.mjd) ):
    print("Start MJD: {}".format(gd.mjd[w_istart]))



    # ===Find last time step=======================================================
    print("Finding last time step...")
    w_iend = gd.findLastTimeStep(w_istart,T9)
    #
    # ===Adding additional end value if needed==================================
    w_iend=gd.checkAppend(["ws","wd"],w_iend,T9,TEXTRA)
    #
    # === Create new dataset with only selected data
    gdx=gd.exportWindForcingData(w_istart,w_iend)

    #============================================================
    # Printing U10 , V10, WS, WD Matrices
    print("Print U10 V10 WS WD data ...")
    u.printMatrix2x2(["U10","V10","WS ","WD "],gd.u10,gd.u10,gd.ws,gd.wd)
    u.printMatrix2x2(["U10","V10","WS ","WD "],gdx.u10,gdx.u10,gdx.ws,gdx.wd)

    # Checking ECMWF DATA and positioning
    print("Checking ECMWF DATA and positioning...")
    i0 = 19 # lat
    j0 = 54 # lon
    inmax = 3
    jnmax = 3
    for i in range(inmax):
        pstr = "P (i,j)=({:2d},{:2d}-{:2d}): (lat,lon)=".format(i+i0,j0,jnmax+j0-1)
        bstr = "B i={:2d} (lat,lon)=".format(0)
        cstr = "C j={:2d} (lat,lon)=".format(0)
        for j in range(jnmax):
            pstr = pstr+"({:6.2f},{:6.2f}) ".format(gdx.lat[i+i0,j+j0], gdx.lon[i+i0,j+j0])
            bstr = bstr+"({:6.2f},{:6.2f}) ".format(gdx.lat[i+i0,0]   , gdx.lon[i+i0,0]   )
            cstr = cstr+"({:6.2f},{:6.2f}) ".format(gdx.lat[0,j+j0]   , gdx.lon[0,j+j0]   )
        print(pstr)

    for i in range(inmax):
        xstr = "X (i,j)=({:2d},{:2d}-{:2d}): (  x,  y)=".format(i+i0,j0,jnmax+j0-1)
        for j in range(jnmax):
            xstr = xstr+"({:8.1f},{:8.1f}) ".format(gdx.x[i+i0,j+j0],   gdx.y[i+i0,j+j0])
        print(xstr)

    insertFakeValue = False
    if (insertFakeValue):
        for t in range(gdx.ws.shape[2]):
            gdx.ws[1+i0,1+j0,t]=50
            gdx.wd[1+i0,1+j0,t]=0
    for i in range(inmax):
        wstr = "W (i,j)=({:2d},{:2d}-{:2d}): ( ws, wd)=".format(i+i0,j0,jnmax+j0-1)
        for j in range(jnmax):
            wstr = wstr+"({:8.1f},{:8.1f}) ".format(gdx.ws[i+i0,j+j0,0],   gdx.wd[i+i0,j+j0,0])
        print(wstr)

    #
    #===Check wind directions=====================================================
    print("Checking wind direction values...")
    (gdx.wd, nchanges) = u.correctWindDirection3D(gdx.wd)
    print("Check done. {} changes made.".format(nchanges))
    #
    #===Generate per hour steps=========================
    print("Generating time (default: per hour) steps (interpolation)...")
    if VERBOSE: gdx.printExample_ws_ws_u10_v10("gdx")
    gdr = gdx.createRamps(["ws","wd"],timestepsperday)
    #
    # Assign to T array
    print("Assigning T array ...")
    T = np.copy(gdr.mjd)
    TN = len(T)
    print("Length of T array           : {}".format(len(T)))
    #
    #======================================================================
    # Load FVCOM grid
    print("Loading FVCOM grid ...")
    fvcomgrd = FVCOMGrid()
    fvcomgrd.loadGridFile(gridfilefull)
    xx = 100 # temp variable
    #======================================================================
    # Printing GRIB Matrix
    #gdx.printGRIBMatrix()

    #
    #======================================================================
    # FVCOM to GRIB MAP
    print("Creating mapping from GRIB to FVCOM ...")
    fgmap = FvcomGribMap(fvcomgrd,gdx) # Maybe we could use gdr here instead?
    fgmap.buildMap()
    #windPol = fgmap.transmapWindPolar(gdr,"simple")
    #windPol = fgmap.transmapWindPolar(gdr,"1D")
    windPol = fgmap.transmapWindPolar(gdr,"gauss")
    #
    print("Calculating WX and WY ...")
    windXY = fgmap.calcWindCartesian()
    #u.calcWindXY(WS,WD) # Calculates the X and Y values and transforms the NorthCW to EastCCW.
    #(WX, WY) = u.calcWindXY(WS,WD) # Calculates the X and Y values and transforms the NorthCW to EastCCW.
    WX = windXY.X
    WY = windXY.Y

    #
    print("Print WS WD WX WY data ...")
    #u.printMatrix2x2(["WS","WD","WX","WY"],WS,WD,WX,WY)
    print("Plotting forcing data ...")
    if (saveimages==1):
        for i in range(len(windXY.T)):
            fgmap.plot("ws",i)
            fgmap.plot("wd",i)
            #fgmap.plot("wx",i)
            #fgmap.plot("wy",i)





#========================================================================================
#========END OF ECMWF====================================================================
#========================================================================================


if (Mode == "simple" or Mode == "csv"):
    #========CHECKS===================================================================
    if (len(WX)!=TN):
        print("\nERROR: WX Dimensions differ from number of time steps!!! {} vs. {}\n".format(len(WX),TN))
    if (len(WY)!=TN):
        print("\nERROR: WY Dimensions differ from number of time steps!!! {} vs. {}\n".format(len(WY),TN))

    #--------AUTOMATED -  DO NOT CHANGE------------------------------------------------------
    T_MJD      = 0     # Number of days since 1858-11-17 00:00:00 to 01-01-2000 at 00:00:00 [http://www.csgnetwork.com/julianmodifdateconv.html & https://scienceworld.wolfram.com/astronomy/ModifiedJulianDate.html]
    T_MJD_2000 = 51544 # Number of days since 1858-11-17 00:00:00 to 01-01-2000 at 00:00:00 [http://www.csgnetwork.com/julianmodifdateconv.html & https://scienceworld.wolfram.com/astronomy/ModifiedJulianDate.html]
    T_MJD_2023 = 59945 # Number of days since 1858-11-17 00:00:00 to 01-01-2000 at 00:00:00 [http://www.csgnetwork.com/julianmodifdateconv.html & https://scienceworld.wolfram.com/astronomy/ModifiedJulianDate.html]
    T_ORIGIN   = 0 # Default value - should not be used.
    T_comment  = "T_ORIGIN = 0; The value should never be this."
    if (T_ZERO=="MJD"):
        T_ORIGIN = T_MJD
        T_comment = "Number of days since 1858-11-17 00:00:00. T_ORIGIN = T_MJD"
    if (T_ZERO=="MJD_2000"):
        T_ORIGIN = T_MJD_2000
        T_comment = "Number of days since 1858-11-17 00:00:00. T_ORIGIN = T_MJD_2000"
    if (T_ZERO=="MJD_2023"):
        T_ORIGIN = T_MJD_2023
        T_comment = "Number of days since 1858-11-17 00:00:00. T_ORIGIN = T_MJD_2023"
    #============
    # Printing time steps one day apart: Seldom used.
    printdaytimesteps = False
    if (printdaytimesteps) :
        x=[]
        for i in range(32):
            x.append("{}, ".format(i+T_ORIGIN))
        print("{} ".format("".join(x)))
    #============

    TimeUnitVal = 1
    if (TimeUnit=='day'):
        TimeUnitVal = 1
    if (TimeUnit=='hour'):
        TimeUnitVal = u.DAYSPERHOUR
    if (TimeUnit=='second'):
        TimeUnitVal = u.DAYSPERSECOND;

    for i in range(TN):
        T[i] = T[i]*TimeUnitVal
    #OLDfor i in range(1,TN):
    #OLD    T[i] = T[i] + T0 *TimeUnitVal
    for i in range(TN):
        T[i] = T[i] + T_ORIGIN

    #T = T * TimeUnitVal
    # for i in range(TN):
    #     WX[i] = WX[i] * WindMax
    #     WY[i] = WY[i] * WindMax
    #========PRINT===================================================================
    print("T array has {} elements.".format(len(T)))
    print("T:           \n{}".format(u.printArray(T,"{:.3f}")))
    print("Windprofile: \n{}".format(u.printArray(WindProfile,"{:.2f}")))
    print("WindprofileX:\n{}".format(u.printArray(WX,"{:.2f}")))
    print("WindprofileY:\n{}".format(u.printArray(WY,"{:.2f}")))
    #========PROGRAM==================================================================
# if simple or csv END
elif (Mode == "ecmwf"):
    node = int(fvcomgrd.nodecount)
    nele = fvcomgrd.cellcount
    T_comment = "Number of days since 1858-11-17 00:00:00. T_ORIGIN = T_MJD"

run = 1
if (run==1):
    print(VersionString)
    #
    if (Mode == "simple" or Mode == "csv"):
        print("Opening grid file: \"{}\":".format(gridfilefull))
        # Using readlines()
        file1 = open(gridfilefull, 'r')
        Lines = file1.readlines()
        N = len(Lines)
        d = [""]*N
        print("Lines in file: {}".format(N))
        count = 0
        # Strips the newline character
        for line in Lines:
            count += 1
            d[count-1]=line
        #
        if (VERBOSE): print("Number of lines read: {}".format(count))
        #
        for i in range(3):
            if (VERBOSE): print("Reading line: {}...".format(i))
            if (VERBOSE): print("L{}        : [{}].".format(i,d[i][:-1])  )
            if (d[i].find("Node Number =")>-1):
                print("Node number found at line {}.".format(i))
                nodeNumber = d[i].split("=",1)[1].strip()
                node = int(nodeNumber)
                print("Number of nodes: {}".format(node))
            if (d[i].find("Cell Number =")>-1):
                print("Cell number found at line {}.".format(i))
                cellNumber = d[i].split("=",1)[1].strip()
                nele = int(cellNumber)
                print("Number of cells: {}".format(nele))
            # if END
        # for END
    # if END simple or csv



    #Read header file
    header = io.getFileContent(headerfilefull)
    header = header.replace("##Casename##",casename)
    header = header.replace("##node##",str(node))
    header = header.replace("##nele##",str(nele))
    header = header.replace("##timenodes##",str(TN))
    header = header.replace("##time_zone##",TIME_ZONE)
    header = header.replace("##VersionString##",VersionString)
    header = header.replace("##ThisFileString##",ThisFileString)



    data = "\tdata: \n"


    xnele = nele
    if (DEBUG):
        xnele = 20


    #===TIME================================================
    time = ""
    x = []
    for i in range (TN):
        x.append(TimeFloatStrMask.format(T[i])+", ")
    time = ("".join(x)).strip()
    time = u.replaceLastChar(time,";")
    time = "\t\ttime = \n\t\t"+time

    #===ITIME================================================
    Itime = ""
    x = []
    for i in range (TN):
        x.append("{:.0f}".format(T[i])+", ")
    Itime = ("".join(x)).strip()
    Itime = u.replaceLastChar(Itime,";")
    Itime = "\t\tItime = \n\t\t"+Itime

    #===ITIME2================================================
    Itime2 = ""
    x = []
    for i in range (TN):
        x.append("{:.0f}".format(T[i]*u.MILLISECONDSPERDAY)+", ")
    Itime2 = ("".join(x)).strip()
    Itime2 = u.replaceLastChar(Itime2,";")
    Itime2 = "\t\tItime2 = \n\t\t"+Itime2

    if (Mode == "simple" or Mode == "csv"):
        #===UWIND_SPEED====================================================
        uwind_speed = u.generateDataSeries("uwind_speed",WX,TN,xnele,WindFloatStrMask) # Mask should be "{:.4f}" or similar

        #===VWIND_SPEED====================================================
        vwind_speed = u.generateDataSeries("vwind_speed",WY,TN,xnele,WindFloatStrMask) # Mask should be "{:.4f}" or similar
    elif (Mode == "ecmwf"):
        uwind_speed = u.generateDataSeries2D("uwind_speed",WX,WindFloatStrMask) # Mask
        vwind_speed = u.generateDataSeries2D("vwind_speed",WY,WindFloatStrMask) # Mask




    data = data  +"\n"+time+"\n\n"+Itime+"\n\n"+Itime2+"\n\n"
    data = data  +uwind_speed+"\n\n"+vwind_speed+"\n\n"
    out = header.replace("##data##",data)

    print("Writing to file: {}...".format(windfilefull))
    io.writeFile(windfilefull,out)


    print("Generating NetCDF file: {} ...".format(ncwindfilefull))
    cmd = "ncgen -b {} -o {}".format(windfilefull,ncwindfilefull)

    os.system(cmd)


    print("\n=====Config (for Case / NML file)::=====")
    print(" TIMEZONE        = 'none',")
    print(" DATE_FORMAT     = 'YMD'")
    print(" START_DATE      = 'days={}' ! {}".format(T[0],T_comment))
    print(" END_DATE        = 'days={}' ! {}".format(T[TN-1],T_comment))
    print("=====")



    print("End of program [{}].".format(VersionString))










