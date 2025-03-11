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
Verbose = 1 # True / False
TEXTRA = 0.1
TimeFloatStrMask = "{:11.6f}"
WindFloatStrMask = "{:.5f}"
SciFloatStrMask  = "{:.8e}"
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
SaveImages      = 0 #
HeatingActive   = 0 # Generate Heating Forcing into the nc-file
PrintParams     = 0
MappingMethod   = "gauss"
WindDirMod360   = 1
TempSeaMin      = 5  # The minimum temperature of the sea water
TempSeaMax      = 12 # The maximum temperature of the sea water
TempSeaWetBulb  = 3  # The wet bulb temperature over sea areas. Do not change lightly
Exp1            = 0
Exp2            = 0
Exp3            = 0

#========WIND SETUP===================================================================
TimeUnit    = 'day' # Unit of T. Can be changed. Must be either 'hour' or 'day' or 'second'
# TN Number of programmed time steps. First and last should be determined by T0 and T9.
TN          = -1 # -1 Indicates non-assigned - AS IT SHOULD BE.
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

if ("debug" in params):            DEBUG            = bool(int(params["debug"]))
if ("basepath" in params):         basepath         = params["basepath"]
if ("gridfile" in params):         gridfile         = params["gridfile"]
if ("headerfile" in params):       headerfile       = params["headerfile"]
if ("windfile" in params):         windfile         = params["windfile"]
if ("ncwindfile" in params ):      ncwindfile       = params["ncwindfile"]
if ("TN" in params ):              TN               = float(params["TN"])
if ("T0" in params ):              T0               = float(params["T0"])
if ("T9" in params ):              T9               = float(params["T9"])
if ("timestepsperday" in params ): timestepsperday  = float(params["timestepsperday"])
if ("saveimages" in params ):      SaveImages       = int(params["saveimages"])
if ("heatingactive" in params ):   HeatingActive    = int(params["heatingactive"])
if ("printparams" in params ):     PrintParams      = int(params["printparams"])
if ("mappingmethod" in params ):   MappingMethod    = params["mappingmethod"]
if ("winddirmod360" in params ):   WindDirMod360    = int(params["winddirmod360"])
if ("verbose" in params ):         Verbose          = int(params["verbose"])
if ("exp1" in params ):            Exp1             = int(params["exp1"])
if ("exp2" in params ):            Exp2             = int(params["exp2"])
if ("exp3" in params ):            Exp3             = int(params["exp3"])


#==========================================
if (PrintParams==1):
    pp = "  {:20s}: {}"
    print("===================================================================")
    print("Parameters::")
    print(pp.format("basepath",basepath))
    print(pp.format("gridfile",gridfile))
    print(pp.format("headerfile",headerfile))
    print(pp.format("windfile",windfile))
    print(pp.format("ncwindfile",ncwindfile))
    print(pp.format("TN",TN))
    print(pp.format("T0",T0))
    print(pp.format("T9",T9))
    print(pp.format("timestepsperday",timestepsperday))
    print(pp.format("saveimages",SaveImages))
    print(pp.format("heatingactive",HeatingActive))
    print(pp.format("printparams",PrintParams))
    print(pp.format("mappingmethod",MappingMethod))
    print(pp.format("winddirmod360",WindDirMod360))
    print(pp.format("verbose",Verbose))
    print(pp.format("exp1",Exp1))
    print(pp.format("exp2",Exp2))
    print(pp.format("exp3",Exp3))
    print("===================================================================")

# if END




#--------AUTOMATED---------------------------------------------------------------
gridfilefull    = u.addFileToPath(basepath,gridfile)
headerfilefull  = headerfile # Should be in same path as this py file.
heatingfilefull = heatingfile # Should be in same path as this py file.
windfilefull    = u.addFileToPath(basepath,windfile) # Output file
ncwindfilefull  = u.addFileToPath(basepath,ncwindfile) # Output NC file


#========================================================================================
#========BEGIN OF ECMWF==================================================================
#========================================================================================
if (Mode == "ecmwf"):
    fromDateTime=u.MJD2datetime(T0)
    toDateTime=u.MJD2datetime(T9)
    gd = GRIBData()
    gd.loadData(fromDateTime, toDateTime, 58, 66, -18, 0.5)


    #Find first time step
    print("Finding first time step ...")
    i = 1
    w_istart = 0
    while (i < len(gd.mjd) ):
        if (gd.mjd[w_istart]>T0):
            print("ERROR: Start MJD in ECMWF larger than T0.[{} and {}]. EXITING.".format(gd.mjd[w_istart],T0))
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

    w_iend=gd.checkAppend(w_iend,T9,TEXTRA)
    # ONLY USE IN SPECIAL CASES
    #fieldList = ["ws","wd","mslp","t2","tp","tpx"]
    #w_iend=gd.checkAppendX(fieldList,w_iend,T9,TEXTRA)
    #
    # === Create new dataset with only selected data
    gdx=gd.exportForcingData(w_istart,w_iend) # gdx is the cut-out step interval
    gdx.printFieldSummary()



    #============================================================
    # Printing U10 , V10, WS, WD Matrices
    printU10V10Matrices = 0
    if (printU10V10Matrices==1):
        print("Print U10 V10 WS WD data ...")
        u.printMatrix2x2(["U10","V10","WS ","WD "],gd.u10,gd.u10,gd.ws,gd.wd)
        u.printMatrix2x2(["U10","V10","WS ","WD "],gdx.u10,gdx.u10,gdx.ws,gdx.wd)

    # Printing ECMWF DATA and positioning
    if (Verbose==1):
        print("Printing ECMWF DATA and positioning...")
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
        #for END
        #
        for i in range(inmax):
            xstr = "X (i,j)=({:2d},{:2d}-{:2d}): (  x,  y)=".format(i+i0,j0,jnmax+j0-1)
            for j in range(jnmax):
                xstr = xstr+"({:8.1f},{:8.1f}) ".format(gdx.x[i+i0,j+j0],   gdx.y[i+i0,j+j0])
            print(xstr)
        #for END_DAT
    # if END
    #
    # FAKE VALUE
    if (Exp1==1):
        i0 = 19 # lat
        j0 = 54 # lon
        for t in range(gdx.ws.shape[2]):

            gdx.t2[1+i0,1+j0,t]     =   50 + gdx.t2[1+i0,1+j0,t]
            gdx.cdrx[1+i0,1+j0,t]   =   gdx.cdrx[1+i0,1+j0,t]
            gdx.tpx[1+i0,1+j0,t]    =   0*10/3600 + gdx.tpx[1+i0,1+j0,t]

            #gdx.ws[1+i0,1+j0,t]=50
            #gdx.wd[1+i0,1+j0,t]=0
    # if END
    #

    # Print WS and WD
    if (Verbose==1):
        print("(WS,WD)-values for inspection")
        for i in range(inmax):
            wstr = "W (i,j)=({:2d},{:2d}-{:2d}): ( ws, wd)=".format(i+i0,j0,jnmax+j0-1)
            for j in range(jnmax):
                wstr = wstr+"({:8.1f},{:8.1f}) ".format(gdx.ws[i+i0,j+j0,0],   gdx.wd[i+i0,j+j0,0])
            print(wstr)
        # for i END
    # if END

    #
    #===Check wind directions=====================================================
    print("Checking wind direction values...")
    (gdx.wd, nchanges) = u.correctWindDirection3D(gdx.wd)
    print("Check done. {} changes made.".format(nchanges))
    gdx.printFieldSummary()


    #
    #===Print example of data
    if (Verbose==1):
        print("Printing example of data: [{}]".format("gdx"))
        gdx.printExample_ws_ws_u10_v10("gdx")
    #if END
    #
    #===Generate per hour steps=========================
    print("Generating time (default: per hour) steps (interpolation)...")
    #gdr = gdx.createRamps(["ws","wd","t2","cdrx","tpx"],timestepsperday) # gdr is the ramped dataset, created from gdx
    gdr = gdx.createRamps([],timestepsperday) # gdr is the ramped dataset, created from gdx
    gdr.printFieldSummary()



    #
    if (WindDirMod360==1):
        print("Modulus back to [0;360] degrees ...")
        #gdx.wd = np.mod(gdx.wd,360.0)
        gdr.calcWDmod360()
        print("Modulus back to [0;360] degrees ... Done.")
        gdr.printFieldSummary()
    # if END

    print("Calc WX & WY ...")
    gdr.calcWindXY()
    print("Calc WX & WY ... Done.")
    gdr.printFieldSummary()


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
    #======================================================================
    # Printing GRIB Matrix
    #gdx.printGRIBMatrix()

    #
    #======================================================================
    # FVCOM to GRIB MAP
    print("Creating element mapping from GRIB to FVCOM ...")
    fgemap = FvcomGribMap(fvcomgrd,gdr)
    fgemap.buildElementMap()
    fgemap.transmapWindPolar(MappingMethod)
    #
    #print("Calculating WX and WY ...")
    #windXY = fgemap.calcWindCartesian()
    #WX = windXY.X
    #WY = windXY.Y
    WX = fgemap.WX
    WY = fgemap.WY

    #
    #print("Print WS WD WX WY data ...")
    #u.printMatrix2x2(["WS","WD","WX","WY"],WS,WD,WX,WY)

    #
    if (SaveImages==1):
        print("Plotting forcing data ...")
        for i in range(len(T)):
            fgemap.p_vectorscale=fgemap.WINDVECTORSCALE
            fgemap.setVectorDelta(10000,10000)
            fgemap.setColormap("hsv")
            #fgemap.plotVector("wd","u10","v10",i)
            #fgemap.plotVector("wd","wx","wy",i)
            fgemap.plotVector("ws","wx","wy",i)
            fgemap.setColormap("jet")
            #fgemap.plot("u10",i)
            #fgemap.plot("v10",i)
            #fgemap.plot("ws",i)
            #fgemap.plot("wd",i)
            fgemap.plot("wx",i)
            fgemap.plot("wy",i)
        #fn = "wd-u10-v10"; cmd = "ffmpeg -y -framerate 3 -i {}/fvcomgribmap-{}-%05d.png -codec png  -vcodec libx264 -crf 22 {}/{}.mp4".format("img",fn,"img",fn); os.system(cmd)
        #fn = "wd-wx-wy";   cmd = "ffmpeg -y -framerate 3 -i {}/fvcomgribmap-{}-%05d.png -codec png  -vcodec libx264 -crf 22 {}/{}.mp4".format("img",fn,"img",fn); os.system(cmd)
        fn = "ws-wx-wy";   cmd = "ffmpeg -y -framerate 3 -i {}/fvcomgribmap-{}-%05d.png -codec png  -vcodec libx264 -crf 22 {}/{}.mp4".format("img",fn,"img",fn); os.system(cmd)
    # if SaveImages END

    # ========================================================================================
    # GENERATION OF NODE FORCING
    print("Creating node mapping from GRIB to FVCOM ...")
    fgnmap = FvcomGribMap(fvcomgrd,gdr) #
    fgnmap.buildNodeMap()
    gdr.printFieldSummary()

    if (HeatingActive == 1):
        # Node values
        fieldList = ['mslp', 't2','cdrx','tpx']
        MSLP, T2, CDRX, TPX = fgnmap.transmapNodeValues(fieldList,MappingMethod)
        #
        # Element-Node values
        fgemap.buildEleToNodeMap()
        WS_EN=fgemap.transmapEleToNodeValues(["ws"])


        #
        #print("Plotting forcing data ...")

        if (SaveImages==1):
            fgemap.setColormap("jet")
            for i in range(TN):
                fgnmap.plot("mslp",i)  # MeanSurfaceLayerPressure
            # for END
            fn = "mslp"; cmd = "ffmpeg -y -framerate 3 -i {}/fvcomgribmap-{}-%05d.png -codec png  -vcodec libx264 -crf 22 {}/{}.mp4".format("img",fn,"img",fn); os.system(cmd)
            #
            for i in range(TN):
                fgnmap.plot("t2",i)    # Temperature T2
            fn = "t2";   cmd = "ffmpeg -y -framerate 3 -i {}/fvcomgribmap-{}-%05d.png -codec png  -vcodec libx264 -crf 22 {}/{}.mp4".format("img",fn,"img",fn); os.system(cmd)
            #
            try:
                for i in range(TN):
                    fgnmap.plot("cdrx",i) # CumulativeDirectRadiationX
                fn = "cdrx"; cmd = "ffmpeg -y -framerate 3 -i {}/fvcomgribmap-{}-%05d.png -codec png  -vcodec libx264 -crf 22 {}/{}.mp4".format("img",fn,"img",fn); os.system(cmd)
            except Exception as e:
                # By this way we can know about the type of error occurring
                print("The error is: ",e)
            # try END
            #
            for i in range(TN):
                fgnmap.plot("tpx",i) # TotalPrecipitationX
            fn = "tpx";  cmd = "ffmpeg -y -framerate 3 -i {}/fvcomgribmap-{}-%05d.png -codec png  -vcodec libx264 -crf 22 {}/{}.mp4".format("img",fn,"img",fn); os.system(cmd)
            #
            # Element-Node Values
            for i in range(TN):
                fgemap.plot("ws_en",i) # WindSpeed@Node
            #for END
            fn = "ws_en";  cmd = "ffmpeg -y -framerate 3 -i {}/fvcomgribmap-{}-%05d.png -codec png  -vcodec libx264 -crf 22 {}/{}.mp4".format("img",fn,"img",fn); os.system(cmd)
            #
            htmlstr = "<html><body><ul><li><a href=\"wd-u10-v10.mp4\">wd-u10-v10</a></li><li><a href=\"wd-wx-wy.mp4\">wd-wx-wy</a></li><li><a href=\"mslp.mp4\">mslp</a></li><li><a href=\"t2.mp4\">t2</a></li><li><a href=\"cdrx.mp4\">cdrx</a></li><li><a href=\"tpx.mp4\">tpx</a></li></ul></body></html>"
            io.writeFile("img/index.php",htmlstr)
        # if SaveImages END





        # Air temperature, degC
        AT0 = 1e-27 #Air temperature
        AT = np.multiply(AT0,np.ones(shape=(fvcomgrd.nodecount,TN))) #Air temperature
        AT = T2
        # Short wave, W/m2
        SW0 = 2E-27 # Short wave
        SW = np.multiply(SW0,np.ones(shape=(fvcomgrd.nodecount,TN))) #Short wave
        SW = CDRX
        # Long wave radiation
        LW0 = 3E-27 # Long wave, W/m2
        LW = np.multiply(LW0,np.ones(shape=(fvcomgrd.nodecount,TN))) #Short wave
        # Air pressure, Pa
        AP0 = 1013.25*100 # Air pressure, Pa
        AP = np.multiply(AP0,np.ones(shape=(fvcomgrd.nodecount,TN))) #Short wave
        AP = MSLP
        # Net heat flux, W/m2
        NHF0 = 4E-27 # Net heat flux, positive: downward flux, heating, negative: upward flux, cooling
        NHF = np.multiply(NHF0,np.ones(shape=(fvcomgrd.nodecount,TN))) #Short wave
        # Precipitation, m/s (Precipitation, ocean lose water is negative), m/S
        PRE0 = 5E-27
        PRE = np.multiply(PRE0,np.ones(shape=(fvcomgrd.nodecount,TN))) #Precipitation
        PRE = TPX
        # Evaporation, m/s (Evaporation, ocean lose water is negative), m/s
        EVA0 = 6E-27
        EVA = np.multiply(EVA0,np.ones(shape=(fvcomgrd.nodecount,TN))) #Precipitation
        TSEA0 = 10.1
        TSEA = np.multiply( TSEA0, np.ones((fvcomgrd.nodecount,TN),float))


        EVA = u.calcEvapSimple(WS_EN,u.calcTempSea(T,TempSeaMin,TempSeaMax),T2,0.8)


    # if END



#========================================================================================
#========END OF ECMWF====================================================================
#========================================================================================


if (Mode == "simple" or Mode == "csv"):
    print("WARNING: SIMPLE and CSV removed in this version. Go back to \"buildwind.py\".")
# if simple or csv END
elif (Mode == "ecmwf"):
    node = int(fvcomgrd.nodecount)
    nele = fvcomgrd.cellcount
    T_comment = "Number of days since 1858-11-17 00:00:00. T_ORIGIN = T_MJD"

run = 1
if (run==1):
    print(VersionString)

    #Read header file
    header = io.getFileContent(headerfilefull)
    header = header.replace("##Casename##",casename)
    header = header.replace("##node##",str(node))
    header = header.replace("##nele##",str(nele))
    header = header.replace("##timenodes##",str(TN))
    header = header.replace("##time_zone##",TIME_ZONE)
    header = header.replace("##VersionString##",VersionString)
    header = header.replace("##ThisFileString##",ThisFileString)
    if (HeatingActive==1):
        header = header.replace("##HeatingFields##",io.getFileContent(heatingfilefull))
    else:
        header = header.replace("##HeatingFields##","")
    # if END



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

    uwind_speed = u.generateDataSeries2D("uwind_speed",WX,WindFloatStrMask) # Mask
    vwind_speed = u.generateDataSeries2D("vwind_speed",WY,WindFloatStrMask) # Mask
    #
    if (HeatingActive==1):
        air_temperature = u.generateDataSeries2D("air_temperature",AT,WindFloatStrMask) # Mask
        short_wave = u.generateDataSeries2D("short_wave",SW,SciFloatStrMask) # Mask
        long_wave = u.generateDataSeries2D("long_wave",LW,SciFloatStrMask) # Mask
        air_pressure = u.generateDataSeries2D("air_pressure",AP,SciFloatStrMask) # Mask
        net_heat_flux = u.generateDataSeries2D("net_heat_flux",NHF,SciFloatStrMask) # Mask
        precip = u.generateDataSeries2D("precip",PRE,SciFloatStrMask) # Mask
        evap = u.generateDataSeries2D("evap",EVA,SciFloatStrMask) # Mask

    if (DEBUG):
        i=uwind_speed.find("\n",100)
        uwind_speed = uwind_speed[0:i-1]+";"
        i=vwind_speed.find("\n",100)
        vwind_speed = vwind_speed[0:i-1]+";"
        #
        if (HeatingActive==1):
            i=air_temperature.find("\n",100)
            air_temperature = air_temperature[0:i-1]+";"
            i=short_wave.find("\n",100)
            short_wave = short_wave[0:i-1]+";"
            i=long_wave.find("\n",100)
            long_wave = long_wave[0:i-1]+";"
            i=long_wave.find("\n",100)
            long_wave = long_wave[0:i-1]+";"
            i=air_pressure.find("\n",100)
            air_pressure = air_pressure[0:i-1]+";"
            i=net_heat_flux.find("\n",100)
            net_heat_flux = net_heat_flux[0:i-1]+";"
            i=precip.find("\n",100)
            precip = precip[0:i-1]+";"
            i=evap.find("\n",100)
            evap = evap[0:i-1]+";"

        # if END
    # if END
    #
    # Accummulate data
    data = data  +"\n"+time+"\n\n"+Itime+"\n\n"+Itime2+"\n\n"
    data = data  +uwind_speed+"\n\n" +vwind_speed +"\n\n"
    if (HeatingActive==1):
        data = data + air_temperature + "\n\n"
        data = data + short_wave + "\n\n"
        data = data + long_wave + "\n\n"
        data = data + air_pressure + "\n\n"
        data = data + net_heat_flux + "\n\n"
        data = data + precip + "\n\n"
        data = data + evap + "\n\n"
    # if END
    #
    # Write data into the header template
    out = header.replace("##data##",data)
    #
    # Write to CDL file...
    print("Writing to file: {} ...".format(windfilefull))
    io.writeFile(windfilefull,out)
    print("Writing to file: {} ... DONE.".format(windfilefull))
    #
    # Generate the NC file...
    print("Generating NetCDF file: {} ...".format(ncwindfilefull))
    cmd = "ncgen -b {} -o {}".format(windfilefull,ncwindfilefull)
    ret_os = os.system(cmd)
    print("Generating NetCDF file:  {} ... DONE (Return value: {}).".format(ncwindfilefull,ret_os))
    #
    # Write a config header for the *_run_nml file (mostly obsolete)
    #
    print("\n=====Config (for Case / NML file)::=====")
    print(" TIMEZONE        = 'none',")
    print(" DATE_FORMAT     = 'YMD'")
    print(" START_DATE      = 'days={}' ! {}".format(T[0],T_comment))
    print(" END_DATE        = 'days={}' ! {}".format(T[TN-1],T_comment))
    print("=====")
    #
    print("End of program [{}].".format(VersionString))










