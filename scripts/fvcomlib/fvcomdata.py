# fvcomdata.py - FVCOMData for for FVCOM
# Tested for version FVCOM 5.0.1 (intel)
# Build: xifvcom501
# Veðurstova Føroya 2024
# Jari í Hjøllum, Knud Simonsen
# Version 1.9 05-11-2024
#
import math
import netCDF4
import numpy as np
import fvcomlibio as io
import matplotlib.pyplot as plt
import matplotlib.tri as mtri
import array as arr # importing "array" for array creations
import time
import os.path
from matplotlib.patches import Rectangle
import matplotlib as mpl
import fvcomlibutil as u

VERBOSE = False

nodefields = ["zeta","h"]
elefields  = ["u","v","ww","salinity"]
dkNode = 'node'
dkEle  = 'ele'
WATERVECTORSCALE = 0.65
WINDVECTORSCALE = 0.20


class FVCOMData:
    def __init__(self):
        # CONSTANTS
        self.WATERVECTORSCALE = 0.65
        self.WINDVECTORSCALE = 0.0425
        self.BEAUFORTSCALE = [0.0, 32.7]

        #Variables
        self.filename = ""
        self.fhandle = 0
        # Data conversion
        self.d_datatitle = None # The data structure for export. Should contain 'd_datatitle' and 'd_data'
        self.d_datahandle      = None # The data structure for export. Should contain 'd_datatitle' and 'd_data'
        self.d_elements = None
        self.d_elementcount = 0
        self.d_fields = None
        self.d_fieldcount = 0
        self.d_siglays = None
        self.d_siglaycount = 0

        # Plotting
        self.p = [] # The data structure for plotting.
        self.t = []
        self.x = []
        self.y = []
        self.xc = []
        self.yc = []
        self.nv = []
        self.ele = []
        self.node   = -1 # Number of nodes
        self.nele   = -1 # Number of elements (cells)S
        self.siglay = -1 # Number of siglay's
        self.siglev = -1 # Number of siglev's
        self.times  = -1 # Number of time steps
        # === Data for plotting and analysis ===
        self.loadvars = ["all"]
        self.siglay = []
        self.siglay_kind = dkNode
        self.siglev = []
        self.siglev_kind = dkNode
        self.siglay_center = []
        self.siglay_center_kind = dkEle
        self.siglev_center = []
        self.siglev_center_kind = dkEle
        self.zeta = []
        self.zeta_kind = dkNode
        self.zeta_bounds = []
        self.u = []
        self.u_kind = dkEle
        self.u_bounds = []
        self.v = []
        self.v_kind = dkEle
        self.v_bounds = []
        self.ww = []
        self.ww_kind = dkEle
        self.ww_bounds = []
        self.temp = []
        self.temp_kind = dkNode
        self.temp_bounds = []
        self.salinity = []
        self.salinity_kind = dkNode
        self.salinity_bounds = []
        # === Data Aliases
        self.z = self.zeta
        self.z_kind = self.zeta_kind
        self.z_bounds = self.zeta_bounds

        # === Forcing Values
        self.uwind = []
        self.uwind_kind = dkEle
        self.uwind_bounds = []
        self.vwind = []
        self.vwind_kind = dkEle
        self.vwind_bounds = []
        self.shortwave = []
        self.shortwave_kind = dkNode
        self.shortwave_bounds = []
        self.netheatflux = []
        self.netheatflux_kind = dkNode
        self.netheatflux_bounds = []
        self.precip = []
        self.precip_kind = dkNode
        self.precip_bounds = []
        self.precip_unitdefault = "m/s"
        self.precip_unitsource = "m/s"
        self.precip_unit = self.precip_unitdefault
        self.precip_unitplot = "mm/h"
        self.evap = []
        self.evap_kind = dkNode
        self.evap_bounds = []
        self.evap_unitdefault = "m/s"
        self.evap_unitsource = "m/s"
        self.evap_unit = self.evap_unitdefault
        self.evap_unitplot = "mm/h"
        self.dye = []
        self.dye_kind = dkNode
        self.dye_bounds = []
        self.dye_unitdefault = "m/s"
        self.dye_unitsource = "m/s"
        self.dye_unit = self.dye_unitdefault
        self.dye_unitplot = "mm/h"



        # === Calculated values
        self.c_velocity = []
        self.velocity = []
        self.velocity_kind = self.u_kind
        self.velocity_bounds = []

        self.c_windvelocity = []
        self.windvelocity = []
        self.windvelocity_kind = self.uwind_kind
        self.windvelocity_bounds = []



        # Regular grid
        self.gm = 0 # number of elements in x direction.
        self.gn = 0 # number of elements in y direction.
        self.gx = np.zeros((0,0),dtype=float) # array of int # gridpoints in regular grid.
        self.gy = np.zeros((0,0),dtype=float) # array of int # gridpoints in regular grid.
        self.gri = np.zeros((0,0),dtype=int)  # array(n,m) of int   # index in irregular grid for currennt


        # === VECTORS
        self.vectors = 0
        self.v_x = np.zeros(0)
        self.v_y = np.zeros(0)
        self.v_dx = np.zeros(0)
        self.v_dy = np.zeros(0)

        self.vxsource = np.zeros(0) # Pointer to numpy data array, e.g. u or v
        self.vysource = np.zeros(0) # Pointer to numpy data array, e.g. u or v




        # === Plotting settings ===
        self.p_agg = False
        self.p_blocking = True
        self.p_xinch    = 5
        self.p_yinch    = 5

        self.p_plt=None

        self.p_contourdata = [] # Container for contour data to be plotted.
        self.p_contourkinds = ''
        self.p_contourbounds = []
        self.p_contourunit = ""
        self.p_triangulation = None
        self.p_colormap=mpl.colormaps['jet'] #mpl.colormaps['turbo'] #mpl.colormaps['jet'] # mpl.colormaps['gist_rainbow'] # mpl.colormaps['plasma'] from https://matplotlib.org/stable/users/explain/colors/colormaps.html

        self.p_colormap_overcolorfactor = 1.05
        self.p_colormap_overcolor = 0 # Is overridden during run. Use p_colormap_overcolorfactor is stead.
        self.p_overcolorrangefactor = 10
        self.p_colormap_undercolorfactor = 0.95
        self.p_colormap_undercolor = 0 # Is overridden during run. Use p_colormap_undercolorfactor is stead.
        self.p_undercolorrangefactor = 0.1

        self.setColormap("jet")
        self.p_colorbarlabel_default    = ""
        self.p_colorbarlabel= self.p_colorbarlabel_default
        self.p_vectorscale_default = 0.25
        self.p_vectorscale = self.p_vectorscale_default
        self.p_vectorxdelta_default = 3000
        self.p_vectorxdelta = self.p_vectorxdelta_default
        self.p_vectorydelta_default = 3000
        self.p_vectorydelta = self.p_vectorydelta_default
        self.p_xbounds_default = []
        self.p_xbounds = self.p_xbounds_default
        self.p_ybounds_default = []
        self.p_ybounds = self.p_ybounds_default
        self.p_vectorcolor_default = '#C000C0'
        self.p_vectorcolor = self.p_vectorcolor_default #'#9141AC' #'#E000E0' #606060' #'#888888'
        self.p_lagcolor_default = '#FF0000' # Magenta
        self.p_lagcolor = self.p_lagcolor_default # Magenta
        self.p_colormapbounds_default = []
        self.p_colormapbounds = self.p_colormapbounds_default
        self.p_nLevels_default = 361
        self.p_nLevels = self.p_nLevels_default
        self.p_nTicks_default = 13
        self.p_nTicks  = self.p_nTicks_default

        self.p_levels = [] # is overwritten during plotting, set nLevels, nTicks instead
        self.p_ticks  = [] # is overwritten during plotting, set nLevels, nTicks instead
        self.p_plottingbounds = [-1, -1, -1 , -1] # x01, x1, y0, y1 # is overwritten during plotting, set p_xbounds and p_ybounds instead



        self.p_xlabel = ""
        self.p_ylabel = ""
        self.p_title = ""

        self.p_showxlabel = True
        self.p_showylabel = True
        self.p_showtitle = True

        # Plot (SCATTER)
        self.p_showlegend=False
        self.p_legendlocation="lower right"




        # === LAG ===
        self.lag_active = False


        #self.setPlotSiglev(0)
#==========================================================================

    def convertContourUnit(self,fromUnit,toUnit):
        self.p_contourdata, self.p_contourunit = u.unitConvert(self.p_contourdata,fromUnit,toUnit)
        return 0
# =================================================================
    def loadFile(self,fn,displayInfo=False):
        self.filename= fn
        self.fhandle = netCDF4.Dataset(fn)
        self.nele = self.fhandle.dimensions['nele'].size
        self.node = self.fhandle.dimensions['node'].size
        self.siglay = self.fhandle.dimensions['siglay'].size
        self.siglev = self.fhandle.dimensions['siglev'].size
        self.time = self.fhandle.variables['time']
        self.times = len(self.fhandle.variables['time'])
        print("Nodes        : {}".format(self.node))
        print("Elements     : {}".format(self.nele))
        print("Sigma layers : {}".format(self.siglay))
        print("Sigma levels : {}".format(self.siglev))
        print("Time steps   : {}".format(self.times))

        if (displayInfo):
            self.displayInfo()

# =================================================================
    def loadLagFile(self,fn,displayInfo=False):
        if (os.path.isfile(fn)) :
            self.lag_filename = fn
            self.lag_fhandle = netCDF4.Dataset(fn)
            self.lag_nlag = self.lag_fhandle.dimensions['nlag'].size
            self.lag_times = len(self.lag_fhandle.variables['time'])
            self.lag_time = self.lag_fhandle.variables['time']
            self.lag_lat = self.lag_fhandle.variables['lat']
            self.lag_lon = self.lag_fhandle.variables['lon']
            self.lag_sigma = self.lag_fhandle.variables['sigma']
            self.lag_x = self.lag_fhandle.variables['x']
            self.lag_y = self.lag_fhandle.variables['y']
            self.lag_z = self.lag_fhandle.variables['z']
            print("LAG nlag       : {}".format(self.lag_nlag))
            print("LAG times      : {}".format(self.lag_times))
            print("LAG time size  : {}".format(self.lag_time.size))
            print("LAG lat size   : {}".format(self.lag_lat.shape))
            print("LAG lon size   : {}".format(self.lag_lon.shape))
            print("LAG sigma size : {}".format(self.lag_sigma.shape))
            print("LAG x size     : {}".format(self.lag_x.shape))
            print("LAG y size     : {}".format(self.lag_y.shape))
            print("LAG z size     : {}".format(self.lag_z.shape))
            self.lag_active = True
        else:
            self.lag_active = False


# =================================================================
# displayInfo()::
# Displays data on the nc dataset
#
    def displayInfo(self):
        for dimension in self.fhandle.dimensions.values():
                print(dimension)
        for variable in self.fhandle.variables.values():
            print(variable)
    # END def displayInfo


# =================================================================
# getData()::
# Gets data from the named elements with chosen fields
# Parameters:
#   elements : list of elements for which to load data.
#   fields   : list of fields for which to load data.
# Returns 0
# Writes the generated data into the variables
#   d_datatitle : Array of string title of each data column
#   d_datahandle: Array of handles to the data array
#
    def getData(self,elements,fields, siglays = [0]):
        elementcount = len(elements)
        fieldcount = len(fields)
        siglaycount = len(siglays)

        self.d_datatitle = np.zeros((1 + elementcount * fieldcount * siglaycount), dtype=object)
        self.d_datahandle = np.zeros((1 + elementcount * fieldcount * siglaycount), dtype=object)
        self.d_datatitle[0]='time'
        self.d_datahandle[0]=self.fhandle.variables['time']

        offset = 1 # (time)
        n = offset
        # Raw data fields
        for i in range(elementcount):
            for j in range(fieldcount):
                for k in range (siglaycount):
                    match fields[j]:
                        case "velocity":
                            print("{}_{}_{}".format(j,i,k))
                            self.d_datatitle[n]="{}_{}_{}".format(fields[j],elements[i],siglays[k])
                            u = self.fhandle.variables["u"][:,siglays[k],elements[i]]
                            v = self.fhandle.variables["v"][:,siglays[k],elements[i]]
                            self.d_datahandle[n]=np.sqrt(np.add(np.square(u),np.square(v)))
                            print("self.d_datahandle[{}]: variable: {}   element:{}   siglay:{}  len:  {}".format(n,fields[j],elements[i],siglays[k],len(self.d_datahandle[n])))
                        case _:
                            print("{}_{}_{}".format(j,i,k))
                            self.d_datatitle[n]="{}_{}_{}".format(fields[j],elements[i],siglays[k])
                            self.d_datahandle[n]=self.fhandle.variables[fields[j]][:,siglays[k],elements[i]]

                            print("self.d_datahandle[{}]: variable: {}   element:{}   siglay:{}  len:  {}".format(n,fields[j],elements[i],siglays[k],len(self.d_datahandle[n])))
                        # case END
                    # match END
                    n += 1
                # for k END
            # for j END
        #for i END

        self.d_elements = elements
        self.d_elementcount = elementcount
        self.d_fields = fields
        self.d_fieldcount = fieldcount
        self.d_siglays = siglays
        self.d_siglaycount = siglaycount

        return 0
    # def END
    #


#         self.datatime = t
#         self.datadata = d
    def getLoadVars(self,plotvar):
        result=["all"]
        match plotvar:
            case "siglay":
                result = ["siglay"]
            case "siglev":
                result = ["siglev"]
            case "siglay_center":
                result = ["siglay_center"]
            case "siglev_center":
                result = ["siglev_center"]
            case "z":
                result = ["z","zeta"]
            case "zeta":
                result = ["z","zeta"]
            case "u":
                result = ["u"]
            case "v":
                result = ["v"]
            case "ww":
                result = ["ww"]
            case "temp":
                result = ["temp"]
            case "salinity":
                result = ["salinity"]
            case "uwind":
                result = ["uwind"]
            case "vwind":
                result = ["vwind"]
            case "velocity":
                result = ["velocity", "u", "v"]
            case "velocityvector":
                result = ["velocityvector", "velocity", "u","v"]
            case "windvelocity":
                result = ["windvelocity", "uwind", "vwind"]
            case "windvelocityvector":
                result = ["windvelocityvector", "windvelocity", "uwind", "vwind"]
            case "windvelocityvector":
                result = ["windvelocityvector", "windvelocity", "uwind", "vwind"]
            case "shortwave":
                result = ["shortwave"]
            case "netheatflux":
                result = ["netheatflux"]
            case "precip":
                result = ["precip"]
            case "evap":
                result = ["evap"]
            case "dye":
                result = ["dye"]


            case _:
                print("ERROR: Unknown or NON-implemented variable ({}). Check spelling or implement the new variable.\nValid options are: u, uwind, v, vwind, velocity, velocityvector, windvelocity, windvelocityvector, salinity, temp, z, zeta.".format(var))
        return result
    # def END
    #==========================================================================================================
    #==========================================================================================================
    #==========================================================================================================
    #
    def getVarName(self,vn):
        varNames = {
            "siglay" : "siglay",
            "siglev"  : "siglev",
            "siglay_center"  : "siglay_center",
            "siglev_center" : "siglev_center",
            "z"   : "zeta",
            "zeta"  : "zeta",
            "u" : "U",
            "v"  : "v",
            "ww"   : "ww",
            "temp"  : "temp",
            "salinity" : "salinity",
            "uwind"   : "uwind",
            "vwind"  : "vwind",
            "velocity"  : "velocity",
            "velocityvector"   : "velocityvector",
            "windvelocity"  : "windvelocity",
            "windvelocityvector"   : "windvelocityvector",
            "shortwave"   : "shortwave",
            "netheatflux"   : "netheatflux",
            "precip"   : "precip",
            "evap"   : "evap",
            "dye"   : "dye",
        }
        return varNames.get(vn, None)
    # def END
    #==========================================================================================================
    #==========================================================================================================
    #==========================================================================================================
    #
    def getVarTitle(self,vn):
        varTitles = {
            "siglay" : "siglay",
            "siglev"  : "siglev",
            "siglay_center"  : "siglay_center",
            "siglev_center" : "siglev_center",
            "z"   : "Waterlevel",
            "zeta"  : "Waterlevel",
            "u" : "U-ward velocity",
            "v"  : "V-ward velocity",
            "ww"   : "W-ward velocity",
            "temp"  : "Temperature",
            "salinity" : "Salinity",
            "uwind"   : "U-wind",
            "vwind"  : "V-wind",
            "velocity"  : "Water velocity",
            "velocityvector"   : "Water velocity vector",
            "windvelocity"  : "Wind velocity",
            "windvelocityvector"   : "Wind velocity vector",
            "shortwave"   : "Short wave radiation",
            "netheatflux"   : "Net heat flux",
            "precip"   : "Precipitation",
            "evap"   : "Evaporation",
            "dye"   : "Dye",
        }
        return varTitles.get(vn, None)
    # def END
    #==========================================================================================================
    #==========================================================================================================
    #==========================================================================================================
    #
    def getVarUnit(self,vn):
        varUnits = {
            "siglay" : "#",
            "siglev"  : "#",
            "siglay_center"  : "m",
            "siglev_center" : "m",
            "z"   : "m",
            "zeta"  : "m",
            "u" : "m/s",
            "v"  : "m/S",
            "ww"   : "m/s",
            "temp"  : "°C",
            "salinity" : "‰ NaCl",
            "uwind"   : "m/s",
            "vwind"  : "m/s",
            "velocity"  : "m/s",
            "velocityvector"   : "m/s",
            "windvelocity"  : "m/s",
            "windvelocityvector"   : "m/s",
            "shortwave"   : "W/m2",
            "netheatflux"   : "W/m2",
            "precip"   : "m/s",
            "evap"   : "m/s",
            "dye"   : "kg/m3",
        }
        return varUnits.get(vn, None)
    # def END
    #==========================================================================================================
    #==========================================================================================================
    #==========================================================================================================
    #
    def getVarCBTitleUnit(self,vn):
        return "{} ({})".format(self.getVarTitle(vn),self.getVarUnit(vn))
    # def END
    #==========================================================================================================
    #==========================================================================================================
    #==========================================================================================================
#
# Parameters:
#   plottimestep     : time index to be plotted
#   plotsiglaystep   : time index to be plotted
    def getPlotData(self,timestep,siglaystep):
        self.setPlotTimeStep(timestep)
        self.setPlotSiglayStep(siglaystep)

        self.t=np.array(self.fhandle.variables['time'])
        self.p_time=np.array(self.t[self.p_timestep])
        print("Time loaded.")
        self.x=np.array(self.fhandle.variables['x'])
        print("X loaded.")
        self.y=np.array(self.fhandle.variables['y'])
        print("Y loaded.")
        self.xc=np.array(self.fhandle.variables['xc'])
        print("XC loaded.")
        self.yc=np.array(self.fhandle.variables['yc'])
        print("YC loaded.")
        self.h=np.array(self.fhandle.variables['h']) #  "Bathymetry" ;
        print("H loaded.")
        self.nv=np.transpose(np.array(self.fhandle.variables['nv'])-1)
        print("NV loaded.")
        self.loadPlotData(self.p_timestep,self.p_siglaystep)

#===================================================================================================================================
# loadPLotData
# Input:
#
#
#
    def loadPlotData(self,timestep,siglaystep):
        self.setPlotTimeStep(timestep)
        self.setPlotSiglayStep(siglaystep)
        self.setPlotSiglevStep(0)

        if ( ("siglay" in self.loadvars) or ("all" in self.loadvars) ):
            print("SIGLAY DIM: {}".format(self.fhandle.variables['siglay'].shape))
            self.siglay = np.array(self.fhandle.variables['siglay'][self.p_siglaystep,:])
            print("SIGLAY (kind={}, siglay={}) loaded.".format(self.siglay_kind,self.p_siglaystep))

        if ( ("siglev" in self.loadvars) or ("all" in self.loadvars) ):
            print("SIGLEV DIM: {}".format(self.fhandle.variables['siglev'].shape))
            self.siglev = np.array(self.fhandle.variables['siglev'][self.p_siglevstep,:])
            print("SIGLEV (kind={}, siglay={}) loaded.".format(self.siglev_kind,self.p_siglaystep))

        if ( ("siglay_center" in self.loadvars) or ("all" in self.loadvars) ):
            try:
                self.siglay_center = np.array(self.fhandle.variables['siglay_center'][self.p_siglaystep,:])
                print("SIGLAY_CENTER (kind={}, siglay={}) loaded.".format(self.siglay_center_kind,self.p_siglaystep))
            except:
                print("SIGLAY_CENTER not found in dataset.")


        if ( ("siglev_center" in self.loadvars) or ("all" in self.loadvars) ):
            try:
                self.siglev_center = np.array(self.fhandle.variables['siglev_center'][self.p_timestep,:])
                print("SIGLEV_CENTER (kind={}, siglay={}) loaded.".format(self.siglev_center_kind,self.p_siglaystep))
            except:
                print("SIGLAY_CENTER not found in dataset.")

        if ( ("zeta" in self.loadvars) or ("all" in self.loadvars) ):
            self.zeta=np.array(self.fhandle.variables['zeta'][self.p_timestep,:]) # "Water Surface Elevation"
            if ( len(self.zeta_bounds)==0 ) :
                self.zeta_bounds=[ np.min(self.fhandle.variables['zeta'][:,:]), np.max(self.fhandle.variables['zeta'][:,:]) ]
            self.z=self.zeta
            self.z_kind=self.zeta_kind
            self.z_bounds = self.zeta_bounds
            print("ZETA/Z (kind={}, siglay={}) loaded.".format(self.zeta_kind,self.p_siglaystep))


        if ( ("u" in self.loadvars) or ("all" in self.loadvars) ):
            self.u=np.array(self.fhandle.variables['u'][self.p_timestep,self.p_siglaystep,:])
            if ( len(self.u_bounds)==0 ) :
                self.u_bounds=[ np.min(self.fhandle.variables['u'][:,:,:]), np.max(self.fhandle.variables['u'][:,:,:]) ]
            print("U (kind={}, timestep={}, siglay={}) loaded.".format(self.u_kind,self.p_timestep,self.p_siglaystep))

        if ( ("v" in self.loadvars) or ("all" in self.loadvars) ):
            self.v=np.array(self.fhandle.variables['v'][self.p_timestep,self.p_siglaystep,:])
            if ( len(self.v_bounds)==0 ) :
                self.v_bounds=[ np.min(self.fhandle.variables['v'][:,:,:]), np.max(self.fhandle.variables['v'][:,:,:]) ]
            print("V (kind={}, timestep={}, siglay={}) loaded.".format(self.v_kind,self.p_timestep,self.p_siglaystep))

        if ( ("ww" in self.loadvars) or ("all" in self.loadvars) ):
            self.ww=np.array(self.fhandle.variables['ww'][self.p_timestep,self.p_siglaystep,:])
    #         self.ww_kind='ele'
            if ( len(self.ww_bounds)==0 ) :
                self.ww_bounds=[ np.min(self.fhandle.variables['ww'][:,:,:]), np.max(self.fhandle.variables['ww'][:,:,:]) ]
            print("ww (kind={}, timestep={}, siglay={}) loaded.".format(self.ww_kind,self.p_timestep,self.p_siglaystep))

        if ( ("temp" in self.loadvars) or ("all" in self.loadvars) ):
            self.temp=np.array(self.fhandle.variables['temp'][self.p_timestep,self.p_siglaystep,:])
            if ( len(self.temp_bounds)==0 ) :
                self.temp_bounds=[ np.min(self.fhandle.variables['temp'][:,:,:]), np.max(self.fhandle.variables['temp'][:,:,:]) ]
            print("TEMP (kind={}, timestep={}, siglay={}) loaded.".format(self.temp_kind,self.p_timestep,self.p_siglaystep))

        if ( ("salinity" in self.loadvars) or ("all" in self.loadvars) ):
            self.salinity=np.array(self.fhandle.variables['salinity'][self.p_timestep,self.p_siglaystep,:])
            if ( len(self.salinity_bounds)==0 ) :
                self.salinity_bounds=[ np.min(self.fhandle.variables['salinity'][:,:,:]), np.max(self.fhandle.variables['salinity'][:,:,:]) ]
            print("SALINITY (kind={}, timestep={}, siglay={}) loaded.".format(self.salinity_kind,self.p_timestep,self.p_siglaystep))


        # === FORCING VALUES =============================================================================================
        if ( ("uwind" in self.loadvars) or ("all" in self.loadvars) ):
            try:
                self.uwind=np.array(self.fhandle.variables['uwind_speed'][self.p_timestep,:])
                if ( len(self.uwind_bounds)==0 ) :
                    self.uwind_bounds=[ np.min(self.fhandle.variables['uwind_speed'][:,:]), np.max(self.fhandle.variables['uwind_speed'][:,:]) ]
                print("UWIND (kind={}, timestep={}, siglay={}) loaded.".format(self.uwind_kind,self.p_timestep,self.p_siglaystep))
            except:
                print("UWIND not found in dataset.")

        if ( ("vwind" in self.loadvars) or ("all" in self.loadvars) ):
            try:
                self.vwind=np.array(self.fhandle.variables['vwind_speed'][self.p_timestep,:])
                if ( len(self.vwind_bounds)==0 ) :
                    self.vwind_bounds=[ np.min(self.fhandle.variables['vwind_speed'][:,:]), np.max(self.fhandle.variables['vwind_speed'][:,:]) ]
                print("VWIND (kind={}, timestep={}, siglay={}) loaded.".format(self.vwind_kind,self.p_timestep,self.p_siglaystep))
            except Exception as e:
                print("VWIND not found in dataset. [{}]".format(e))


        if ( ("shortwave" in self.loadvars) or ("all" in self.loadvars) ):
            try:
                self.shortwave=np.array(self.fhandle.variables['short_wave'][self.p_timestep,:])
                if ( len(self.shortwave_bounds)==0 ) :
                    self.shortwave_bounds=[ np.min(self.fhandle.variables['short_wave'][:,:]), np.max(self.fhandle.variables['short_wave'][:,:]) ]
                print("SHORTWAVE (kind={}, timestep={}, siglay={}) loaded.".format(self.shortwave_kind,self.p_timestep,self.p_siglaystep))
            except Exception as e:
                print("SHORTWAVE not found in dataset. [{}]".format(e))
            # try END
        # if END

        if ( ("netheatflux" in self.loadvars) or ("all" in self.loadvars) ):
            try:
                self.netheatflux=np.array(self.fhandle.variables['net_heat_flux'][self.p_timestep,:])
                if ( len(self.netheatflux_bounds)==0 ) :
                    self.netheatflux_bounds=[ np.min(self.fhandle.variables['net_heat_flux'][:,:]), np.max(self.fhandle.variables['net_heat_flux'][:,:]) ]
                print("NETHEATFLUX (kind={}, timestep={}, siglay={}) loaded.".format(self.netheatflux_kind,self.p_timestep,self.p_siglaystep))
            except Exception as e:
                print("NETHEATFLUX not found in dataset. [{}]".format(e))
            # try END
        # if END

        fieldname="precip"
        if ( (fieldname in self.loadvars) or ("all" in self.loadvars) ):
            try:
                # Read the data itself
                self.precip=np.array(self.fhandle.variables[fieldname][self.p_timestep,:])
                # Read the bounds
                if ( len(self.precip_bounds)==0 ) :
                    self.precip_bounds=[ np.min(self.fhandle.variables[fieldname][:,:]),  np.max(self.fhandle.variables[fieldname][:,:]) ]
                # if END
                print("{} (kind={}, timestep={}, siglay={}, unit={}) loaded.".format(fieldname.upper(),self.precip_kind,self.p_timestep,self.p_siglaystep,self.precip_unit))
            except Exception as e:
                print("{} not found in dataset. [{}]".format(fieldname.upper(),e))
            # try END
        # if END


        fieldname="evap"
        if ( (fieldname in self.loadvars) or ("all" in self.loadvars) ):
            try:
                # Read the data itself
                self.evap=np.array(self.fhandle.variables[fieldname][self.p_timestep,:])
                # Read the bounds
                if ( len(self.evap_bounds)==0 ) :
                    self.evap_bounds=[ np.min(self.fhandle.variables[fieldname][:,:]), np.max(self.fhandle.variables[fieldname][:,:]) ]
                # if END
                print("{} (kind={}, timestep={}, siglay={}, unit={}) loaded.".format(fieldname.upper(),self.evap_kind,self.p_timestep,self.p_siglaystep,self.evap_unit))
                print("shape {}".format(self.evap.shape))
            except Exception as e:
                print("{} not found in dataset. [{}]".format(fieldname.upper(),e))
            # try END
        # if END

        fieldname="dye"
        if ( (fieldname in self.loadvars) or ("all" in self.loadvars) ):
            try:
                # Read the data itself
                self.dye=np.array(self.fhandle.variables['DYE'][self.p_timestep,self.p_siglaystep,:])
                # Read the bounds
                if ( len(self.dye_bounds)==0 ) :
                    self.dye_bounds=[ np.min(self.fhandle.variables['DYE'][:,:,:]), np.max(self.fhandle.variables['DYE'][:,:,:]) ]
                # if END
                print("{} (kind={}, timestep={}, siglay={}, unit={}) loaded.".format(fieldname.upper(),self.dye_kind,self.p_timestep,self.p_siglaystep,self.dye_unit))
                print("shape {}".format(self.dye.shape))
            except Exception as e:
                print("{} not found in dataset. [{}]".format(fieldname.upper(),e))
            # try END
        # if END





        # === CALCULATED VALUES =============================================================================================
        # OBS Calculated value
        #
        # VELOCITY
        if ( ("velocity" in self.loadvars) or ("all" in self.loadvars) ):
            if ( len(self.c_velocity)== 0):
                print("Calculating the velocity variables for ALL points...")
                t1 = self.fhandle.variables['u'][:,:,:]
                t2 = self.fhandle.variables['v'][:,:,:]
                self.c_velocity = np.sqrt(np.add(np.square(t1),np.square(t2)))
            #self.velocity = np.sqrt(np.add(np.square(self.u),np.square(self.v)))
            self.velocity = self.c_velocity[self.p_timestep,self.p_siglaystep,:]
            self.velocity_kind = self.u_kind
            if ( len(self.velocity_bounds)==0 ) :
                self.velocity_bounds=[ np.min(self.c_velocity), np.max(self.c_velocity) ]
                print("Velocity bounds found: {} {}".format(self.velocity_bounds[0],self.velocity_bounds[1]))

            (i_velmin, j_velmin, k_velmin) = np.unravel_index(np.argmin(self.c_velocity, axis=None), self.c_velocity.shape)
            if VERBOSE: print("MIN timestep: {} Siglay: {}, Element or Node: {}".format(i_velmin, j_velmin, k_velmin))
            if VERBOSE: print("MIN VALUE: {}.".format(self.c_velocity[i_velmin, j_velmin, k_velmin]))

            (i_velmax, j_velmax, k_velmax) = np.unravel_index(np.argmax(self.c_velocity, axis=None), self.c_velocity.shape)
            if VERBOSE: print("MAX timestep: {} Siglay: {}, Element or Node: {}".format(i_velmax, j_velmax, k_velmax))
            if VERBOSE: print("MAX VALUE: {}.".format(self.c_velocity[i_velmax, j_velmax, k_velmax]))
            if VERBOSE: print("VELOCITY (kind={}, timestep={}, siglay={}) calculated.".format(self.velocity_kind,self.p_timestep,self.p_siglaystep))
        #
        # WINDVELOCITY
        if ( ("windvelocity" in self.loadvars) or ("all" in self.loadvars) ):
            if ( len(self.c_windvelocity)== 0):
                print("Calculating the windvelocity variables for ALL points...")
                t1 = self.fhandle.variables['uwind_speed'][:,:]
                t2 = self.fhandle.variables['vwind_speed'][:,:]
                self.c_windvelocity = np.sqrt(np.add(np.square(t1),np.square(t2)))
            self.windvelocity = self.c_windvelocity[self.p_timestep,:]
            self.windvelocity_kind = self.u_kind
            if ( len(self.windvelocity_bounds)==0 ) :
                self.windvelocity_bounds=[ np.min(self.c_windvelocity), np.max(self.c_windvelocity) ]
                print("Velocity bounds found: {} {}".format(self.windvelocity_bounds[0],self.windvelocity_bounds[1]))
            print("VELOCITY (kind={}, timestep={}, siglay={}) calculated.".format(self.windvelocity_kind,self.p_timestep,self.p_siglaystep))




#===================================================================================================================================
# PLOT
#
    def plot(self):

        #===============PLOT INTI BEGIN================================================================================================
        #
        #/opt/fvcom/cron/sims/m/s/xiSim501/FAR/far2024-10-01/scripts/fvcomdata.py:461: RuntimeWarning: More than 20 figu
        #res have been opened. Figures created through the pyplot interface (`matplotlib.pyplot.figure`) are retained un
        #til explicitly closed and may consume too much memory. (To control this warning, see the rcParam `figure.max_op
        #en_warning`). Consider using `matplotlib.pyplot.close()`.
        if (self.p_plt != None ):
            self.p_plt.close()
        self.p_plt=plt
        fig = plt.figure()
        fig.set_size_inches(self.p_xinch, self.p_yinch)
        ax = fig.add_subplot(1,1,1)
        #===============PLOT INTI END===============================================================================================

        #===============PLOTTING BOUNDS BEGIN================================================================================================
        #
        # Plot bounds BEGIN
        plotmargin=1e-4
        if (len(self.p_xbounds)==2):
            self.p_plottingbounds[0] = (1-plotmargin)*self.p_xbounds[0]
            self.p_plottingbounds[1] = (1+plotmargin)*self.p_xbounds[1]
        else:
            self.p_plottingbounds[0] = (1-plotmargin)*np.min(self.x)
            self.p_plottingbounds[1] = (1+plotmargin)*np.max(self.x)
        # if END
        self.p_plt.xlim(self.p_plottingbounds[0], self.p_plottingbounds[1])
        #
        if (len(self.p_ybounds)==2):
            self.p_plottingbounds[2] = (1-plotmargin)*self.p_ybounds[0]
            self.p_plottingbounds[3] = (1+plotmargin)*self.p_ybounds[1]
        else:
            self.p_plottingbounds[2] = (1-plotmargin)*np.min(self.y)
            self.p_plottingbounds[3] = (1+plotmargin)*np.max(self.y)
        # if END
        self.p_plt.ylim(self.p_plottingbounds[2], self.p_plottingbounds[3])
        #===============PLOTTING BOUNDS BEGIN================================================================================================



        #===============COUNTOUR BEGIN=============================================================================================
        # From : https://www.fabrizioguerrieri.com/blog/surface-graphs-with-irregular-dataset/
        if (self.p_triangulation == None ):
            self.p_triangulation = mtri.Triangulation(self.x, self.y, self.nv) # Must have -1 here, since np arrays are 0-indexed.
        # triplot: https://matplotlib.org/stable/api/tri_api.html
        ax.triplot(self.p_triangulation, linewidth=0.5, c="#D3D3D3", markerfacecolor="#DC143C",markeredgecolor="black", markersize=10)
        ax.set_xlabel('X (m)')
        ax.set_ylabel('Y (m)')
        epsilon=1e-7
        #
        # IF p_contourbounds is set, it mean there are predefined bounds, most likely from loading of data.
        if ( len(self.p_contourbounds)==0):# If there are no global extrema for the entire dataset, use separate for each image.
            pmin=np.min(self.p_contourdata)
            pmax=np.max(self.p_contourdata)

            if ( (abs(pmax - pmin) < 1e-10) ):
                pmax = pmin + 1
                print("WARNING: MAX and MIN identical. Aurocorrected MAX to {}.".format(pmax))
            # if END
        else: # Use global.
            pmin=self.p_contourbounds[0]
            pmax=self.p_contourbounds[1]
            if ( (abs(pmax - pmin) < 1e-20) ):
                pmax = pmin * 2 + 1e-10
                print("WARNING: MAX and MIN identical. Aurocorrected MAX to {}.".format(pmax))
            elif ( (abs(pmax - pmin) < 1e-15) ):
                pmax = pmin * 2 + 1e-8
                print("WARNING: MAX and MIN identical. Aurocorrected MAX to {}.".format(pmax))
            elif ( (abs(pmax - pmin) < 1e-10) ):
                pmax = pmin * 2 + 1e-5
                print("WARNING: MAX and MIN identical. Aurocorrected MAX to {}.".format(pmax))
            # if END

        # if END
        #
        if VERBOSE: print("P (VERBOSE)     Min Max {:+12.10f} {:+12.10f}".format(pmin,pmax))
        print("Defined Contour Min Max {:+12.10f} {:+12.10f}".format(self.p_contourbounds[0],self.p_contourbounds[1]))
        print("Found   Contour Min Max {:+12.10f} {:+12.10f}".format(np.min(self.p_contourdata),np.max(self.p_contourdata)))
        tpmin = pmin*(1-epsilon)
        tpmax = pmax*(1+epsilon)
        tprange = tpmax-tpmin
        tpdelta = tprange /(self.p_nLevels)
        print("TP      Contour Min Max {:+12.10f} {:+12.10f}".format(tpmin,tpmax))

        self.p_levels = np.linspace(tpmin,tpmax,self.p_nLevels)
        self.p_levels = np.append(self.p_levels,self.p_overcolorrangefactor*tpmax+tpdelta) # Overcolor
        self.p_levels = np.insert(self.p_levels,0,self.p_undercolorrangefactor*tpmin-tpdelta) # Undercolor
        self.p_ticks = np.linspace(tpmin,tpmax,self.p_nTicks)
        #
        # === PLOT CONTOUR ===
        if (self.p_contourkind == 'node'): # node
            #self.p_tripcolor = ax.tricontourf(self.p_triangulation, self.p_contourdata, levels=self.p_levels, cmap=self.p_colormap)

            # ORG - THIS WORKS! DO NOT DELETE THIS WHATEVER YOU DO
            self.p_tripcolor = ax.tricontourf(self.p_triangulation, self.p_contourdata, vmin=tpmin, vmax=tpmax, levels=self.p_levels, cmap=self.p_colormap)
            #self.p_tripcolor = ax.tricontourf(self.p_triangulation, self.p_contourdata, vmin=tpmin, vmax=tpmax, cmap=self.p_colormap)

        if (self.p_contourkind == 'ele'): # ele
              #print("Length of xtriang: {}, xc: {}, yc: {}, data:{}".format(len(self.p_triangulation.x),len(self.xc),len(self.yc),len(self.p_contourdata)))

              self.p_tripcolor = ax.tripcolor(self.p_triangulation, self.p_contourdata,vmin=tpmin, vmax=tpmax, cmap=self.p_colormap)

        self.showColorbar()
        #===============COUNTOUR END====================================================================================

        #===============VECTORS BEGIN===================================================================================
        if (len(self.vxsource)>0 and len(self.vxsource)>0 ):
            delta = 0.5 * (self.p_vectorxdelta + self.p_vectorydelta) # average of x and y-delta
            kk = self.p_vectorscale * delta

            #vectorbounds=[-60000,60000,-85000,60000]
            if ( len(self.gx) == 0):
                self.populateRegularGrid([self.p_plottingbounds[0], self.p_plottingbounds[1], self.p_vectorxdelta, self.p_plottingbounds[2], self.p_plottingbounds[3], self.p_vectorydelta])
            # if END
            for i in range(self.gm):
                for j in range(self.gn):
                    plt.arrow(self.xc[self.gri[i][j]], self.yc[self.gri[i][j]],
                              kk*self.vxsource[self.gri[i][j]], kk*self.vysource[self.gri[i][j]],
                               head_width = 500.2, width = 0.05, color = self.p_vectorcolor)
                    if VERBOSE:
                        print("Arrow {} {} {} {}.".format(self.xc[self.gri[i][j]], self.yc[self.gri[i][j]], kk*self.vxsource[self.gri[i][j]], kk*self.vysource[self.gri[i][j]]))
                    # if END
                # for j END
            # for i END
            #
            # Draw vector legend
            dx=self.p_plottingbounds[1]-self.p_plottingbounds[0]
            dy=self.p_plottingbounds[3]-self.p_plottingbounds[2]
            rec=plt.Rectangle((self.p_plottingbounds[0], self.p_plottingbounds[2]), (dx)*0.15, (dy)*0.05, edgecolor='black',facecolor='white')
            r=ax.add_patch(rec)
            #
            if (self.p_vectorscale > 0.2):
                vlen = 2.0
            else:
                vlen = 10.0
            # if END
            plt.arrow(self.p_plottingbounds[0]+0.02*dx, self.p_plottingbounds[2]+0.032*dy,kk*vlen, 0,head_width = 500.2, width = 0.05,
                      color=self.p_vectorcolor)
            plt.text(self.p_plottingbounds[0]+0.02*dx, self.p_plottingbounds[2]+0.006*dy, "{} m/s".format(vlen), fontsize = 12, horizontalalignment='left',     verticalalignment='bottom')


        #===============VECTORS END ================================================================================================

        #===============LAG BEGIN==============================================================================================
        if ( self.lag_active ):
            print("Time: {} LAG: {}.".format(self.time[self.p_timestep],self.lag_time[self.p_timestep]))
            iLagTime = np.argmin(np.abs(self.lag_time-self.time[self.p_timestep]))
            print("LAG iLagTime {}".format(iLagTime))
            for i in range(self.lag_nlag):
                #print("P {}: x:{}  y:{}".format(i,self.lag_x[iLagTime][i],self.lag_y[iLagTime][i]))
                circle1 = plt.Circle((self.lag_x[iLagTime][i],self.lag_y[iLagTime][i]), 100, color=self.p_lagcolor)
                ax.add_patch(circle1)

        #===============LAG END ================================================================================================






        # if END
        #
        # Finalize plot
        self.p_figure=fig
        if (not self.p_blocking):
            plt.ion() #if non-blocking
        plt.draw()
        plt.subplots_adjust(left=0.06, right=0.96, top=0.95, bottom=0.05)
        plt.show()
    # def END
    #
    #
    #
    #
    #===============================================================================================================================
    # plotScatter
    def plotScatter(self):
        if (self.p_plt != None ):
            self.p_plt.close()
        # if END
        self.p_plt=plt

        if (not self.p_blocking):
            plt.ion() #if non-blocking
        # if END
        if (self.p_agg):
            mpl.use("Agg")
        # if END

        fig = plt.figure()
        fig.set_size_inches(self.p_xinch, self.p_yinch)
        ax = fig.add_subplot(1,1,1)

        for i in range(1,len(self.d_datahandle)):
            plt.scatter(self.d_datahandle[0][:],self.d_datahandle[i][:],s=10)

        if (self.p_showlegend):
            plt.legend(self.d_datatitle[1:],loc=self.p_legendlocation)

        if (self.p_showxlabel and len(self.p_xlabel)>0):
            plt.xlabel(self.p_xlabel)

        if (self.p_showylabel and len(self.p_ylabel)>0):
            plt.ylabel(self.p_ylabel)


        if (self.p_showtitle and len(self.p_title)>0):
            plt.title(self.p_title)



        self.p_figure=fig
        plt.draw()
        plt.subplots_adjust(left=0.06, right=0.96, top=0.95, bottom=0.05)
        plt.show()
    # def END
    #
    #
    #
    #
    #===============================================================================================================================
        def sqr(self, x):
            return x*x
    # def END
    #
    #===============================================================================================================================
    # populateRegularGrid
    #  input:
    # grid = [xmin, xmax, xdelta, ymin, ymax, ydelta]
    def populateRegularGrid(self, grid):

       # xc, yc # center of elements

        self.gxdim = [grid[0], grid[1], grid[2]] # xmin, xmax, xdelta  # (60000 - -60000) / 5000 +1 = 120.000 / 5.000 = 24 + 1 = 25
        self.gydim = [grid[3], grid[4], grid[5]] # ymin, ymax, ydelta


        self.gm = int( (self.gxdim[1]-self.gxdim[0])/self.gxdim[2] + 1 )
        self.gn = int( (self.gydim[1]-self.gydim[0])/self.gydim[2] + 1 )

        self.gx = np.zeros((self.gm,self.gn),dtype=float)
        self.gy = np.zeros((self.gn,self.gn),dtype=float)
        self.gri = np.zeros((self.gm,self.gn),dtype=int)

        # Build regular grid
        for i in range(self.gm):
            for j in range(self.gn):
                self.gx[i][j]=i*self.gxdim[2] + self.gxdim[0]
                self.gy[i][j]=j*self.gydim[2] + self.gydim[0]
                self.gri[i][j]=i*self.gm+j


        ##d2 = np.add(np.square(np.subtract(self.gx[i],self.xc),np.square(np.subtract(self.gy,s))))
        for i in range(self.gm):
            for j in range(self.gn):
                d2best = 1e24
                ibest = -1
                d2 = np.add( np.square(np.subtract(self.gx[i][j],self.xc)) , np.square(np.subtract(self.gy[i][j],self.yc)) )
                #print("shape of x-GRID: {}".format(d2.shape))
                ibest = np.argmin(d2)
                self.gri[i][j]=ibest
            ## for j end
        ## for i end
        return self.gri, self.gm, self.gn
    # def END

#===================================================================================================================================
# showColorbar
#
    def showColorbar(self):
        #self.p_cbar = self.p_plt.colorbar(self.p_tripcolor, ticks=self.p_levels, format='%.4f')
        if ( (max(abs(self.p_ticks))>1000) or (max(abs(self.p_ticks))<0.001) ):
            p_colorbartickmask='%.3e'
        elif max(abs(self.p_ticks))<0.01 :
            p_colorbartickmask='%.4f'
        elif max(abs(self.p_ticks))<0.1 :
            p_colorbartickmask='%.4f'
        else :
            p_colorbartickmask='%.3f'
        #
        if self.p_colorbarlabel == "":
            self.p_colorbarlabel = self.p_contourunit

        self.p_cbar = plt.colorbar(self.p_tripcolor, ticks=self.p_ticks, format=p_colorbartickmask, label = self.p_colorbarlabel)


        #self.p_cbar = self.p_plt.colorbar(self.p_tripcolor)
    # def END

#==================================================================================================================================
#==================================================================================================================================
    def setColormap(self,cmname):
        self.p_colormap=mpl.colormaps[cmname]
        self.p_colormap_overcolor = u.lighten_color( self.p_colormap(1.0), self.p_colormap_overcolorfactor)
        self.p_colormap.set_over(self.p_colormap_overcolor)
        self.p_colormap_undercolor = u.lighten_color( self.p_colormap(0.0), self.p_colormap_undercolorfactor)
        self.p_colormap.set_under(self.p_colormap_undercolor)
        #self.p_colormap.set_under('k')
        return self.p_colormap
    # def END
#==================================================================================================================================
#==================================================================================================================================

#===================================================================================================================================
    #def setContour(self,contourdata,contourkind):
        #if VERBOSE: print("Shape of contour data: {}".format(contourdata.shape))
        #self.p_contourdata=contourdata
        #self.p_contourkind=contourkind # node / ele
        #self.p_contourbounds = []

#===================================================================================================================================
    def setContour(self,contourdata,contourkind='',countourbounds=[],contourunit="",plotcontourunit=""):
        if VERBOSE: print("Shape of contour data: {}".format(contourdata.shape))
        if (plotcontourunit!="" and plotcontourunit!=contourunit):
            self.p_contourunit = plotcontourunit
            uc = u.unitConvertFactor(contourunit,plotcontourunit)
            self.p_contourdata=np.multiply( uc, contourdata )
            if (len(countourbounds)>0):
                self.p_contourbounds = u.listMultiply( uc, countourbounds.copy())
                print("Countourbounds: {} ".format(self.p_contourbounds))
            # if END
        else:
            self.p_contourdata=contourdata
            if (len(countourbounds)>0):
                self.p_contourbounds =  countourbounds
                print("Countourbounds: {} ".format(self.p_contourbounds))
            # if END

        # if END
        if (len(contourkind)>0):
            self.p_contourkind=contourkind # node / ele
        # if END

    # def END
    #====================================================================================================
    #====================================================================================================
    #
    def setVariableName(self,vn):
        self.p_variableName=vn
    #def END
    #====================================================================================================
    #====================================================================================================

#===================================================================================================================================
    def setVectors(self, xvector, yvector):
        self.vxsource = xvector
        self.vysource = yvector

#===================================================================================================================================
    def setVectorScale(self, vs):
        self.p_vectorscale = vs

#===================================================================================================================================
    def setVectorColor(self, vc):
        self.p_vectorcolor = vc

#===================================================================================================================================
    def setVectorDelta(self, vxd, vyd):
        self.p_vectorxdelta = vxd
        self.p_vectorydelta = vyd


#===================================================================================================================================
    def setVectorCount(self, vectorcount):
        self.vectors = vectorlen
        self.v_x = np.zeros(self.vectors)
        self.v_y = np.zeros(self.vectors)
        self.v_dx = np.zeros(self.vectors)
        self.v_dy = np.zeros(self.vectors)

#===================================================================================================================================
    def setPlotTimeStep(self,timestep):
        self.p_timestep = timestep

#===================================================================================================================================
    def setPlotAGG(self, agg):
        self.p_agg = agg
#===================================================================================================================================
    def setPlotSiglayStep(self,siglaystep):
        self.p_siglaystep = siglaystep
#===================================================================================================================================
    def setPlotSiglevStep(self,siglevstep):
        self.p_siglevstep = siglevstep
#===================================================================================================================================
    def setPlotBlocking(self,value):
        self.p_blocking=value
#===================================================================================================================================
    def setPlotSize(self,pxinch,pyinch):
        self.p_xinch = pxinch
        self.p_yinch = pyinch
#===================================================================================================================================
    def saveplot(self,fn):
        self.p_figure.savefig(fn)
        print("Saved figure to file: {}".format(fn))
#===================================================================================================================================

    def p_Reset(self):
        print("Resetting plot settings...")
        self.p_colorbarlabel    = self.p_colorbarlabel_default
        self.p_vectorscale      = self.p_vectorscale_default
        self.p_vectorxdelta     = self.p_vectorxdelta_default
        self.p_vectorydelta     = self.p_vectorydelta_default
        self.p_bounds           = self.p_bounds_default
        self.p_vectorcolor      = self.p_vectorcolor_default #'#9141AC' #'#E000E0' #606060' #'#888888'
        self.p_lagcolor         = self.p_lagcolor_default # Magenta
        self.p_colormapbounds   = self.p_colormapbounds_default
        self.p_nLevels          = self.p_nLevels_default
        self.p_nTicks           = self.p_nTicks_default
    #def END

#======================================================================
# generateTriangles
# OLD : Not intended for use. However, it works.
    def XXOLDgenerateTriangles(self):
        nan=math.nan
        xx = []
        yy = []

        for index in range(len(self.nv[0,:])):
            i0 = self.nv[0,index-1]
            i1 = self.nv[1,index-1]
            i2 = self.nv[2,index-1]
    ##        print("Element index {} is defined by nodes {}, {}, {}.".format(index+1,i0,i1,i2))
            x0=self.x[i0-1]
            x1=self.x[i1-1]
            x2=self.x[i2-1]

            y0=self.y[i0-1]
            y1=self.y[i1-1]
            y2=self.y[i2-1]
            xx.append([x0,x1,x2])
            yy.append([y0,y1,y2])

            if ((index % 1000==0)):
                print("index {}...".format(index))
        self.xx=np.array(xx)
        self.yy=np.array(yy)



    def exportcsv(self,fn,separator=","):
        s = []
        ss=[]
        for j in range(len(self.d_datatitle)):
            ss.append(self.d_datatitle[j])
        s.append(separator.join(ss))
        for i in range(len(self.d_datahandle[0])):
            ss=[]
            for j in range(len(self.d_datahandle)):
                ss.append("{}".format(self.d_datahandle[j][i]))
            s.append(",".join(ss))
        s="\n".join(s)
        io.writeFile(fn, s)




