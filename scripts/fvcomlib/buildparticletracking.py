# buildparticletracking.py
# Particle tracking generator for FVCOM 
# Tested for version FVCOM 5.0.1 (intel)
# Build: ifvcom501.wd.river.lag (@fvcom-u18-skeid)
# Jari í Hjøllum, Knud Simonsen
# Version 1.5 12-11-2024
#
#========IMPORT===================================================================
import os
import sys
import array as arr # importing "array" for array creations
import fvcomlibio as io
import fvcomlibutil as u
#========CONSTANTS - DO NOT CHANGE================================================
DAYSPERSECOND = 1.0/86400.0 #  seconds/day. Constant - DO NOT CHANGE
DAYSPERHOUR = 1.0/24.0 # days/hour. Constant - DO NOT CHANGE
MSPERDAY = 86400*1000 # days/hour. Constant - DO NOT CHANGE
#========INIT===================================================================
MODE = "file" # can be "file" or "parameters"


#MODE = "parameter"
#--------CASE-------------------------------------------------------------------
casename            = "lag_init"
#--------FILES------------------------------------------------------------------
# These values are default values, and the values used in "file" mode. In "parameter" mode they may be overridden.
basepath        = "../input"
basepath        = "."
datafile        = "particle_NS.dat" #Particle init input file, for NetCDF generation
headerfile      = "buildparticletracking_base.cdl" #Input file, NetCDF header, for NetCDF header  -- DO NOT CHANGE LIGHTLY!!!
lagfilecdl      = "lag_init.cdl" #Output cdl file for NetCDF generation
lagfilenc       = "lag_init.nc" #Output NetCDF file
#========LAG SETUP===================================================================
TITLE              = "TestbedEstuary tse0001_run02, test with particles at 1 m depth." # Title string
                                        # for comment section in nc file-
PARTICLEPATHLENGTH = 0 # in meters
PARTICLEGROUP      = 1 # If "inc" the marker is made incremental, otherwise the value
PARTICLEMARK       = "inc" # If "inc" the marker is made incremental, otherwise the value
PARTICLEMARK       = 0 # If "inc" the marker is made incremental, otherwise the value
TBEG               = 60623 # Default value T0
TEND               = 60700 # Default value T9

#========CMDLINEPARAMS==========================================================
cmdparams = []
params = []
nargs = len(sys.argv)
print("Parameters ({}): ".format(nargs))
for i in range(nargs):
    print(sys.argv[i])

for i in range(nargs):
    cmdparams.append(sys.argv[i])

if len(cmdparams)>1:
    params=u.parse_kv_pairs(cmdparams[1])

if (len(params)>0):
    MODE = "parameter"

    for y in params:
        print (y,':',params[y])
    print("=======")


# === Setting default values ===
par_title=TITLE
par_tbeg=TBEG
par_tend=TEND
par_tdelta=3600 # in seconds
par_pathlength = 0
par_x0 = 12200.8
par_y0 = 128.184
par_z0 = 0.0
par_stdev = 5
par_lonlatactive=0
par_lon0=-6.372099487554092
par_lat0=62.10174136553437
par_group = PARTICLEGROUP
par_mark = PARTICLEMARK
par_nparticles=1000
par_ngroups = 25
par_npergroup = 40



if ("basepath" in params):       basepath         = params["basepath"]
if ("datafile" in params):       datafile         = params["datafile"]
if ("lagfilecdl" in params):     lagfilecdl       = params["lagfilecdl"]
if ("lagfilenc" in params):      lagfilenc        = params["lagfilenc"]
if ("title" in params ):         par_title        = params["title"]
if ("tbeg" in params ):          par_tbeg         = float(params["tbeg"])
if ("tend" in params ):          par_tend         = float(params["tend"])
if ("tdelta" in params ):        par_tdelta       = float(params["tdelta"])
if ("pathlength" in params ):    par_pathlength   = float(params["pathlength"])
if ("x0" in params ):            par_x0           = float(params["x0"])
if ("y0" in params ):            par_x0           = float(params["x0"])
if ("z0" in params ):            par_z0           = float(params["z0"])
if ("stdev" in params ):         par_stdev        = float(params["stdev"])
if ("lonlatactive" in params ):  par_lonlatactive = float(params["lonlatactive"])
if ("lon0" in params ):          par_lon0         = float(params["lon0"])
if ("lat0" in params ):          par_lat0         = float(params["lat0"])
if ("group" in params ):         par_group        = params["group"]
if ("mark" in params ):          par_mark         = params["mark"]
if ("nparticles" in params ):    par_nparticles   = int(params["nparticles"])
if ("ngroups" in params ):       par_ngroups      = int(params["ngroups"])
if ("npergroup" in params ):     par_npergroup    = int(params["npergroup"])



#========LAG SETUP - BE CAREFUL=================================================
TimeUnit    = 'day' # Unit of T. Can be changed. Must be either 'hour' or 'day' or 'second'
TN          = 2 # Number of programmed time steps. First and last should be determined by T0 and T9.
T0          = 0 # The starting time of the simulation to which this input should be used.
                # Take care to let his be in units of TimeUnit
T9          = 999999 # Ultimate end of the time scope of simulation
                # Take care to let his be in units of TimeUnit
T_ZERO      = "MJD" # Must be either 'MJD', 'MJD_2000' or 'MJD_2023'
TIME_ZONE   = 'none' # Use either 'none' or 'UTC' here.
T = arr.array('d',[T0, T9] ) # [T0, TRELSTEP1, TRELSTEP2, ... TRELSTEPN, T9]
                            #   or
                            # [0.0, T0, TRELSTEP1, TRELSTEP2, ... TRELSTEPN, T9]
                            # In units of chosen unit. NB.: First element must have value T0 or 0.0
                            # and last T9

#========Verbose/Debugging output====================================================
verbose = True

#--------VERSION----------------------------------------------------------------
Version         = "1.5 (12-11-2024)"
VersionString   = "BuildParticleTracking v. {} by Jari í Hjøllum, 2024".format(Version)
ThisFileString  = "This file was generated at {}".format(u.generateNowTime())


#========CHECKS===================================================================


#--------AUTOMATED - DO NOT CHANGE-------------------------------------------------
datafilefull    = basepath+"/"+datafile
headerfilefull  = headerfile
lagfilecdlfull  = basepath+"/"+lagfilecdl # Output file
lagfilencfull   = basepath+"/"+lagfilenc # Output NC file
#--------AUTOMATED -  DO NOT CHANGE---------------------------------------------------------------
T_MJD      = 0     # Number of days since 1858-11-17 00:00:00 to 01-01-2000 at 00:00:00 [http://www.csgnetwork.com/julianmodifdateconv.html & https://scienceworld.wolfram.com/astronomy/ModifiedJulianDate.html]
T_MJD_2000 = 51544 # Number of days since 1858-11-17 00:00:00 to 01-01-2000 at 00:00:00 [http://www.csgnetwork.com/julianmodifdateconv.html & https://scienceworld.wolfram.com/astronomy/ModifiedJulianDate.html]
T_MJD_2023 = 59945 # Number of days since 1858-11-17 00:00:00 to 01-01-2000 at 00:00:00 [http://www.csgnetwork.com/julianmodifdateconv.html & https://scienceworld.wolfram.com/astronomy/ModifiedJulianDate.html]
T_ORIGIN   = 0 # Default value - should not be used.
T_comment  = "T_ORIGIN = 0; The value should never be this."
if (T_ZERO=="MJD"):
    T_ORIGIN = T_MJD
    T_comment = "Number of days since 1858-11-17 00:00:00. T_ORIGIN = T_MJD_2000"
if (T_ZERO=="MJD_2000"):
    T_ORIGIN = T_MJD_2000
    T_comment = "Number of days since 1858-11-17 00:00:00. T_ORIGIN = T_MJD_2000"
if (T_ZERO=="MJD_2023"):
    T_ORIGIN = T_MJD_2023
    T_comment = "Number of days since 1858-11-17 00:00:00. T_ORIGIN = T_MJD_2023"
#========DEBUGGING / VERBOSE - YOU MAY CHANGE=================================
# Printing time steps one day apart: Seldom used.
printdaytimesteps = False # You may change this: True/False
if (printdaytimesteps) :
    x=[]
    for i in range(32):
        x.append("{}, ".format(i+T_ORIGIN))
    print("{} ".format("".join(x)))
#--------AUTOMATED -  DO NOT CHANGE---------------------------------------------------------------
TimeUnitVal = 1
if (TimeUnit=='day'): 
    TimeUnitVal = 1
if (TimeUnit=='hour'): 
    TimeUnitVal = daysperhour
if (TimeUnit=='second'): 
    TimeUnitVal = daysperseconds;
#
for i in range(TN):
    T[i] = T[i]*TimeUnitVal
#for i in range(1,TN):
    #T[i] = T[i] + T0 *TimeUnitVal
for i in range(TN):
    T[i] = T[i] + T_ORIGIN
T0R  = T0*TimeUnitVal+T_ORIGIN
T9R  = T9*TimeUnitVal+T_ORIGIN
TBEGR = TBEG*TimeUnitVal+T_ORIGIN
TENDR = TEND*TimeUnitVal+T_ORIGIN
#========DEBUGGING / VERBOSE - YOU MAY CHANGE=================================    
if (verbose):
    print("Start time: days = {}. End time: days = {}.".format(T[0],T[TN-1]))  
#=============================================================================    
#
#========PROGRAM===================================================================
run = 1 # if the program should be executed. Most of the time this should be "1".
if (run==1):
    print(VersionString)
    if ( MODE == "file"):
        print("Opening data file: \"{}\":".format(datafilefull))
        # Using readlines()
        file1 = open(datafilefull, 'r')
        lines = file1.readlines()
        N = len(lines)
        d = [""]*N
        print("Lines in file: {}".format(N))
        if (verbose):
            print("File content:\n=====FILE BEGIN=====")
            for line in lines:
                print("{}".format(line.strip()))
            print("=====FILE END=======")
        #
        # Rearranging the strings into an array of strings
        count = 0
        # Strips the newline character
        for line in lines:
            s = line.strip()
            if (len(s)>0):
                d[count]=s
                count += 1
        print("Number of lines arranged: {}".format(count))
        #
        # Load the data
        # Number of particles
        nparticles=int(d[0]) # First line contains the number of particles
        print("Number of particles: {}".format(nparticles))
        #Declare the arrays for the particle data
        pn = arr.array('i',[0]*nparticles )
        px = arr.array('d',[0]*nparticles )
        py = arr.array('d',[0]*nparticles )
        pz = arr.array('d',[0]*nparticles )
        ptbeg = arr.array('d',[TBEGR]*nparticles )
        ptend = arr.array('d',[TENDR]*nparticles )
        ppathlength = arr.array('d',[PARTICLEPATHLENGTH]*nparticles )
        pgroup = arr.array('i',[PARTICLEGROUP]*nparticles )
        pmark = arr.array('i',[0]*nparticles )
        if (PARTICLEGROUP=="inc"):
            for i in range(nparticles):
                pgroup[i]=i+1
        if (PARTICLEMARK=="inc"):
            for i in range(nparticles):
                pmark[i]=i+1
        #
        # Reading the particle data
        nparticlesread = 0 # reading the
        for i in range(1,nparticles+1):
            j=i-1 # The particle index is j.
            #print("Reading line: {}...".format(i))
            #print("L{}        : [{}].".format(i,d[i])  )
            s = d[i]
            a = s.split()
            pn[j]=int(a[0]) # particle no
            #print("AParticle {}".format(a[0]))
            px[j]=float(a[1]) # x
            py[j]=float(a[2]) # y
            pz[j]=float(a[3])  # z
            if (verbose): print("Particle {} at {}  {}  {}".format(pn[j],px[j],py[j],pz[j]))
            if (len(a)>4): ptbeg[j]=a[4] # tbeg if defined
            if (len(a)>5): ptend[j]=a[5] # tend if defined
            if (len(a)>6): ppathlength[j]=a[6] # group if defined
            if (len(a)>7): pgroup[j]=a[7] # group if defined
            if (len(a)>8): pmark[j]=a[8] # group if defined
            nparticlesread += 1
            if (nparticlesread==nparticles): break
    # if END
    elif ( MODE == "parameter" ):
        print("MODE: Parameter")
        tbeg=par_tbeg
        tend=par_tend
        tdelta = par_tdelta/86400.0
        x0=par_x0
        y0=par_y0
        stdev=par_stdev
        lonlatactive=par_lonlatactive
        if ( lonlatactive == 1):
            x_origo = 0
            y_origo = 0
            lon_origo = -7
            lat_origo = 62
            lon0=par_lon0
            lat0=par_lat0
            (x0,y0)=u.lonlat2Pos(lon0,lat0,x_origo,y_origo,lon_origo,lat_origo)
            print("x {}    y {}".format(x0,y0))
        pathlength=par_pathlength
        nparticles=par_nparticles
        ngroups=par_ngroups
        npergroup=par_npergroup
        group = 0 # should be 0
        mark = 0  # should be 0
        if isinstance(par_group,int): group = par_group
        if isinstance(par_group,int): mark = par_mark


        pn = arr.array('i',[0]*nparticles )
        px = arr.array('d',[0]*nparticles )
        py = arr.array('d',[0]*nparticles )
        pz = arr.array('d',[0]*nparticles )
        ptbeg = arr.array('d',[tbeg]*nparticles )
        ptend = arr.array('d',[tend]*nparticles )
        ppathlength = arr.array('d',[pathlength]*nparticles )
        pgroup = arr.array('i',[group]*nparticles )
        pmark = arr.array('i',[mark]*nparticles )

        (px, py) = u.gaussian2D(x0,y0,stdev,nparticles)
        n = 0
        for i in range(par_ngroups):
            for j in range(npergroup):
                try:
                    k=i*npergroup+j
                    #print("{} {}".format(k,n))
                    pn[k]=n
                    ptbeg[k]=tbeg+i*tdelta
                    ptend[k]=tend
                    ppathlength[k]=par_pathlength
                    pgroup[k]=i
                    pmark[k]=k+1
                    n = n+1
                except Exception as error:
                    print("An exception occurred:", error)
            # for j END
        # for i END
        if (PARTICLEGROUP=="inc"):
            for i in range(nparticles):
                pgroup[i]=i+1
        if (PARTICLEMARK=="inc"):
            for i in range(nparticles):
                pmark[i]=i+1

    # elif END
    else:
        print("ERROR: Unknown MODE!")
        sys.exit()
    # if-else END
    #

    #
    #
    #Read header base file
    header = io.getFileContent(headerfilefull)
    header = header.replace("##Casename##",casename)
    header = header.replace("##nparticles##",str(nparticles))
    header = header.replace("##time_zone##",TIME_ZONE)
    header = header.replace("##title##",TITLE)
    header = header.replace("##VersionString##",VersionString)
    header = header.replace("##ThisFileString##",ThisFileString)
    
    
   
    data = "\tdata: \n"
  

    
    #===TIME================================================
#     time = ""
#     x = []
#     for i in range (TN):
#         x.append("{:.2f}".format(T[i])+", ")
#     time = ("".join(x)).strip()
#     time = u.replaceLastChar(time,";")  
#     time = "\t\ttime = \n\t\t"+time
    
    datalist = []
    sx = u.generateDataSeries("x",px,nparticles,1,"{:.6f}") # Mask should be "{:.4f}" or similar
    datalist.append(sx)
    sy = u.generateDataSeries("y",py,nparticles,1,"{:.6f}") # Mask should be "{:.4f}" or similar
    datalist.append(sy)
    sz = u.generateDataSeries("z",pz,nparticles,1,"{:.6f}") # Mask should be "{:.4f}" or similar
    datalist.append(sz)
    stbeg = u.generateDataSeries("tbeg",ptbeg,nparticles,1,"{:.6f}") # Mask should be "{:.4f}" or similar
    datalist.append(stbeg)
    stend = u.generateDataSeries("tend",ptend,nparticles,1,"{:.6f}") # Mask should be "{:.4f}" or similar
    datalist.append(stend)
    spathlength = u.generateDataSeries("pathlength",ppathlength,nparticles,1,"{:.6f}") # Mask should be "{:.4f}" or similar
    datalist.append(spathlength)
    sgroup = u.generateDataSeries("group",pgroup,nparticles,1,"{:d}") # Mask should be "{:.4f}" or similar
    datalist.append(sgroup)
    smark = u.generateDataSeries("mark",pmark,nparticles,1,"{:d}") # Mask should be "{:.4f}" or similar
    datalist.append(smark)

    

    
    
    
    
    
    data = data +"\n\n".join(datalist)
    out = header.replace("##data##",data)
    
    print("Writing to file: {}...".format(lagfilecdlfull))
    io.writeFile(lagfilecdlfull,out)
    
    
    print("Generating NetCDF file: {} ...".format(lagfilencfull))
    cmd = "ncgen -b {} -o {}".format(lagfilecdlfull,lagfilencfull)

    os.system(cmd)  
    
    
    print("\n=====Config (for Case / NML file)::=====")
    print(" TIMEZONE        = 'none',")
    print(" DATE_FORMAT     = 'YMD'")
    print(" START_DATE      = 'days={}' ! {}".format(T[0],T_comment))
    print(" END_DATE        = 'days={}' ! {}".format(T[TN-1],T_comment))
    print("=====")


        
    print("End of program.")



