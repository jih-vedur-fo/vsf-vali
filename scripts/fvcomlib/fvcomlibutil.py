# fvcomlibutil.py
# Wind generator for FVCOM 4.3, 5.0
# COSUrFI 2023
# Jari í Hjøllum, Knud Simonsen
# Version 1.9 31-10-2024
#

import datetime as dt
from shlex import shlex
from numpy import random
import math
import numpy as np
import os

#===CONSTANTS==========================================================
DEBUG=False
VERBOSE=False
DEG2RAD = math.pi/180.0
RAD2DEG = 180.0/math.pi
DAYSPERSECOND = 1.0/86400.0 #  seconds/day. Constant - DO NOT CHANGE
DAYSPERHOUR = 1.0/24.0 # days/hour. Constant - DO NOT CHANGE
MILLISECONDSPERDAY = 86400*1000 # days/hour. Constant - DO NOT CHANGE
MJDYEAR = 365.2421897 # on 01-01-2000 according to https://en.wikipedia.org/wiki/Tropical_year
#==================
pico = 1e-12
nano = 1e-9
micro = 1e-6
milli = 1e-3
unit = 1
kilo = 1e3
mega  = 1e6
giga = 1e9
tera = 1e12
secondsperhour = 3600

#========================================================================
def addTrailingSlash(path):
    return os.path.join(path, '')

#========================================================================
def addFileToPath(path,filename):
    return os.path.join(path, filename)

#========================================================================
# Input: 
#   tpd : Dewpoint temperature (in Celsius)
#   t   : Temperature  (in Celsius)
#
def dewpointToRH(tdp,t):
    # From https://iridl.ldeo.columbia.edu/dochelp/QA/Basic/dewpoint.html
    # Relative humidity gives the ratio of how much moisture the air is holding to how much moisture it could hold at a given temperature.
    # This can be expressed in terms of vapor pressure and saturation vapor pressure:
    # RH = 100% x (E/Es)
    # where, according to an approximation of the Clausius-Clapeyron equation:
    # E = E0 x exp[(L/Rv) x {(1/T0) - (1/Td)}] and
    # Es = E0 x exp[(L/Rv) x {(1/T0) - (1/T)}]
    # where E0 = 0.611 kPa, (L/Rv) = 5423 K (in Kelvin, over a flat surface of water), T0 = 273 K (Kelvin)
    # and T is temperature (in Kelvin), and Td is dew point temperature (also in Kelvin).
    # So, if you know the temperature, you can solve for Es, and substitute the equation for E into the expression for relative humidity and solve for Td (dew point).
    # If you are interested in a simpler calculation that gives an approximation of dew point temperature if you know the observed temperature and relative humidity, the following formula was proposed in a 2005 article by Mark G. Lawrence in the Bulletin of the American Meteorological Society:
    # Td = T - ((100 - RH)/5.)
    # where Td is dew point temperature (in degrees Celsius), T is observed temperature (in degrees Celsius), and RH is relative humidity (in percent). Apparently this relationship is fairly accurate for relative humidity values above 50%.
    # More details can be found in the article:
    # Lawrence, Mark G., 2005: The relationship between relative humidity and the dewpoint temperature in moist air: A simple conversion and applications. Bull. Amer. Meteor. Soc., 86, 225-233. doi: http;//dx.doi.org/10.1175/BAMS-86-2-225  
    rh = 5*(tdp-t)+100
    return rh

#========================================================================
def ensure_numpy_array(value):
    arr = np.asarray(value)
    return arr if arr.ndim > 0 else np.array([arr])  # Ensure 1D array

#========================================================================
# Calc saturation partial pressure of water at temp t
# input : t in degC
# output pressure in Pa
# Based on interpolation-polynomium between -25 and +40 degC
# -25  63,25
# -20  103,2
# -15  165,2
# -10  259,2
# -5   401,5
# 0 610,8
# 5  871,9
# 10  1227
# 15  1704
# 20  2337
# 25  3167
# 30  4243
# 35  5623
# Formula f(x) = 0,0393512340600576 x2 + 1,64471673914321 x2 + 39,5281581653641 x + 577,564717635306
def calcSatPartialWaterPressure(t):
    coeff = np.array([3, 2, 1, 0])

    factors = [0.0393512340600576, 1.64471673914321, 39.5281581653641, 577.564717635306]

    #print("Size of array: {}".format(np.size(t)))
    #print("Shape of array: {}".format(t.shape))
    ilen = np.size(t)
    #print(ilen)


    x = np.zeros((ilen),float)
    #x[0]=-1


    for i in range(ilen):
        ts = np.multiply(t[i], np.ones((4),float))
        x[i] = np.sum(np.multiply(factors,np.power(ts,coeff)))
    # for i END


    return x

#========================================================================
# Calculates the evaporation from the sea surface
# From eq (5) https://ethz.ch/content/dam/ethz/special-interest/usys/iac/iac-dam/documents/edu/courses/atmospheric_physics_lab_work/evaporation.pdf

# T0 is the Sea temperature in C
# T is the Air temperature in C
# p is the pressure in Pa (conversion to hPa is done inside)
# TwDelta is the number of degrees (in C), that Tw (Wet bulb temperature) is below the air temperature. Should be positive.
def calcEvapSimple(u,Twater,Tair,RH=0.80):
    Twater = ensure_numpy_array(Twater)
    Tair = ensure_numpy_array(Tair)
    RH = ensure_numpy_array(RH)

    a = 30.6 # m/s
    b = 32.1 # no unit
    deltaHw = 2410 # kJ/kg

    mA = np.zeros(Tair.shape,float)
    #print("u shape: {}".format(u.shape))
    #print("Twater shape: {}".format(Twater.shape))
    #print("Tair shape: {}".format(Tair.shape))

    pwPa = calcSatPartialWaterPressure(Twater)
    #print("pw({}):\n{}".format(Twater,pwPa))
    pwHg = (1/133.322) * pwPa # mmHg
    tlen = np.size(Twater)
    for t in range(tlen):
        paPa = calcSatPartialWaterPressure(Tair[:,t])*RH
        #print("pa({}):\n{}".format(Tair[:,t],paPa))
        paHg = (1/133.322) * paPa # mmHg
        mA[:,t] = (a+b*u[:,t])*(pwHg[t]-paHg)/deltaHw # kg/(m2 hour)
        mA[:,t] = np.multiply(mA[:,t],1 /(1000 * 3600)) #  1kg/m2 = 1mmH2O => 1/1000 mH2O; 1/hour = 1/(3600s)
    # for END

    return mA


def DONOTUSEcalcEvapSimple2(windvelocity,T0,T,RH):
    def calcES(temp):
        return np.multiply(6.112,np.exp(np.divide(np.multiply(17.67,temp),np.add(temp,243.5))))
    # def-sub END
    p = 101325 # Pa
    TwDelta = 3 # degC
    T0 = 10.1 # degC
    rho = 1.293 # kg/m3
    CD  = 1e-3
    A   = 6.6e-4 # K-1
    Tw = np.subtract(T,TwDelta) # Wet bulb temperature, 3 deg below T
    T0w = np.subtract(T0,TwDelta) # Wet bulb temperature, 3 deg below T
    phPa = np.multiply(1e-2,p) # convert from Pa to hPa, for which the formula is valid

    # t0 is water temperature


    es = calcES(T)
    #e = np.subtract(es,np.multiply(A,np.multiply(phPa,np.subtract(T,Tw))))
    e = es *RH
    q = np.multiply(0.622,np.divide(e,phPa))

    es0 = calcES(T0)
    e0 = np.subtract(es0,np.multiply(A,np.multiply(phPa,np.subtract(T0,T0w))))
    q0 = np.multiply(0.622,np.divide(e0,phPa)) # p in hPa



    Egcm2y1 = np.multiply(rho*CD, np.multiply(windvelocity,np.subtract(q0,q))) # In units of g cm-2 y-1
    x = 1.e-6 * 1e4 * 1.0/(31556736) #g cm-2 y-1 til m/s ## 1e-6m3 * 1e4m-2 * 1/31556736 s-1
    E = np.multiply(x, Egcm2y1) # in m/s


    return E
# def END
#
#========================================================================
def calcTempSea(MJD, TMin, TMax):
    T0   = (TMax+TMin)/2.0
    TAmp = (TMax-TMin)/2.0
    MJD0 = 60676 # 01-01-2025
    MJDTMin = 60735 # 01-03-2025
    k  = 2*math.pi/MJDYEAR
    k0 = 2*math.pi/MJDTMin
    # T = TAmp * sin( k * (MJD - MJDTMin) )
    T = TAmp*np.sin(  k * (MJD - MJDTMin)) + T0
    #print("Sea temperature:\n{}".format(T))
    return T

#========================================================================
# Calculate wind speed and direction
# Returns:
# Absolute wind speed
# Angle (360 deg) relative to NORTH and CW
#
#Inspired from https://stackoverflow.com/questions/20924085/python-conversion-between-coordinates
#
def calcWindSpeedDirection(u, v):
    ws = np.sqrt(np.add(np.square(u),np.square(v)))
    wd = np.multiply(RAD2DEG,np.arctan2(v,u)) # Angle in East CCW
    wd = np.subtract(90,wd) # Transform from EastCCW to NorthCW
    wd = np.mod(np.add(180,wd),360) # Transform from TO-direction to FROM-direction
    return ws, wd

#========================================================================
# Calculates the X and Y values and transforms the NorthCW to EastCCW.
def calcWindXY(ws,wd):
    wd = np.subtract(wd,180) # Transform from FROM-direction to TO-direction
    wd = np.subtract(90,wd) # Transforms the NorthCW to EastCCW.
    wd = np.multiply(DEG2RAD,wd) # Transforms to Radians
    wx = np.multiply(ws,np.cos(wd))
    wy = np.multiply(ws,np.sin(wd))
    return wx, wy
# def END
#
#========================================================================
# Check and correct Wind Direction values.
# This is used in interpolation, to prevent jumping values where
# smooth transitions should be.
# Convert date to MJD (float)
def correctWindDirection(d_winddir,w_istart,w_iend):
    nchanges = 0
    for i in range(w_istart,w_iend-1):
        while (d_winddir[i+1]-d_winddir[i] > 180): # THEN CounterClockwise
            x1=d_winddir[i+1]
            x2=d_winddir[i+1]-360
            d_winddir[i+1]=x2
            nchanges = nchanges + 1
            if VERBOSE: print("Changed rotation direction of point {} to CCW ({} to {}) (prev. {}).".format(i+1,x1,x2,d_winddir[i]))
        # while END
        while (d_winddir[i+1]-d_winddir[i] < -180): # THEN CounterClockwise
            x1=d_winddir[i+1]
            x2=d_winddir[i+1]+360
            d_winddir[i+1]=x2
            nchanges = nchanges + 1
            if VERBOSE: print("Changed rotation direction of point {} to CW ({} to {}) (prev. {}).".format(i+1,x1,x2,d_winddir[i]))
        # while END
    #A for END
    return d_winddir, nchanges
# def END

#========================================================================
# Check and correct Wind Direction values.
# This is used in interpolation, to prevent jumping values where
# smooth transitions should be.
# Convert date to MJD (float)
def correctWindDirection3D(wd):
    nchanges = 0
    jcnt=wd.shape[0]
    kcnt=wd.shape[1]
    icnt=wd.shape[2]
    print("jCNT: {}  kCNT: {}   iCNT: {}".format(jcnt,kcnt,icnt))
    for j in range(jcnt): # X - direction
        for k in range(kcnt): # y - direction
            for i in range(icnt-1): # Time steps
                while (wd[j,k,i+1]-wd[j,k,i] > 180): # THEN CounterClockwise
                    x1=wd[j,k,i+1]
                    x2=wd[j,k,i+1]-360
                    wd[j,k,i+1]=x2
                    nchanges = nchanges + 1
                    if VERBOSE: print("Changed rotation (x,y,t)=({},{},{}) to CCW ({:6.1f} to {:6.1f}) (prev.pt. {:6.1f}).".format(j,k,i+1,x1,x2,wd[j,k,i]))
                # while END
                while (wd[j,k,i+1]-wd[j,k,i] < -180): # THEN CounterClockwise
                    x1=wd[j,k,i+1]
                    x2=wd[j,k,i+1]+360
                    wd[j,k,i+1]=x2
                    nchanges = nchanges + 1
                    if VERBOSE: print("Changed rotation (x,y,t)=({},{},{}) to CW ({:6.1f} to {:6.1f}) (prev.pt. {:6.1f}).".format(j,k,i+1,x1,x2,wd[j,k,i]))
                # while END
            # for i END
        #for k END
    #for j END
    return wd, nchanges
# def END



def date2MJD(d):
    dateform = "%Y-%m-%d"
    d = dt.strptime(d,dateform)
    d0 = dt.strptime('1858-11-17',dateform)
    delta = d - d0
    #print("Delta d : {}".format(delta.days))
    return delta.days

# Convert datestring to MJD (float)
def datestr2MJD(dstr):
    dateform = "%Y-%m-%d"
    d  = dt.strptime(dstr,dateform)
    d0 = dt.strptime('1858-11-17',dateform)
    delta = d - d0
    #print("Delta d : {}".format(delta.days))
    return delta.days

# Convert datetime to MJD (float)
def datetime2MJD(d):
    datetimeform = "%Y-%m-%d %H:%M:%S"
    #d = dt.datetime.
    #d=dt.strptime(d,datetimeform)
    d0 =dt.datetime.strptime('1858-11-17 00:00:00',datetimeform)
    delta = d - d0
    res = delta.days + delta.seconds/86400
    #print("Delta d : {}".format(res))
    return res

# Convert datetimestring to MJD (float)
def datetimestr2MJD(dtstr):
    datetimeform = "%Y-%m-%d %H:%M:%S"
    d  = dt.strptime(dtstr,datetimeform)
    d0 = dt.strptime('1858-11-17 00:00:00',datetimeform)
    delta = d - d0
    res = delta.days + delta.seconds/86400
    print("Delta d : {}".format(res))
    return res

def gaussian2D(x0, y0, stdev, n):
    r = random.normal(0,stdev,n)
    angle = np.multiply(2*math.pi ,random.rand(n))
    rx = np.add(np.multiply(r,np.cos(angle)) , int(x0))
    ry = np.add(np.multiply(r,np.sin(angle)) , int(y0))
    ##rz = np.d2(n)
    return rx, ry

def gaussian2DX(x0, y0, stdev, n, X = 4.0):

    r = random.normal(0,stdev,n)
    #rx=np.array(15,n)
    r = np.minimum(np.abs(r),X*stdev)
    angle = np.multiply(2*math.pi ,random.rand(n))
    rx = np.add(np.multiply(r,np.cos(angle)) , int(x0))
    ry = np.add(np.multiply(r,np.sin(angle)) , int(y0))
    #rz = np.zeros(n)
    return rx, ry



# Space-invariant FVCOM input generator
# dx : Array with data values 
# dxn : Number of elements in array 
# dxn2 : If the data should be repeated in a second dimension this is the setting to do it on.
#        A common case is the number of grid cells (nele).
#        But may also often be 1.
# strmask : string mask for cdl generation
def generateDataSeries(fieldname, dx, dxn, dxn2, strmask):
    ds =  ""
    x = []
    xn = 0
    yn = 0
    cnt = 0
    for i in range (dxn):
        for j in range(dxn2):
            x.append(strmask.format(dx[i])+", ")
            xn = xn + 1
            cnt += 1
        if (cnt % 10 ==0):
            x.append("\n\t\t\t")
        yn = yn + 1
    ds = ("".join(x)).strip()
    ds = replaceLastChar(ds,";")
    if (len(fieldname)>0):
        ds = "\t\t{} = \n\t\t\t".format(fieldname)+ds
    else:
        ds = " \n\t\t\t".format(fieldname)+ds
    print("Generated {}: {} elements.".format(fieldname,xn));
    return ds
# def END
#
#======================================================================================
# Generate 2D data (spatial 2D resolution is collapsed into 1D in FVCOM) input data series
# Parameters:
# fieldname (string)   : Name of field, e.g. "uwind_speed"
# data (2D numpy array) : Input data series.
#                           Dimensions:
#                               1, spatial index
#                               2 time index
# strmask (string)     : String mask for format. For float to string conversion.
#                        E.g.: "{:.4f}"
# Returns:
#       dso (string)   : String containing the data.
#
def generateDataSeries2D(fieldname, data, strmask):
    dso =  ""
    dsl = [] # Data String List
    xn = 0 # Number of elements added.
    yn = 0 # Number of lines added.
    cnt = 0
    ilen = data.shape[0]
    tlen = data.shape[1]
    for t in range (tlen):
        for i in range(ilen):
            dsl.append(strmask.format(data[i,t])+", ")
            xn = xn + 1
            cnt += 1
            if (cnt % 10 == 0):
                dsl.append("\n\t\t\t")
                yn = yn + 1
            # if END
        # for i END
    # for t END
    #
    dso = ("".join(dsl)).strip()
    dso = replaceLastChar(dso,";")
    if (len(fieldname)>0):
        dso = "\t\t{} = \n\t\t\t".format(fieldname)+dso
    else:
        dso = " \n\t\t\t".format(fieldname)+dso
    print("Generated {}: {} elements.".format(fieldname,xn));
    return dso
#
#======================================================================================
# Generate 3D data input data series
# Parameters:
# fieldname (string)   : Name of field, e.g. "uwind_speed"
# dsi (3D numpy array) : Input data series.
#                           Dimensions:
#                               1 & 2, spatial indicies.
#                               3 time index
# strmask (string)     : String mask for format. For float to string conversion.
#                        E.g.: "{:.4f}"
# Returns:
#       dso (string)   : String containing the data.
#
def OLDgenerateDataSeries3D(fieldname, dsi, strmask):
    dso =  ""
    dsl = [] # Data String List
    xn = 0 # Number of elements added.
    yn = 0 # Number of lines added.
    cnt = 0
    ilen = dsi.shape[0]
    jlen = dsi.shape[1]
    tlen = dsi.shape[2]
    for t in range (tlen):
        for i in range(ilen):
            for j in range(jlen):
                dsl.append(strmask.format(dsi[i,j,t])+", ")
                xn = xn + 1
                cnt += 1
                if (cnt % 10 == 0):
                    dsl.append("\n\t\t\t")
                # if END
            # for j END
            yn = yn + 1
        # for i END
    # for t END
    #
    dso = ("".join(dsl)).strip()
    dso = replaceLastChar(dso,";")
    if (len(fieldname)>0):
        dso = "\t\t{} = \n\t\t\t".format(fieldname)+dso
    else:
        dso = " \n\t\t\t".format(fieldname)+dso
    print("Generated {}: {} elements.".format(fieldname,xn));
    return dso


def generateNowTime():
    inow = dt.datetime.now() # current date and time
    date_time = inow.strftime("%d-%m-%Y, %H:%M:%S")
    ds = "{} | {} ms since 1, 1970, 00:00:00 (UTC)".format(date_time,inow.timestamp()*1000)
    print(ds)
    return ds

def d1norm(npx, npy,x0,y0):
    d1 = np.sqrt( np.add( np.square(np.subtract(npx,x0)) , np.square(np.subtract(npy,y0)) ) )

    return d1

# Calulates and returns the squared norm2 (Pythagoras) of an NumPy array (npx, npy) to a point (x0,y0)
def d2norm(npx, npy,x0,y0):
    d2 = np.add( np.square(np.subtract(npx,x0)) , np.square(np.subtract(npy,y0)) )
    return d2

# Calulates and returns the squared norm2 (Pythagoras) of an NumPy array (npx, npy) to a point (x0,y0)
def xd2norm(npx,x0):
    d2 = np.square(np.subtract(npx,x0))
    return d2

def printArray(a,strmask):
    s = []
    for i in range(len(a)):
        s.append(strmask.format(a[i]))
    return ", ".join(s)



def MJD2datetime(mjd):
    datetimeform = "%Y-%m-%dT%H:%M:%SUTC"
    d0 = dt.datetime.strptime('1858-11-17T00:00:00UTC',datetimeform)
    hrs = int(mjd*24.0)
    secs = int(mjd*86400.0)

    d = d0 + dt.timedelta(seconds=secs)
    return d


def latlon2Pos(lat, lon, y_origo, x_origo, lat_origo, lon_origo):
    r_equator=6378137 #https://gscommunitycodes.usf.edu/geoscicommunitycodes/public/geophysics/Gravity/earth_shape.php
    f=1.0 / 298.257223563
    r_lat=r_equator * (1.0 - f * (math.sin(math.pi*lat_origo/180.0))**2 ) # The radius of earth at the specific latitude.
    #print("r_lat      = {}".format(r_lat))
    r_poleaxis = r_lat*math.cos(math.pi*lat_origo/180.0)
    #print("r_poleaxis = {}".format(r_poleaxis))
    y=2*math.pi*r_lat*(lat-lat_origo)/360.0
    x=2*math.pi*r_poleaxis*(lon-lon_origo)/360.0
    return x, y

#===============================================================================================
# FROM: https://stackoverflow.com/questions/37765197/darken-or-lighten-a-color-in-matplotlib
#
#

def lighten_color(color, amount=0.5):
    """
    Lightens the given color by multiplying (1-luminosity) by the given amount.
    Input can be matplotlib color string, hex string, or RGB tuple.

    Examples:
    >> lighten_color('g', 0.3)
    >> lighten_color('#F034A3', 0.6)
    >> lighten_color((.3,.55,.1), 0.5)
    """
    import matplotlib.colors as mc
    import colorsys
    try:
        c = mc.cnames[color]
    except:
        c = color
    c = colorsys.rgb_to_hls(*mc.to_rgb(c))
    return colorsys.hls_to_rgb(c[0], 1 - amount * (1 - c[1]), c[2])
#===============================================================================================
#===============================================================================================
def listMultiply(factor, lst):
    for i in range(len(lst)):
        lst[i] = factor * lst[i]
    return lst
# def END
#===============================================================================================
#===============================================================================================

# Backwards compatibility
def lonlat2Pos(lon, lat, x_origo, y_origo, lon_origo, lat_origo):
    return latlon2Pos(lat, lon, y_origo, x_origo, lat_origo, lon_origo)



#From https://stackoverflow.com/questions/38737250/extracting-key-value-pairs-from-string-with-quotes
def parse_kv_pairs(text, item_sep=",", value_sep="="):
    """Parse key-value pairs from a shell-like text."""
    # initialize a lexer, in POSIX mode (to properly handle escaping)
    lexer = shlex(text, posix=True)
    # set ',' as whitespace for the lexer
    # (the lexer will use this character to separate words)
    lexer.whitespace = item_sep
    # include '=' as a word character
    # (this is done so that the lexer returns a list of key-value pairs)
    # (if your option key or value contains any unquoted special character, you will need to add it here)
    lexer.wordchars += value_sep
    lexer.wordchars += '.'
    lexer.wordchars += '/'
    lexer.wordchars += '-'
    lexer.wordchars += '_'
    lexer.wordchars += '*'
    lexer.wordchars += '?'
    # then we separate option keys and values to build the resulting dictionary
    # (maxsplit is required to make sure that '=' in value will not be a problem)
    return dict(word.split(value_sep, maxsplit=1) for word in lexer)

# steps = points - 1
def ramp(begin,end,points):
    res = []
    steps =points - 1
    delta = (end-begin)/(steps)
    for i in range(0,steps+1):
        res.append(begin+delta*i)
    return np.float64(res)

# steps = points - 1
def ramp1D(begin,end,points):
    D = 1
    DAX = D - 1
    res = np.zeros((points),float)
    steps =points - 1
    delta = np.divide(np.subtract(end,begin),steps)
    if DEBUG: print("begin {}".format(begin))
    if DEBUG: print("end {}".format(end))
    if DEBUG: print("delta {}".format(delta))
    for i in range(0,steps+1):
        newval =np.add(begin,np.multiply(delta,i))
        if DEBUG: print("1D NEWVAL      : {}".format(newval))
        res[i]=newval
        if DEBUG: print("1D RES         : {:8.4f}".format(res[i]))
    return res

# steps = points - 1
def ramp3D(begin,end,points):
    D = 3
    DAX = D - 1
    res = np.zeros((begin.shape[0],begin.shape[1],points),float)
    #res = np.expand_dims(res, axis=DAX)
    steps =points - 1
    delta = np.divide(np.subtract(end,begin),steps)
    x = 10
    y  = 10
    if DEBUG: print("3D begin {}".format(begin[x,y]))
    if DEBUG: print("3D end   {}".format(end[x,y]))
    if DEBUG: print("3D delta {}".format(delta[x,y]))
    for i in range(0,steps+1):
        newval =np.add(begin,np.multiply(delta,i))
        res[:,:,i]=newval
        if DEBUG: print("3D NEWVAL[{:2d},{:2d}]{:2s}    : {}".format(x,y," ",newval[x,y]))
        if DEBUG: print("3D Val   [{:2d},{:2d},{:2d}]   : {}".format(x,y,i,res[x,y,i]))
    return res

def ramps1DJoin(lst):
    for i in range(len(lst)-1):
        lst[i]=lst[i][:-1]
    res=np.concatenate(lst)
    return res


def ramps3DJoin(lst):
    for i in range(len(lst)-1): # For each element except the last one, remove (next line), copy and assign everything except the last time step in each ramp. Thereby we avoid 2 point in the time series with the same time-coordinate and values.
        lst[i]=lst[i][:,:,:-1]
    res=np.concatenate(lst,axis=2)
    return res


# steps = points - 1
def ramps(vals,nsteps):
    res = []
    n = len(vals)-1
    steps = -1
    delta = -1
    for i in range(n):
        steps=nsteps[i]
        dy=vals[i+1]-vals[i]
        dx=steps
        dydx = dy/dx
        #print("dy: {}  dx: {}.   dy/dx: {}".format(dy,dx,dydx))
        for j in range(steps):
            ddx = j
            #print(vals[i]+dydx*ddx)
            res.append(vals[i]+dydx*ddx)
        # for j
    # for i
    res.append(vals[n])
    return res



def replaceLastChar(s,replacement):
    size = len(s)
    s = s[:-1]+replacement
    return s



def printMatrix2x2(L,a,b,c,d):
    xlen=a.shape[0]
    ylen=a.shape[1]
    yrange1 = [0, 1 ]
    yrange2 = [ylen-2, ylen-1]
    xrange1 = [0,4]
    xrange2 = [xlen-4,xlen]
    print("{} {} {} {}{:8d}{:12s}{:6d}{:10s}{:12d}{:6s}{:12d}"
          .format(L[0],L[1],L[2],L[3],yrange1[0]," ",yrange1[1]," ",yrange2[0]," ",yrange2[1]))
    for i in range(xrange1[0],xrange1[1]):
        str1="{} {}   {:3d} ".format(L[0],L[1],i+1)
        str2="{} {}   {:3d} ".format(L[2],L[3],i+1)
        for j in yrange1:
            str1=str1+"({:6.1f}; {:6.1f})  ".format(a[i,j,0],b[i,j,0])
            str2=str2+"({:6.1f}; {:6.1f})  ".format(c[i,j,0],d[i,j,0])
        str1 = str1 + "... "
        str2 = str2 + "... "
        for j in yrange2:
            str1=str1+"({:6.1f}; {:6.1f})  ".format(a[i,j,0],b[i,j,0])
            str2=str2+"({:6.1f}; {:6.1f})  ".format(c[i,j,0],d[i,j,0])
        print(str1)
        print(str2)
    # for END
    print("   ...   ")
    for i in range(xrange2[0],xrange2[1]):
        str1="{} {}   {:3d} ".format(L[0],L[1],i+1)
        str2="{} {}   {:3d} ".format(L[2],L[3],i+1)
        for j in yrange1:
            str1=str1+"({:6.1f}; {:6.1f})  ".format(a[i,j,0],b[i,j,0])
            str2=str2+"({:6.1f}; {:6.1f})  ".format(c[i,j,0],d[i,j,0])
        str1 = str1 + "... "
        str2 = str2 + "... "
        for j in yrange2:
            str1=str1+"({:6.1f}; {:6.1f})  ".format(a[i,j,0],b[i,j,0])
            str2=str2+"({:6.1f}; {:6.1f})  ".format(c[i,j,0],d[i,j,0])
        print(str1)
        print(str2)
    # for END


#===============================================0000

def prog(i,N,fraction,strmask = "{:3.0f}%"):
    tick=int(round(N*fraction))
    if ( i % tick  == 0 ): print(strmask.format(round(100.0*i/N)))
#==================================================================================
def unitConvert(fromData, fromUnit, toUnit):
    ucFactor = unitConvertFactor(fromUnit,toUnit)

    if (ucFactor >= 0):
        return np.multiply(fromData,ucFactor), toUnit
    else:
        print("CONVERT DATA NOT OK. Error : {}.".format(-1*ucFactor))
        return fromData, fromUnit
    # if END


# def END


#==================================================================================
def unitConvertFactor(fromUnit, toUnit):
    error = 0
    ucFactor = 1.0
    if (fromUnit != toUnit):
        match fromUnit:
            case "m/s":
                match toUnit:
                    case "μm/h":
                        ucFactor = secondsperhour/(micro)
                    # case "mm/h" END
                    case "um/h":
                        ucFactor = secondsperhour/(micro)
                    # case "mm/h" END
                    case "mm/h":
                        ucFactor = secondsperhour/(milli)
                    # case "mm/h" END
                # match END
            case "mm/h":
                match toUnit:
                    case "m/s":
                        #print("mega: {}".format(mega))
                        ucFactor = milli/(secondsperhour)

                    # case "m/s" END
                # match END
            case _:
                print("ERROR: Unknown FROMUNIT ({})".fornmat(fromUnit))
                ucFactor = -1
            # case END
        # match END
    else:
        #print("WARNING: FROM unit ({}) and TO unit ({})are identical.".format(fromUnit,toUnit))
        return ucFactor, error
    # if END

    return ucFactor
# def END

