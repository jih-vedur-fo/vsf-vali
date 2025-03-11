#downloadecmwf data
import os
from pathlib import Path
import logging
import ftplib
from datetime import date, datetime, timedelta
import datetime as dt
from time import time, sleep
import numpy as np
import pygrib as pgr
import fvcomlibutil as u
import shutil
import glob
import sys

VERBOSE = False
GRIBBASEDIR = "/opt/fvcom/cron/forcing/ecmwf/"
GRIBCURRENTBUFFER = "0/"
GRIBTEMPBUFFER = "1/"
GRIBARCHIVE = "archive/"
MJD0 = 2400000.5 # Zero of MJD compared to JulianDay



#=============================================================================================================
# Copy and RENAME files from CURRENTBUFFER to ARCHIVE
#
def copyToArchive():
    print("Copying data files to archive ...")
    baseDir = GRIBBASEDIR
    gribDir = baseDir + GRIBCURRENTBUFFER
    archiveDir = baseDir + GRIBARCHIVE
    model_run_time = datetime(date.today().year,date.today().month,date.today().day,0,0)

    flist = os.listdir(gribDir)
    flen=len(flist)
    if (flen>0):
        flist=sorted(flist)

        runtime=flist[0][3:11]
        #print(runtime)
        runtime_year   = dt.datetime.now().year
        runtime_month  = int(runtime[0:2])
        runtime_day    = int(runtime[2:4])
        runtime_hour   = int(runtime[4:6])
        runtime_minute = int(runtime[6:8])
        runtime_second = int("00")
        datayear=runtime_year

        #print("{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(runtime_year,runtime_month,runtime_day,runtime_hour,runtime_minute,runtime_second))

        for i in range(flen):
        #for i in range(1):
            #print(flist[i])
            timestepnp=gribstring2NPDateTime64(flist[i][11:20],runtime_month)
            #print(timestepnp)
            timestep=gribstring2DateTimeFilename(flist[i][11:20],runtime_month)
            #timestep=timestep.replace("00-01-00","00-00-00") # Special case
            #print(timestep)
            src = gribDir+flist[i]
            dfn = "{}.grib".format(timestep)
            dst = archiveDir+dfn
            print("Copying {} to {} in archive...".format(flist[i],dfn))
            shutil.copy(src,dst)
        # for END
    else:
        print("No files to copy to archive...")
    # if-else END
#def END
#
#=============================================================================================================
# Download latest files from ECMWF to CURRENTBUFFER
#
def download_ecmwf_data():
    base_dir = GRIBBASEDIR
    treepath = base_dir + GRIBCURRENTBUFFER
    temppath = base_dir + GRIBTEMPBUFFER
    print("Creating folders [{}] ...".format(temppath))
    os.makedirs(temppath, exist_ok=True)
    print("Creating folders [{}] ...".format(treepath))
    os.makedirs(treepath, exist_ok=True)

    # Clear that folder off old temp data first.
    [f.unlink() for f in Path(temppath).glob("*") if f.is_file()]

    # FTP-Server information

    # HOSTNAME = "212.55.53.90"
    HOSTNAME = "ftp.vedur.fo"
    USERNAME = "dmi-ecmwf"
    PASSWORD = "hdl3YLDD6bajQayY"
    #ftp_server = ftplib.FTP(HOSTNAME, USERNAME, PASSWORD)
    print("Connecting to FTP server [{}] ...".format(HOSTNAME))
    ftp_server = None
    if ftp_server is None:
        logging.info('Connecting...')
        # print("Connecting...")
        ftp_server = ftplib.FTP(HOSTNAME, USERNAME, PASSWORD)

    # Defining model run time from today at midnight (i.e. taking ECMWF data from the 00:00 model run, first available around 06:40 UTC in the morning)
    model_run_time = datetime(date.today().year,date.today().month,date.today().day,0,0)

    # Taking 3-hourly data time steps representing the time range of present day (day 1) at 15:00 until midnight (00:00) between day 4 and 5.
        #for x in range(1,29):
    hourdelta = 0
    ndays=6
    nfilesperday = 8
    nfiles= ndays * nfilesperday + 1
    waitmax = 5
    for x in range(0,nfiles):
    #for x in range(1,0):
        print("Downloading {} of {}...  ".format(x+1,nfiles))
        nwait = 0
        # print(f'\nDownloading {x} of 28...')
        model_timestep_date = model_run_time + timedelta(hours=x*3+hourdelta)
        name = 'A1S'+str(model_run_time.month).zfill(2)+str(model_run_time.day).zfill(2)+str(model_run_time.hour).zfill(2)+'00'+str(model_timestep_date.month).zfill(2)+str(model_timestep_date.day).zfill(2)+str(model_timestep_date.hour).zfill(2)+'001'
        name2 =  "A1S{:02d}{:02d}{:02d}00{:02d}{:02d}{:02d}011".format(
            model_run_time.month, model_run_time.day, model_run_time.hour,
            model_timestep_date.month, model_timestep_date.day,  model_timestep_date.hour)

        k=0
        while k==0:
            if ftp_server is None:
                ftp_server = ftplib.FTP(HOSTNAME, USERNAME, PASSWORD)
            # if END
            print("Attempting file:  {} ...".format(name))
            if name in ftp_server.nlst():
                k=1 # continue with next file
                with open(name, "wb") as file:
                    print("Downloading file: {} ...".format(name))
                    ftp_server.retrbinary(f"RETR {name}", file.write)
                    os.rename(name, temppath+name)
                sleep(1)
            elif name2 in ftp_server.nlst():
                k=1 # continue with next file
                with open(name2, "wb") as file:
                    print("Downl. alt. file: {} ...".format(name2))
                    ftp_server.retrbinary(f"RETR {name2}", file.write)
                    os.rename(name2, temppath+name2)
                sleep(1)
            elif (nwait < waitmax ):
                now = datetime.now()
                current_time = now.strftime("%H:%M:%S")
                print('Waiting..' + current_time)
                nwait = nwait + 1
                sleep(60)
            else:
                k=1 # continue with next file
        # while END
    # for END
    #
    #Copy new files to current buffer
    print("Moving temp files to current buffer...")
    # Clear that folder off old data first.
    [f.unlink() for f in Path(treepath).glob("*") if f.is_file()]
    for fn in glob.glob(temppath+"*"):
        if not os.path.isdir(fn):
            shutil.move(fn,treepath)
    #shutil.copy(temppath+"*",treepath)
    [f.unlink() for f in Path(temppath).glob("*") if f.is_file()]

    print("Download done.")
# def END
#
#=============================================================================================================
# Convert a GRIB datetimestring to python datetime format
#
def gribstring2DateTime(str,runtime_month):
    #print(str)
    str_year=dt.datetime.now().year
    str_month=int(str[0:2])
    str_day = int(str[2:4])
    if (runtime_month==12 and str_month==1):
        str_year = str_year +1
    str_hour = int(str[4:6])
    str_minute = int(str[6:8])
    str_second = int("00")
    #print("{:02d}:{:02d}:{:02d}".format(str_hour,str_minute,str_second))
    #dtx = dt.datetime.combine(date(str_year, str_month,str_day),dt.time(str_hour,str_minute,str_second))
    dtx = dt.datetime(str_year, str_month,str_day,str_hour,str_minute,str_second)
    return dtx
# def END
#

#=============================================================================================================
# Convert a GRIB datetimestring to a datetime string
#
def gribstring2DateTimeFilename(str,runtime_month):
    #print(str)
    str_year=int(dt.datetime.now().year)

    str_month=int(str[0:2])
    str_day = int(str[2:4])
    if (runtime_month==12 and str_month==1):
        str_year = str_year +1
    str_hour = int(str[4:6])
    str_minute = int(str[6:8])
    str_second = int("00")
    dtstr = "{:4d}-{:02d}-{:02d}T{:02d}-{:02d}-{:02d}".format(str_year,str_month,str_day,str_hour,str_minute,str_second)
    return dtstr
# def END
#
#=============================================================================================================
# Convert a GRIB datetimestring to NumPy DateTime64 format
#
def gribstring2NPDateTime64(str,runtime_month):
    #print(str)
    str_year=dt.datetime.now().year
    str_month=int(str[0:2])
    str_day = int(str[2:4])
    if (runtime_month==12 and str_month==1):
        str_year = str_year +1

    str_hour = int(str[4:6])
    str_minute = int(str[6:8])
    str_second = int("00")
    dtx = np.datetime64("{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}".format(str_year,str_month,str_day,str_hour,str_minute,str_second))
    return dtx
# def END
#
#=============================================================================================================
# Get a message (with index index) from a GRIB (grbs) dataset
#
def getMessage(grbs, index):
    return grbs.message(index)
# def END
#


def printMessages(grbs):
    n = 0
    for grb in grbs:
        print("{} {}".format(n,grb))
        n = n + 1

def printKeys(grb):
    for xx in grb.keys():
        try:
            print("grb[{}]: {}".format(xx,grb[xx]))
        except Exception as e:
            print("Error reading key: {}: {}".format(xx,e))

def selectMessage(grbs, messagename, targetvalue,lat1=0, lat2=90, lon1=-90, lon2=90):
    filterPropertyName="latitudeOfLastGridPointInDegrees"
    index = -1
    values = []
    grbx = []
    index = 0
    valueFound = False
    while (not valueFound):
        grbx = grbs.select(name=messagename)[index]
        #print(grbx.keys())
        if grbx[filterPropertyName] == targetvalue:
            valueFound = True
            #values = grbx.values # This WORKS and returns the whole grid.
            values, lat, lon = grbx.data(lat1, lat2, lon1, lon2)
            #lat, lon = grbs.select(name='Mean sea level pressure')[index].latlons()
            #lat, lon = grbx.latlons()
            if (VERBOSE):
                print("Lat/Lon: {} {} {}   {} {} {}".format(lat.shape, lat.min(), lat.max(), lon.shape, lon.min(), lon.max()))
                print("Value ({}) found (index={})".format(messagename,index))
        else:
            #print("Value NOT found (index={})".format(index))
            index = index + 1
    return values, lat, lon, grbx, index



#================================================================================================
# Returns the GRIB data for the intervals
# Time     : [fromDateTime; toDateTime]
# Latitude : [lat1; lat2]
# Longitude: [lon1, lon2]
# Returns  : timesteps, lat, lon, x, y, mslp, u10, v10, t2, c1, c2, c3
def get_ecmwf_FVCOMdata(fromDateTime, toDateTime, lat1, lat2, lon1, lon2):
    # Settings
    targetFilterValue = 57.5
    targetFilterValue = 30.0

    # Initialize parameters
    fromDateTime = fromDateTime - dt.timedelta(seconds=5)
    toDateTime   = toDateTime   + dt.timedelta(seconds=5)
    epsilon = 1e-6
    lat1 = lat1 - epsilon # Lower the limit by just a bit, to be sure to be under...
    lat2 = lat2 + epsilon # Raise the limit by just a bit, to be sure to be over...
    lon1 = lon1 - epsilon # Lower the limit by just a bit, to be sure to be under...
    lon2 = lon2 + epsilon # Raise the limit by just a bit, to be sure to be over...

    # Initialize dirs
    baseDir = GRIBBASEDIR
    gribDir = baseDir + GRIBCURRENTBUFFER
    archiveDir = baseDir + GRIBARCHIVE
    #model_run_time = datetime(date.today().year,date.today().month,date.today().day,0,0)

    #===============================================================================
    # Find files
    dirlist = os.listdir(archiveDir)
    dirlist=sorted(dirlist)
    flist=[]
    dflist=[]
    for fl in dirlist:
        dtstr = fl[0:19]
        #print("[{}]".format(dtstr))

        dfl = datetime.strptime(dtstr, '%Y-%m-%dT%H-%M-%S')
        #print("{} > {} : {}".format(dfl,fromDateTime,dfl>fromDateTime))
        #print("{} < {} : {}".format(dfl,toDateTime,dfl<toDateTime))
        if ( (dfl>=fromDateTime) and (dfl<toDateTime) ):
            print("{} OK".format(fl))
            flist.append(fl)
            dflist.append(dtstr)
        else:
            if (VERBOSE): print("{} NOT OK".format(fl))
    flist=sorted(flist)
    flen=len(flist)
    if (flen == 0):
        print("ERROR: No files in folder list. Check criterions!")
        sys.exit()
    #flen = 6
    #sys.exit()

    #====================================================================================
    # Read data dimensions
    grbs = pgr.open(archiveDir+flist[0])
    (data, lat, lon, grb, index) = selectMessage(grbs,"Mean sea level pressure",targetFilterValue, lat1, lat2, lon1, lon2)
    xlen=data.shape[0]
    ylen=data.shape[1]

    #===================================================
    # Initialize timesteps array
    dt0=dt.datetime(1900,1,1,00,00,00) # Just a dummy value to initialize the array with

    print("Calculate the number of timesteps to generate ...")
    nTimeSteps = 0
    for i in range(flen):
        if (flist[i].find("T00-01-00.grib")>-1):
            nTimeSteps = max(nTimeSteps-1,0)
        # if END
        nTimeSteps = nTimeSteps + 1
    # for END
    print("Number of calculated time steps: {}".format(nTimeSteps))


    timesteps=np.array(nTimeSteps*[dt0],datetime)
    #targetFilterValue = 57.5
    #targetFilterValue = 30.0
    #if (targetFilterValue == 57.5):
        #xlen=101
        #ylen=211
    #else:
        #xlen=221
        #ylen=501
    julianDay     = np.zeros([nTimeSteps])
    startStep     = np.zeros([nTimeSteps])
    endStep       = np.zeros([nTimeSteps])
    refMJD        = np.zeros([nTimeSteps]) # Calculated field
    mjd           = np.zeros([nTimeSteps])
    hour          = np.zeros([nTimeSteps])
    xxtimefactor  = np.zeros([nTimeSteps]) # timefactor for missing DELTA fields
    lon           = np.zeros([xlen,ylen])
    lat           = np.zeros([xlen,ylen])
    x             = np.zeros([xlen,ylen])
    y             = np.zeros([xlen,ylen])
    mslp          = np.zeros([xlen,ylen,nTimeSteps])
    u10           = np.zeros([xlen,ylen,nTimeSteps])
    v10           = np.zeros([xlen,ylen,nTimeSteps])
    dpt2          = np.zeros([xlen,ylen,nTimeSteps])
    t2            = np.zeros([xlen,ylen,nTimeSteps])
    cdr           = np.zeros([xlen,ylen,nTimeSteps]) # Clear-sky direct solar radiation at surface, J m**-2
    cdrx          = np.zeros([xlen,ylen,nTimeSteps]) # DELTA Clear-sky direct solar radiation at surface, J m**-2/3h
    cbh           = np.zeros([xlen,ylen,nTimeSteps]) # Cloud base height
    cp            = np.zeros([xlen,ylen,nTimeSteps]) # Convective precipitation, m
    lsp           = np.zeros([xlen,ylen,nTimeSteps]) # Large-scale precipitation, m
    lspx          = np.zeros([xlen,ylen,nTimeSteps]) # DELTA Large-scale precipitation, m/3h
    sp            = np.zeros([xlen,ylen,nTimeSteps])  # Surface pressure, Pa
    tcc           = np.zeros([xlen,ylen,nTimeSteps]) # Total cloud cover, 0-1
    vis           = np.zeros([xlen,ylen,nTimeSteps]) # Visibility, m
    tp            = np.zeros([xlen,ylen,nTimeSteps]) # Total Precipitation, m
    tpx           = np.zeros([xlen,ylen,nTimeSteps]) # DELTA Total Precipitation Delta, m/3h
    c1            = np.zeros([xlen,ylen,nTimeSteps])
    c2            = np.zeros([xlen,ylen,nTimeSteps])
    c3            = np.zeros([xlen,ylen,nTimeSteps])
    # Used??::
    #uquiver = np.zeros([xlen,ylen,nTimeSteps])
    #vquiver = np.zeros([xlen,ylen,nTimeSteps])
    #windspeed = np.zeros([xlen,ylen,nTimeSteps])
    #direction = np.zeros([xlen,ylen,nTimeSteps])
    #
    # Temp variables for CDR/CDRX, LSP/LSPX, TP/TPX
    cdr2 = None
    cdr1 = None
    lsp2 = None
    lsp1 = None
    tp1 = None
    tp2 = None


    gridConstructed = False

    n = 0 # Counter
    for i in range(flen):
    #for i in range(1):
        print("Reading file ({} of {}): {} ...".format(i+1,flen,flist[i]))
        isModelData = True
        if (flist[i].find("T00-01-00.grib")>-1):
            nm1 = max (n - 1, 0)
            print("WARNING: Overwriting simulation data, with new inital data (measurements) (n:{}->{}).".format(n,nm1))
            n = nm1
            isModelData = False
             # Roll back and overwrite previous entry.
        # if END
        fn=archiveDir+flist[i]
        grbs = pgr.open(fn)


        if VERBOSE: print("Length of grbs: {}".format(len(grbs)))
        grb=grbs.message(1)

        # FOR DEBUG/DEVELOPMENT PURPOSES::
        #printKeys(grb)
        #printMessages(grbs)

        # DO NOT DELETE - YET....
        julianDay[n] = grb['julianDay']
        startStep[n] = grb['startStep']
        endStep[n]   = grb['endStep']
        refMJD[n] = julianDay[n] - MJD0
        mjd[n] = refMJD[n] + startStep[n]/24
        hour[n] = grb['startStep']
        xxtimefactor[n] = 3.0/max(3.0,hour[n]) # Factor used to calculate data, when delta value is missing/impossible to calculate.
        if VERBOSE:
            print("JulianDay {}    MJD: {}".format(julianDay[n],mjd[n]))
        #for grb in grbs:
        #    print(grb)

        #(xtime, latx, lonx, grb, index) = selectMessage(grbs,"time",targetFilterValue, lat1, lat2, lon1, lon2)
        #print("xtime {}".format(xtime))
        #sys.exit()


        # MSLP
        (mslp[:,:,n], latx, lonx, grb, index) = selectMessage(grbs,"Mean sea level pressure",targetFilterValue, lat1, lat2, lon1, lon2)
        lat[:,:]=latx
        lon[:,:]=lonx
        if VERBOSE:
            print("LAT shape: {}".format(lat.shape))
        # if END
        #
        #
        # U10
        (u10[:,:,n], latx, lonx, grb, index) = selectMessage(grbs,"10 metre U wind component",targetFilterValue, lat1, lat2, lon1, lon2)
        #
        # V10
        (v10[:,:,n], grb, latx, lonx, index) = selectMessage(grbs,"10 metre V wind component",targetFilterValue, lat1, lat2, lon1, lon2)
        #
        # DPT2
        (dpt2[:,:,n], grb, latx, lonx, index) = selectMessage(grbs,"2 metre dewpoint temperature",targetFilterValue, lat1, lat2, lon1, lon2)
        #
        # T2
        (t2[:,:,n], grb, latx, lonx, index) = selectMessage(grbs,"2 metre temperature",targetFilterValue, lat1, lat2, lon1, lon2)
        #
        # CDR / CDRX
        # Reading: Clear-sky direct solar radiation at surface, J m**-2
        if ( not cdr2 is None):
            cdr1 = cdr2
        # if END
        (cdr2, grb, latx, lonx, index) = selectMessage(grbs,"Surface direct short-wave radiation, clear sky",targetFilterValue, lat1, lat2, lon1, lon2)
        #
        if (isModelData):
            if ( not cdr1 is None):
                cdrx[:,:,n]=np.subtract(cdr2,cdr1)
            else:
                print("WARNING: {:4.1f}% of Clear-sky direct solar radiation at surface used for delta radiation. (hour = {})".format(xxtimefactor[n]*100, hour[n]))
                cdrx[:,:,n]=np.multiply(cdr2,xxtimefactor[n])
            # if END
            cdr[:,:,n] = cdr2 # Same :-)
        else:
            print("WARNING: CDRX = CDR2 - CDRN")
            cdrx[:,:,n] = np.subtract(cdr2 , cdr[:,:,n])
            print("WARNING: CDR overwritten with measurement data.")
            cdr[:,:,n] = cdr2 # Same :-)
        # if END
        # Ensure only positive precipitation
        cdrx[:,:,n] = np.maximum(cdrx[:,:,n], 0)
        #
        #
        #
        # CBH
        (cbh[:,:,n], grb, latx, lonx, index) = selectMessage(grbs,"Cloud base height",targetFilterValue, lat1, lat2, lon1, lon2)
        #
        # CP
        (cp[:,:,n], grb, latx, lonx, index) = selectMessage(grbs,"Convective precipitation",targetFilterValue, lat1, lat2, lon1, lon2)
        #
        #
        # LSP / LSPX
        # Reading: Clear-sky direct solar radiation at surface, J m**-2
        if ( not lsp2 is None):
            lsp1 = lsp2
        # if END
        (lsp2, grb, latx, lonx, index) = selectMessage(grbs,"Large-scale precipitation",targetFilterValue, lat1, lat2, lon1, lon2)
        #
        if (isModelData):
            if ( not lsp1 is None):
                lspx[:,:,n]=np.subtract(lsp2,lsp1)
            else:
                print("WARNING: {:4.1f}% of Large-scale precipitation used for delta precipitation. (hour = {})".format(xxtimefactor[n]*100, hour[n]))
                lspx[:,:,n]=np.multiply(lsp2,xxtimefactor[n])
            # if END
            lsp[:,:,n] = lsp2 # Same :-)
        else:
            print("WARNING: LSPX = LSP2 - LSPN")
            lspx[:,:,n] = np.subtract(lsp2 , lsp[:,:,n])
            print("WARNING: LSP overwritten with measurement data.")
            lsp[:,:,n] = lsp2 # Same :-)
        # if END
        # Ensure only positive precipitation
        lspx[:,:,n] = np.maximum(lspx[:,:,n], 0)
        #
        #
        # SP
        (sp[:,:,n], grb, latx, lonx, index) = selectMessage(grbs,"Surface pressure",targetFilterValue, lat1, lat2, lon1, lon2)
        #
        # TCC
        (tcc[:,:,n], grb, latx, lonx, index) = selectMessage(grbs,"Total cloud cover",targetFilterValue, lat1, lat2, lon1, lon2)
        #
        # VIS
        (vis[:,:,n], grb, latx, lonx, index) = selectMessage(grbs,"Visibility",targetFilterValue, lat1, lat2, lon1, lon2)
        #
        #
        #
        # TP / TPX
        # Reading Total precipitation
        if ( not tp2 is None):
            tp1 = tp2
        # if END
        (tp2, grb, latx, lonx, index) = selectMessage(grbs,"Total precipitation",targetFilterValue, lat1, lat2, lon1, lon2)
        #
        if (isModelData):
            if ( not tp1 is None):
                tpx[:,:,n]=np.subtract(tp2,tp1)
            else:
                print("WARNING: {:4.1f}% of total preciptitation used for delta precipitation. (hour = {})".format(xxtimefactor[n]*100, hour[n]))
                tpx[:,:,n]=np.multiply(tp2,xxtimefactor[n])
            # if END
            tp[:,:,n] = tp2 # Same :-)
        else:
            print("WARNING: TPX = TP2 - TPN")
            tpx[:,:,n] = np.subtract(tp2 , tp[:,:,n])
            print("WARNING: TP overwritten with measurement data.")
            tp[:,:,n] = tp2 # Same :-)
            #print("WARNING: TP NOT overwritten with measurement data.")
        # if END
        # Ensure only positive precipitation
        tpx[:,:,n] = np.maximum(tpx[:,:,n], 0)
        #
        #
        # C1
        (c1[:,:,n], grb, latx, lonx, index) = selectMessage(grbs,"Low cloud cover",targetFilterValue, lat1, lat2, lon1, lon2)
        # C2
        (c2[:,:,n], grb, latx, lonx, index) = selectMessage(grbs,"Medium cloud cover",targetFilterValue, lat1, lat2, lon1, lon2)
        # C3
        (c3[:,:,n], grb, latx, lonx, index) = selectMessage(grbs,"High cloud cover",targetFilterValue, lat1, lat2, lon1, lon2)

        #timesteps[n]=datetime.strptime(dflist[i],'%Y-%m-%dT%H-%M-%S')
        timesteps[n]=u.MJD2datetime(mjd[n])
        #timesteps[i]=string2DateTime(flist[i][11:20],runtime_month)
        print("  File timestamp: {}".format(timesteps[n].strftime("%Y-%m-%d %H:%M:%S")))




        if (not gridConstructed):
            gridConstructed = True
            for j in range(xlen):
                for k in range(ylen):
                    rx, ry=u.latlon2Pos(lat[j][k],lon[j][k],0,0,62.0,-7.0)
                    x[j][k]=rx
                    y[j][k]=ry
                # for k END
            #for j END
        #if END
        n = n + 1
    # for END
    ncount = n
    #
    #sys.exit()
    #Check dimensions of data:
    print("Dimensions of {:10s} are {}.".format("timestemps",timesteps.shape))
    print("Dimensions of {:10s} are {}.".format("lat",lat.shape))
    print("Dimensions of {:10s} are {}.".format("lon",lon.shape))
    print("Dimensions of {:10s} are {}.".format("x",x.shape))
    print("Dimensions of {:10s} are {}.".format("y",y.shape))
    print("Dimensions of {:10s} are {}.".format("mslp",mslp.shape))
    print("Dimensions of {:10s} are {}.".format("u10",u10.shape))
    print("Dimensions of {:10s} are {}.".format("v10",v10.shape))
    print("Dimensions of {:10s} are {}.".format("dpt2",dpt2.shape))
    print("Dimensions of {:10s} are {}.".format("t2",t2.shape))
    print("Dimensions of {:10s} are {}.".format("cdr",cdr.shape))
    print("Dimensions of {:10s} are {}.".format("cdrx",cdrx.shape))
    print("Dimensions of {:10s} are {}.".format("cbh",cbh.shape))
    print("Dimensions of {:10s} are {}.".format("cp",cp.shape))
    print("Dimensions of {:10s} are {}.".format("lsp",lsp.shape))
    print("Dimensions of {:10s} are {}.".format("lspx",lspx.shape))
    print("Dimensions of {:10s} are {}.".format("sp",sp.shape))
    print("Dimensions of {:10s} are {}.".format("tcc",tcc.shape))
    print("Dimensions of {:10s} are {}.".format("vis",vis.shape))
    print("Dimensions of {:10s} are {}.".format("tp",tp.shape))
    print("Dimensions of {:10s} are {}.".format("tpx",tpx.shape))
    print("Dimensions of {:10s} are {}.".format("c1",c1.shape))
    print("Dimensions of {:10s} are {}.".format("c2",c2.shape))
    print("Dimensions of {:10s} are {}.".format("c3",c3.shape))

    if (timesteps.shape[0]!=mslp.shape[2]):
        print("ERROR: {} and {} dimensions differ ({} and {}).".format("timesteps","mslp",timesteps.shape[0],mslp.shape[2]))
        sys.exit()
    if (lat.shape!=lon.shape):
        print("ERROR: {} and {} dimensions differ ({} and {}).".format("lat","lon",lat.shape,lon.shape))
        sys.exit()
    if (lon.shape!=x.shape):
        print("ERROR: {} and {} dimensions differ ({} and {}).".format("lon","x",lon.shape,x.shape))
        sys.exit()
    if (x.shape!=y.shape):
        print("ERROR: {} and {} dimensions differ ({} and {}).".format("x","y",x.shape,y.shape))
        sys.exit()
    if (y.shape[0]!=mslp.shape[0] or y.shape[1]!=mslp.shape[1]):
        print("ERROR: {} and {} dimensions differ ({} and {}) (excluding timesteps dimension (2)).".format("y","mslp",y.shape,mslp.shape))
        sys.exit()
    if (mslp.shape!=u10.shape):
        print("ERROR: {} and {} dimensions differ ({} and {}).".format("mslp","u10",mslp.shape,u10.shape))
        sys.exit()
    if (u10.shape!=v10.shape):
        print("ERROR: {} and {} dimensions differ ({} and {}).".format("u10","v10",u10.shape,v10.shape))
        sys.exit()
    if (v10.shape!=t2.shape):
        print("ERROR: {} and {} dimensions differ ({} and {}).".format("v10","t2",v10.shape,t2.shape))
        sys.exit()
    if (t2.shape!=tp.shape):
        print("ERROR: {} and {} dimensions differ ({} and {}).".format("t2","tp",t2.shape,tp.shape))
        sys.exit()
    if (tp.shape!=tpx.shape):
        print("ERROR: {} and {} dimensions differ ({} and {}).".format("tp","tpx",tp.shape,tpx.shape))
        sys.exit()
    if (tpx.shape!=c1.shape):
        print("ERROR: {} and {} dimensions differ ({} and {}).".format("tpx","c1",tpx.shape,c1.shape))
        sys.exit()
    if (c1.shape!=c2.shape):
        print("ERROR: {} and {} dimensions differ ({} and {}).".format("c1","c2",c1.shape,c2.shape))
        sys.exit()
    if (c2.shape!=c3.shape):
        print("ERROR: {} and {} dimensions differ ({} and {}).".format("c2","c3",c2.shape,c3.shape))
        sys.exit()
    if (c3.shape!=tp.shape):
        print("ERROR: {} and {} dimensions differ ({} and {}).".format("c2","c3",c2.shape,c3.shape))
        sys.exit()




    return (timesteps,
         lat,
         lon,
         x,
         y,
         mslp, # Mean sea level pressure, Pa
         u10,  # 10 metre U wind component, m/s
         v10,  # 10 metre V wind component, m/s
         dpt2,  # 2 metre dewpoint temperature, °C/C (GRIB: K)
         t2,   # 2 metre temperature, °C/C (GRIB: K)
         cdr,  # Clear-sky direct solar radiation at surface, J m**-2
         cdrx, # DELTA Clear-sky direct solar radiation at surface, J m**-2 / 3h
         cbh,  # Cloud base height
         cp,   # Convective precipitation, m
         lsp,  # Large-scale precipitation, m
         lspx, # DELTA Large-scale precipitation, m/3h
         sp,   # Surface pressure, Pa
         tcc,  # Total cloud cover, 0-1
         vis,  # Visibility, m
         tp,   # Total precipitation, m H2O
         tpx,  # DELTA Total Precipitation, m/3h H20
         c1,   # Low cloud cover, 0-1
         c2,   # Medium cloud cover, 0-1
         c3    # High cloud cover, 0-1
         )
# def END
#========================================================================================
