import numpy as np
from fvcomgrid import FVCOMGrid
import fvcomgrid
#from gribdata import GRIBData
import gribdata
import fvcomlibutil as u
import matplotlib.pyplot as plt
import matplotlib.tri as mtri
import matplotlib as mpl
import os
import math


VERBOSE = False
DEBUG = False
I_FG = 0
J_FG = 1

HALF = 0.5
NM = 1852
MinPerDeg = 60
GribCellWidthDeg = 0.2
SQRT2 = 1.41421356237


class FvcomGribMap:

    def __init__(self,fvcomGridX=None,gribDataX=None):
        self.WATERVECTORSCALE = 0.65
        self.WINDVECTORSCALE = 0.0425
        self.BEAUFORTSCALE = [0.0, 32.7]

        self.fgmap = np.zeros((0,0),int)
        self.maptype = None # "ele" or "node"
        self.entrycount = -1 # Number of FVCOM grid mapped nodes/elements
        self.fvcomgrid = fvcomGridX
        self.gribdata = gribDataX
        self.verbose = False
        self.GribCellWidthDeg = 0.2
        #
        self.T      = None # Time variable - Corresponds to GRIB.timesteps - USE MJD in stead.
        # GRIB measurement data - transmapped and interpolated.
        self.U10    = None # Transmapped data, can be overwritten. Original data are stored in the gribdata object.
        self.V10    = None # Transmapped data, can be overwritten. Original data are stored in the gribdata object.
        self.MSLP   = None
        self.DPT2   = None
        self.T2     = None
        self.CDR    = None
        self.CDRX   = None
        self.CBH    = None
        self.CP     = None
        self.LSP    = None
        self.LSPX   = None
        self.SP     = None
        self.TCC    = None
        self.VIS    = None
        self.TP     = None
        self.TPX    = None
        self.C1     = None
        self.C2     = None
        self.C3     = None
        self.MJD    = None
        # GRIB calculated data - transmapped and interpolated.
        self.WS     = None
        self.WD     = None
        self.WX     = None
        self.WY     = None
        # FVCOM GRID Element-Node (EN) data - data from elements mapped to closest node.
        self.WS_EN  = None

        #self.windPolar     = ForcingDataPolar # Dummy object
        #self.windUV        = ForcingDataCartesianUV # Dummy object
        #self.windCartesian = ForcingDataCartesian # Dummy object
        self.GaussLat = 62
        self.GaussNearN = 2
        self.GaussCorrectionFactor = SQRT2*SQRT2

        self.GaussSigma = (1* NM)


        # PLOTTING
        self.p_saveplot                 = True
        self.p_xinch_default            = 12
        self.p_xinch                    = self.p_xinch_default
        self.p_yinch_default            = 12
        self.p_yinch                    = self.p_yinch_default
        self.p_figure                   = None
        self.p_plt                      = None
        self.p_triangulation            = None
        self.p_colormap_default         = mpl.colormaps['jet']
        self.p_colormap                 = self.p_colormap_default # Cyclic: hsv. Progressive: jet. From: https://matplotlib.org/
                                             # stable/users/explain/colors/colormaps.html
                                             # plot_color_gradients('Cyclic', ['twilight', 'twilight_shifted', 'hsv'])
        self.p_colorbarlabel_default    = ""
        self.p_colorbarlabel= self.p_colorbarlabel_default
        self.p_vectorscale_default = 0.25
        self.p_vectorscale = self.p_vectorscale_default
        self.p_vectorxdelta_default = 3000
        self.p_vectorxdelta = self.p_vectorxdelta_default
        self.p_vectorydelta_default = 3000
        self.p_vectorydelta = self.p_vectorydelta_default
        self.p_bounds_default = None
        self.p_bounds = self.p_bounds_default
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
        # Default values etc...
        self.p_Reset() # Resets all plotting values back to default
        self.p_levels = [] # is overwritten during plotting, set nLevels, nTicks instead
        self.p_ticks  = [] # is overwritten during plotting, set nLevels, nTicks instead


        # Regular grid
        self.p_gm = int(0) # number of elements in x direction.
        self.p_gn  = 0 # number of elements in y direction.
        self.p_gx = np.zeros((0,0),dtype=float)
        self.p_gy = np.zeros((0,0),dtype=float) # array of int # gridpoints in regular grid.
        self.p_grid = np.zeros((0,0),dtype=int)  # array(n,m) of int   # index in irregular grid for currennt

    # def END
    #====================================================================================
    #
    #====================================================================================
    # buildMap
    def buildMap(self):
        self.buildElementMap()
    # def END
    #====================================================================================
    #
    #====================================================================================
    #====================================================================================
    # buildMapElement
    def buildElementMap(self):
        self.fgmap=np.zeros((self.fvcomgrid.cellcount, 2),dtype=int)
        #
        ilen=self.fvcomgrid.cellcount # disable if debug
        progStr = "Building element map {:4.0f}%"
        for i in range(ilen):
            # Calculate all d1-norms from current cellcenter (i), to all x and y in GRIB data:
            d1=u.d1norm(self.gribdata.x,self.gribdata.y,self.fvcomgrid.cellCenters[i,0],self.fvcomgrid.cellCenters[i,1])
            # Find index-set of smallest d1.
            (ibest, jbest) = np.unravel_index(np.argmin(d1, axis=None), d1.shape)
            if DEBUG:
                if (i<20):
                    print("ibest:{}     jbest: {}    d1.shape:{}".format(ibest,jbest,d1.shape))
            # Store the map
            self.fgmap[i,I_FG]=ibest
            self.fgmap[i,J_FG]=jbest

            if self.verbose:
                if (i < 10 or i > (ilen-10)  ):
                    print("{:5d}: GX[{}] GY[{}] (d={:8.1f}) F({:8.1f},{:8.1f}) <-> G({:8.1f},{:8.1f}) => ({:8.1f},{:8.1f})"
                        .format(i,ibest,jbest,d1[ibest,jbest], self.fvcomgrid.cellCenters[i,0],self.fvcomgrid.cellCenters[i,1],self.gribdata.x[ibest,jbest],self.gribdata.y[ibest,jbest],self.fvcomgrid.cellCenters[i,0]-self.gribdata.x[ibest,jbest],self.fvcomgrid.cellCenters[i,1]-self.gribdata.y[ibest,jbest]))


            u.prog(i,ilen-1,0.25,progStr)
            #if END
        #for END
        self.maptype="ele"
        self.entrycount=self.fvcomgrid.cellcount
        print("Mapping elements done.")
    # def END
    #====================================================================================
    #====================================================================================
    # buildMapElement
    def buildEleToNodeMap(self):
        print("Mapping element-nodes ...")
        jMax=9876543210
        self.enmap=np.multiply(jMax,np.ones((self.fvcomgrid.nodecount),dtype=int))
        jlen=self.fvcomgrid.cellcount # disable if debug
        progStr = "Building element-node map {:4.0f}%"
        for j in range(jlen):
            in0=self.fvcomgrid.cells[j,0]-1 # Indexes are 0-indexed
            in1=self.fvcomgrid.cells[j,1]-1 # Indexes are 0-indexed
            in2=self.fvcomgrid.cells[j,2]-1 # Indexes are 0-indexed
            self.enmap[in0]=min(self.enmap[in0],j+1) # Values are 1-indexed
            self.enmap[in1]=min(self.enmap[in1],j+1) # Values are 1-indexed
            self.enmap[in2]=min(self.enmap[in2],j+1) # Values are 1-indexed
            if DEBUG:
                if j<10:
                    print("cell{}:  {}  {}  {}".format(j+1,self.fvcomgrid.cells[j,0],self.fvcomgrid.cells[j,1],self.fvcomgrid.cells[j,2]))
                # if END
            #if END
            #
            # Print progress...
            u.prog(j,jlen-1,0.25,progStr)
        #for j END
        #
        iErrors = 0
        for i in range(self.fvcomgrid.nodecount):
            if (self.enmap[i]<0 or self.enmap[i]>self.fvcomgrid.cellcount):
                print("ERROR: Index of Element-Node (node:{}) outside cell count: {}.".format(i,self.enmap[i]))
                iErrors = iErrors + 1
            # if END
        # for i END

        if DEBUG:
            for i in range(10):
                print("Node {}: {}".format(i,self.enmap[i]))
            # for i END
        # if DEBUG END
        #
        print("Mapping element-node done. Errors: {}".format(iErrors))
        return
    # def END
#=============================================================================================================================
#
#=============================================================================================================================
#=============================================================================================================================
# buildMapNode
    def buildNodeMap(self):
        self.fgmap=np.zeros((self.fvcomgrid.nodecount, 2),dtype=int)
        #
        ilen=self.fvcomgrid.nodecount # disable if debug
        progStr = "Building node map {:4.0f}%"

        ##dxr=np.zeros((ilen,self.gribdata.x.shape[0],self.gribdata.x.shape[1]))
        for i in range(ilen):
            d1=u.d1norm(self.gribdata.x,self.gribdata.y,self.fvcomgrid.nodes[i,fvcomgrid.inX],self.fvcomgrid.nodes[i,fvcomgrid.inY])
            (ibest, jbest) = np.unravel_index(np.argmin(d1, axis=None), d1.shape)
            ##dx=d1
            ##dxr[i,:,:]=dx
            ###ix = np.argmin(dx)
            ##ibest0, jbest0 = ibest, jbest
            ##(ibest, jbest) = np.unravel_index(np.argmin(dx, axis=None), dx.shape)


            ##if (ibest==ibest0 and jbest==jbest0):
                ##print("WARNING - SAME INDEX: {}=={} and {}=={}".format(ibest,ibest0,jbest,jbest0))

            self.fgmap[i,I_FG]=ibest
            self.fgmap[i,J_FG]=jbest

            if self.verbose:
                if (i < 10 or i > (ilen-10)  ):
                    print("{:5d}: GX[{}] GY[{}] (d={:8.1f}) F({:8.1f},{:8.1f}) <-> G({:8.1f},{:8.1f}) => ({:8.1f},{:8.1f})"
                        .format(i,ibest,jbest,d1[ibest,jbest], self.fvcomgrid.nodes[i,0],self.fvcomgrid.nodes[i,1],self.gribdata.x[ibest,jbest],self.gribdata.y[ibest,jbest],self.fvcomgrid.nodes[i,0]-self.gribdata.x[ibest,jbest],self.fvcomgrid.nodes[i,1]-self.gribdata.y[ibest,jbest]))
                # if END
            #if END
            u.prog(i,ilen,0.25,progStr)
        #for END
        self.maptype="node"
        self.entrycount=self.fvcomgrid.nodecount
        print("Mapping nodes done.")
    # def END
#=============================================================================================================================
#
#=============================================================================================================================
#=============================================================================================================================
# calcWindCartesian
    def calcWindCartesian(self):
        #self.windCartesian = ForcingDataCartesian()
        #self.windCartesian.T = np.copy(self.windPolar.T)
        self.WX, self.WY= u.calcWindXY(self.WS,self.WD) # Calculates the X and Y values and transforms the NorthCW to
        #self.windCartesian.X=WX
        #self.windCartesian.Y=WY
        return self.WX, self.WY
    # def END
#=============================================================================================================================
#=============================================================================================================================
#
    def getEntryX(self, index):
        if (self.maptype == "ele"):
            return self.fvcomgrid.cellCenters[index,fvcomgrid.inX]
        else:
            return self.fvcomgrid.nodes[index,fvcomgrid.inX]
    # def END
#=============================================================================================================================
#
    def getEntryY(self, index):
        if (self.maptype == "ele"):
            return self.fvcomgrid.cellCenters[index,fvcomgrid.inY]
        else:
            return self.fvcomgrid.nodes[index,fvcomgrid.inY]
    # def END
#=============================================================================================================================
#==================================================================================================================================
#==================================================================================================================================
    def getField(self,fn):
        match fn:
            # Uncomment these lines if the commented fields are needed
            # case "timeBounds": return self.timeBounds
            # case "latBounds" : return self.latBounds
            # case "lonBounds" : return self.lonBounds
            # case "timesteps" : return self.timesteps
            # case "lat"       : return self.lat
            # case "lon"       : return self.lon
            # case "x"         : return self.x
            # case "y"         : return self.y
            case "mslp"      : return self.MSLP
            case "u10"       : return self.U10
            case "v10"       : return self.V10
            case "dpt2"      : return self.DPT2
            case "t2"        : return self.T2
            case "cdr"       : return self.CDR
            case "cdrx"      : return self.CDRX
            case "cbh"       : return self.CBH
            case "cp"        : return self.CP
            case "lsp"       : return self.LSP
            case "lspx"      : return self.LSPX
            case "sp"        : return self.SP
            case "tcc"       : return self.TCC
            case "vis"       : return self.VIS
            case "tp"        : return self.TP
            case "tpx"       : return self.TPX
            case "c1"        : return self.C1
            case "c2"        : return self.C2
            case "c3"        : return self.C3
            case "mjd"       : return self.MJD
            case "ws"        : return self.WS
            case "wd"        : return self.WD
            case "wx"        : return self.WX
            case "wy"        : return self.WY
            case "ws_en"     : return self.WS_EN
            case _           : return None


    # def END
#=============================================================================================================================
#==================================================================================================================================
#==================================================================================================================================
#
    def getFieldKind(self, fn):
        # Dictionary mapping field names to their respective unit attributes
        fieldKinds = {
            "mslp" : "node",
            "u10"  : "ele",
            "v10"  : "ele",
            "dpt2" : "node",
            "t2"   : "node",
            "cdr"  : "node",
            "cdrx" : "node",
            "cbh"  : "node",
            "cp"   : "node",
            "lsp"  : "node",
            "lspx" : "node",
            "sp"   : "node",
            "tcc"  : "node",
            "vis"  : "node",
            "tp"   : "node",
            "tpx"  : "node",
            "c1"   : "node",
            "c2"   : "node",
            "c3"   : "node",
            "mjd"  : "node",
            "ws"   : "ele",
            "wd"   : "ele",
            "wx"   : "ele",
            "wy"   : "ele",
            "ws_en" : "node"
        }
        return fieldKinds.get(fn, None)
    # def END
#=============================================================================================================================
#==================================================================================================================================
#==================================================================================================================================
#
    def getFieldPlotTitle(self, fn):
        # Dictionary mapping field names to their respective unit attributes
        fieldPCTitle = {
            "mslp" : "Mean surface level pressure (MSLP) (MJD={:.3f})",
            "u10"  : "U-Wind (U10) (MJD={:.3f})",
            "v10"  : "V-Wind (V10) (MJD={:.3f})",
            "dpt2" : "Dewpoint Temperature (DPT2) (MJD={:.3f})",
            "t2"   : "Air temperature (T2) (MJD={:.3f})",
            "cdr"  : "Clear-sky direct solar radiation (CDR) (MJD={:.3f})",
            "cdrx" : "Delta Clear-sky direct solar radiation (CDRX) (MJD={:.3f})",
            "cbh"  : "Cloud base height (CBH) (MJD={:.3f})",
            "cp"   : "(CP) (MJD={:.3f})",
            "lsp"  : "(LSP) (MJD={:.3f})",
            "lspx" : "(LSPX) (MJD={:.3f})",
            "sp"   : "(SP) (MJD={:.3f})",
            "tcc"  : "(TCC) (MJD={:.3f})",
            "vis"  : "(VIS) (MJD={:.3f})",
            "tp"   : "(TP) (MJD={:.3f})",
            "tpx"  : "(TPX) (MJD={:.3f})",
            "c1"   : "(C1) (MJD={:.3f})",
            "c2"   : "(C2) (MJD={:.3f})",
            "c3"   : "(C3) (MJD={:.3f})",
            "mjd"  : "(MJD) (MJD={:.3f})",
            "ws"   : "WindSpeed (WS) (MJD={:.3f})",
            "wd"   : "WindDirection (WD) (MJD={:.3f})",
            "wx"   : "X-Wind (WX) (MJD={:.3f})",
            "wy"   : "Y-Wind (WY) (MJD={:.3f})",
            "ws_en"  : "WindSpeed (WS (node)) (MJD={:.3f})",
        }
        return fieldPCTitle.get(fn, None)
    # def END
#=============================================================================================================================
#==================================================================================================================================
#==================================================================================================================================
#
    def getFieldPlotColorbarLabel(self, fn):
        # Dictionary mapping field names to their respective unit attributes
        fieldPCColorbarLabel = {
            "mslp" : "Mean surface level pressure (MSLP) ({})".format(self.gribdata.getFieldUnit(fn)),
            "u10"  : "U-Wind (U10) ({})".format(self.gribdata.getFieldUnit(fn)),
            "v10"  : "V-Wind (V10) ({})".format(self.gribdata.getFieldUnit(fn)),
            "dpt2" : "Dewpoint Temperature (DPT2)({})".format(self.gribdata.getFieldUnit(fn)),
            "t2"   : "Air temperature (T2) ({})".format(self.gribdata.getFieldUnit(fn)),
            "cdr"  : "Clear-sky direct solar radiation (CDR) ({})".format(self.gribdata.getFieldUnit(fn)),
            "cdrx" : "Delta Clear-sky direct solar radiation (CDRX) ({})".format(self.gribdata.getFieldUnit(fn)),
            "cbh"  : "Cloud base height (CBH) ({})".format(self.gribdata.getFieldUnit(fn)),
            "cp"   : "(CP) ({})".format(self.gribdata.getFieldUnit(fn)),
            "lsp"  : "(LSP) ({})".format(self.gribdata.getFieldUnit(fn)),
            "lspx" : "(LSPX) ({})".format(self.gribdata.getFieldUnit(fn)),
            "sp"   : "(SP) ({})".format(self.gribdata.getFieldUnit(fn)),
            "tcc"  : "(TCC) ({})".format(self.gribdata.getFieldUnit(fn)),
            "vis"  : "(VIS) ({})".format(self.gribdata.getFieldUnit(fn)),
            "tp"   : "(TP) ({})".format(self.gribdata.getFieldUnit(fn)),
            "tpx"  : "Precipitation (TPX) ({})".format(self.gribdata.getFieldUnit(fn)),
            "c1"   : "(C1) ({})".format(self.gribdata.getFieldUnit(fn)),
            "c2"   : "(C2) ({})".format(self.gribdata.getFieldUnit(fn)),
            "c3"   : "(C3) ({})".format(self.gribdata.getFieldUnit(fn)),
            "mjd"  : "(MJD) ({})".format(self.gribdata.getFieldUnit(fn)),
            "ws"   : "WindSpeed (WS) ({})".format(self.gribdata.getFieldUnit(fn)),
            "wd"   : "WindDirection (WD) ({})".format(self.gribdata.getFieldUnit(fn)),
            "wx"   : "X-Wind (WX) ({})".format(self.gribdata.getFieldUnit(fn)),
            "wy"   : "Y-Wind (WY) ({})".format(self.gribdata.getFieldUnit(fn)),
            "ws_en"   : "WindSpeed (WS (node)) ({})".format(self.gribdata.getFieldUnit(fn)),
        }
        return fieldPCColorbarLabel.get(fn, None)
    # def END
    #====================================================================================
    #====================================================================================
    def getMJDCount(self):
        return (self.gribdata.mjd.shape[0])
    # def END
    #====================================================================================
    #====================================================================================
    def plot(self,fn, timeIndex):
        plt=None
        tix=self.gribdata.mjd[timeIndex]

        if fn == "ws":
            plt=self.plotContour(self.WS,timeIndex,"ele","WindSpeed (MJD={:.3f})".format(tix),"Wind speed (m/s)")
        elif fn == "wd":
            tmp_cml = self.p_colormapbounds
            tmp_ntl = self.p_nTicks
            self.p_nTicks = 13
            self.p_colormapbounds = [0, 360]
            plt=self.plotContour(self.WD,timeIndex,"ele","WindDirection (MJD={:.3f})".format(tix),"Wind direction (deg)")
            self.p_colormapbounds = tmp_cml
            self.p_nTicks = tmp_ntl

        elif fn == "wx":
            plt=self.plotContour(self.getField(fn),timeIndex,self.getFieldKind(fn),self.getFieldPlotTitle(fn).format(tix),self.getFieldPlotColorbarLabel(fn))
        elif fn == "wy":
            plt=self.plotContour(self.getField(fn),timeIndex,self.getFieldKind(fn),self.getFieldPlotTitle(fn).format(tix),self.getFieldPlotColorbarLabel(fn))
        elif fn == "u10":
            plt=self.plotContour(self.getField(fn),timeIndex,self.getFieldKind(fn),self.getFieldPlotTitle(fn).format(tix),self.getFieldPlotColorbarLabel(fn))
        elif fn == "v10":
            plt=self.plotContour(self.getField(fn),timeIndex,self.getFieldKind(fn),self.getFieldPlotTitle(fn).format(tix),self.getFieldPlotColorbarLabel(fn))
        elif fn == "mslp":
            plt=self.plotContour(self.getField(fn),timeIndex,self.getFieldKind(fn),self.getFieldPlotTitle(fn).format(tix),self.getFieldPlotColorbarLabel(fn))
        elif fn == "t2":
            plt=self.plotContour(self.getField(fn),timeIndex,self.getFieldKind(fn),self.getFieldPlotTitle(fn).format(tix),self.getFieldPlotColorbarLabel(fn))
        elif fn == "cdr":
            plt=self.plotContour(self.getField(fn),timeIndex,self.getFieldKind(fn),self.getFieldPlotTitle(fn).format(tix),self.getFieldPlotColorbarLabel(fn))
        elif fn == "cdrx":
            plt=self.plotContour(self.CDRX,timeIndex,'node',"CDRX (MJD={:.3f})".format(tix),"Radiation (W/m2)")
        elif fn == "tp":
            plt=self.plotContour(self.TP,timeIndex,'node',"TP (MJD={:.3f})".format(tix),"Total precipitation (acc.) (m)")
        elif fn == "tpx":
            plt=self.plotContour(self.getField(fn),timeIndex,self.getFieldKind(fn),self.getFieldPlotTitle(fn).format(tix),self.getFieldPlotColorbarLabel(fn))
        elif fn == "c1":
            plt=self.plotContour(self.C1,timeIndex,'node',"C1 (MJD={:.3f})".format(tix),"C1 cloud cover (0-1)")
        elif fn == "c2":
            plt=self.plotContour(self.C2,timeIndex,'node',"C2 (MJD={:.3f})".format(tix),"C2 cloud cover (0-1)")
        elif fn == "c3":
            plt=self.plotContour(self.C3,timeIndex,'node',"C3 (MJD={:.3f})".format(tix),"C3 cloud cover (0-1)")
        elif fn == "ws_en":
            xx=self.getField(fn)
            #print(xx)
            xx=self.getFieldKind(fn)
            plt=self.plotContour(self.getField(fn),timeIndex,self.getFieldKind(fn),self.getFieldPlotTitle(fn).format(tix),self.getFieldPlotColorbarLabel(fn))



        if (plt != None):
            if VERBOSE:
                print("Saving image {} np. {} ...".format(fn,timeIndex))
            # if END
            os.system("mkdir -p img")
            if self.p_saveplot:
                self.saveplot("img/fvcomgribmap-{}-{:05d}.png".format(fn,timeIndex))
        # if END
        return plt
    # def END
    #====================================================================================
    #====================================================================================
    #
    #====================================================================================
    #====================================================================================
    def plotContour(self, field, timeIndex,pcontourkind = "ele",ptitle="Arb. measure at any time", pcolorbarlabel="Arbitrary measure (arb. unit)"):
        self.p_title=ptitle
        self.p_colorbarlabel=pcolorbarlabel

        #contourdata = self.windPolar.S[:,timeIndex]
        contourdata = field[:,timeIndex]
        blocking = False
        if (not blocking):
            mpl.use("Agg")
        # if END
        #
        if (not self.p_plt is None):
            self.p_plt.close()
        # if END
        self.p_plt=plt
        #
        fig = self.p_plt.figure()
        fig.set_size_inches(self.p_xinch, self.p_yinch)
        self.p_fig = fig
        ax = fig.add_subplot(1,1,1)
        self.p_ax = ax
        #===============COUNTOUR BEGIN====================================================================================
        # From : https://www.fabrizioguerrieri.com/blog/surface-graphs-with-irregular-dataset/
        x = self.fvcomgrid.nodes[:,0]
        y = self.fvcomgrid.nodes[:,1]
        xc=self.fvcomgrid.cellCenters[:,0]
        yc=self.fvcomgrid.cellCenters[:,1]
        nv = np.subtract(self.fvcomgrid.cells,1)
        if (self.p_triangulation == None):
            self.p_triangulation = mtri.Triangulation(x, y, nv) # Must have -1 here, since np arrays are 0-indexed.
        # triplot: https://matplotlib.org/stable/api/tri_api.html
        ax.triplot(self.p_triangulation, linewidth=0.5, c="#D3D3D3", markerfacecolor="#DC143C",markeredgecolor="black", markersize=10)
        ax.set_xlabel('X (m)')
        ax.set_ylabel('Y (m)')
        epsilon=1e-7
        #
        if (self.p_colormapbounds == []):
            pmin=np.min(field)
            pmax=np.max(field)
        else:
            pmin = self.p_colormapbounds[0]
            pmax = self.p_colormapbounds[1]
        # if END
        tpmin = pmin*(1-epsilon)
        tpmax = pmax*(1+epsilon)

        self.p_levels = np.linspace(tpmin,tpmax,self.p_nLevels)
        self.p_ticks = np.linspace(tpmin,tpmax,self.p_nTicks)

        # === PLOT CONTOUR ===
        if (pcontourkind == 'node'): # node
            # tricontourf : https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.tricontourf.html
            self.p_tripcolor = ax.tricontourf(self.p_triangulation, contourdata, vmin=tpmin, vmax=tpmax, levels=self.p_levels, cmap=self.p_colormap)
            # WORKS self.p_cbar = plt.colorbar(self.p_tripcolor, ticks=self.p_ticks, format='%.1f')
        # if END
        if (pcontourkind == 'ele'): # ele
            #print("Length of xtriang: {}, xc: {}, yc: {}, data:{}".format(len(self.p_triangulation.x),len(xc),len(yc),len(ws)))
            self.p_tripcolor = ax.tripcolor(self.p_triangulation, contourdata, vmin=tpmin, vmax=tpmax, cmap=self.p_colormap) # Hetta riggar
        # if END


        self.showColorbar()
        self.p_plt.title(self.p_title)
        self.p_figure=fig

        if (not blocking):
            plt.ion() #if non-blocking
        plt.draw()
        plt.subplots_adjust(left=0.06, right=0.96, top=0.95, bottom=0.05)
        plt.show()
        return plt
    # def END
#=============================================================================================================================
#
#=============================================================================================================================
#=============================================================================================================================
    # def END
    def plotVector(self,contourFieldName,xfieldName, yfieldName, timeIndex):
        xField = self.getField(xfieldName)
        yField = self.getField(yfieldName)
        cField = self.getField(contourFieldName)

        pcontourKind = self.getFieldKind(contourFieldName)
        #HERTIL....
        ptitle = self.getFieldPlotTitle(contourFieldName).format(self.gribdata.mjd[timeIndex])
        pcolorbarlabel = self.getFieldPlotColorbarLabel(contourFieldName)
        # Call plot, but do not save image yet
        tmp_bool = self.p_saveplot
        self.p_saveplot = False
        #plt = self.plotContour(cField,timeIndex,pcontourKind,ptitle,pcolorbarlabel)
        plt = self.plot(contourFieldName,timeIndex)
        self.p_saveplot = tmp_bool
        #
        #
        delta = 0.5 * (self.p_vectorxdelta + self.p_vectorydelta) # average of x and y-delta
        kk = self.p_vectorscale * delta
        self.p_bounds=[-60000,60000,-90000,70000]

        if ( len(self.p_gx) == 0):
            self.populateRegularGrid([self.p_bounds[0], self.p_bounds[1], self.p_vectorxdelta, self.p_bounds[2],self.p_bounds[3], self.p_vectorydelta])
        # if END
        self.p_xc = self.fvcomgrid.cellCenters[:,0]
        self.p_yc = self.fvcomgrid.cellCenters[:,1]
        for i in range(self.p_gm):
            for j in range(self.p_gn):
                #print("{}  {}      {}  {}        {}   {} ".format(i,j, self.p_xc[self.p_grid[i][j]], self.p_yc[self.p_grid[i][j]], xField[self.p_grid[i][j],timeIndex],  yField[self.p_grid[i][j],timeIndex]))
                plt.arrow(self.p_xc[self.p_grid[i][j]], self.p_yc[self.p_grid[i][j]],
                            kk*xField[self.p_grid[i][j],timeIndex], kk*yField[self.p_grid[i][j],timeIndex],
                            head_width = 500.2, width = 0.05, color = self.p_vectorcolor)
            # for END
        # for END
        if self.p_saveplot:
            self.saveplot("img/fvcomgribmap-{}-{}-{}-{:05d}.png".format(contourFieldName,xfieldName, yfieldName,timeIndex))




    #def END
#===============================================================================================================================
# populateRegularGrid
#  input:
# grid = [xmin, xmax, xdelta, ymin, ymax, ydelta]
    def populateRegularGrid(self, grid):

       # xc, yc # center of elements

        self.p_gxdim = [grid[0], grid[1], grid[2]] # xmin, xmax, xdelta  # (60000 - -60000) / 5000 +1 = 120.000 / 5.000 = 24 + 1 = 25
        self.p_gydim = [grid[3], grid[4], grid[5]] # ymin, ymax, ydelta


        self.p_gm = int( (self.p_gxdim[1]-self.p_gxdim[0])/self.p_gxdim[2] + 1 )
        self.p_gn = int( (self.p_gydim[1]-self.p_gydim[0])/self.p_gydim[2] + 1 )

        self.p_gx = np.zeros((self.p_gm,self.p_gn),dtype=float)
        self.p_gy = np.zeros((self.p_gn,self.p_gn),dtype=float)
        self.p_grid = np.zeros((self.p_gm,self.p_gn),dtype=int)

        # Build regular grid
        for i in range(self.p_gm):
            for j in range(self.p_gn):
                self.p_gx[i,j]=i*self.p_gxdim[2] + self.p_gxdim[0]
                self.p_gy[i,j]=j*self.p_gydim[2] + self.p_gydim[0]
                self.p_grid[i,j]=i*self.p_gm+j


        ##d2 = np.add(np.square(np.subtract(self.p_gx[i],self.xc),np.square(np.subtract(self.p_gy,s))))
        for i in range(self.p_gm):
            for j in range(self.p_gn):
                d2best = 1e24
                ibest = -1
                d2 = np.add( np.square(np.subtract(self.p_gx[i][j],self.fvcomgrid.cellCenters[:,0])) , np.square(np.subtract(self.p_gy[i][j],self.fvcomgrid.cellCenters[:,1])) )
                #print("shape of x-GRID: {}".format(d2.shape))
                ibest = np.argmin(d2)
                self.p_grid[i][j]=ibest
            ## for j end
        ## for i end
        return self.p_grid, self.p_gm, self.p_gn
    # def END
#=============================================================================================================================
#
    def propertyEleToNode(self,elefield):
        if (self.fvcomgrid.enMap == []):
            self.fvcomgrid.calcEleNodeMap()
        NF = np.zeros((self.fvcomgrid.nodecount, len(self.T)),dtype=float)
        for i in range(self.fvcomgrid.nodecount):
            print(i)
            for t in range(len(self.T)):
                k = self.fvcomgrid.enMap[i]
                NF[i,t]=elefield[k,t]
            # for END
        # for END
        return NF
    # def END

#=============================================================================================================================
#=============================================================================================================================
    def saveplot(self,fn):
        self.p_figure.savefig(fn)
        print("Saved figure to file: {}".format(fn))
    # def END
#=============================================================================================================================
#
#=============================================================================================================================
#=============================================================================================================================
#
# Transforms from 2D regular grid to 1D irregular grid
    def transmapWindPolar(self,method):
        if ( method == "simple" ):
            self.U10, self.V10, self.WS, self.WD, self.WX, self.WY = self.transmapWindPolarSimple()
        elif ( method == "1D" ):
            self.U10, self.V10, self.WS, self.WD, self.WX, self.WY = self.transmapWindPolar1D()
        elif ( method == "gauss" ):
            self.U10, self.V10, self.WS, self.WD, self.WX, self.WY = self.transmapWindPolarGauss()
        else:
            self.U10 = None
            self.V10 = None
            self.WS = None
            self.WD = None
            self.WX = None
            self.WY = None
        # if END
        #
        self.T   = np.copy(self.gribdata.timesteps)
        self.MJD = np.copy(self.gribdata.mjd)
        #self.windPolar=ForcingDataPolar()
        #self.windPolar.T=np.copy(self.gribdata.mjd)
        #self.windPolar.S=WS
        #self.windPolar.D=WD
        #self.windUV=ForcingDataCartesianUV()
        #self.windUV.T=np.copy(self.gribdata.mjd)
        #self.windUV.U=U10
        #self.windUV.V=V10
        #self.windXY=ForcingDataCartesian()
        #self.windXY.T=np.copy(self.gribdata.mjd)
        #self.windXY.X=WX
        #self.windXY.Y=WY


        return self.U10, self.V10, self.WS, self.WD, self.WX, self.WY
    # def END
#=============================================================================================================================
    def transmapWindPolarSimple(self):
        print("Transmapping SIMPLE from GRIB(u10,v10,ws,wd,wx,wy)[{},{},{}] to FVCOM(U10,V10,WS,WD,WX,WY)[{},{}] ...".format(self.gribdata.ws.shape[0],self.gribdata.ws.shape[1],self.gribdata.ws.shape[2], self.fvcomgrid.cellcount,self.gribdata.mjd.shape[0]))
        TN=self.gribdata.mjd.shape[0]
        #print(TN)
        #wfp=ForcingDataPolar()
        #
        U10 = np.zeros((self.entrycount,TN),float)
        V10 = np.zeros((self.entrycount,TN),float)
        S   = np.zeros((self.entrycount,TN),float)
        D   = np.zeros((self.entrycount,TN),float)
        X   = np.zeros((self.entrycount,TN),float)
        Y   = np.zeros((self.entrycount,TN),float)

        progStr = "Transmapping (U10,V10,WS,WD,WX,WY) {:3.0f}%"

        #
        for i in range(self.entrycount):
            for t in range(TN):
                gi=self.fgmap[i,I_FG]
                gj=self.fgmap[i,J_FG] # her stóð i_fg
                U10[i,t] = self.gribdata.u10[gi,gj,t]
                V10[i,t] = self.gribdata.v10[gi,gj,t]
                X[i,t]   = self.gribdata.wx[gi,gj,t]
                Y[i,t]   = self.gribdata.wy[gi,gj,t]
                S[i,t]   = self.gribdata.ws[gi,gj,t]
                D[i,t]   = self.gribdata.wd[gi,gj,t]

            # for END
            u.prog(i,self.entrycount-1,0.25,progStr)
        # for END
        #X, Y= u.calcWindXY(self.windPolar.S,self.windPolar.D)

        return U10, V10, S, D, X, Y
    # def END
#=============================================================================================================================
    def transmapWindPolar1D(self):
        minDist = 250.0 # m
        nearN = 1 # Nearest neightbors

        print("Transmapping 1D from GRIB(u10,v10,ws,wd,wx,wy)[{},{},{}] to FVCOM(U10,V10,WS,WD,WX,WY)[{},{}] ...".format(self.gribdata.ws.shape[0],self.gribdata.ws.shape[1],self.gribdata.ws.shape[2], self.fvcomgrid.cellcount,self.gribdata.mjd.shape[0]))
        TN=self.gribdata.mjd.shape[0]
        #wfp=ForcingDataPolar()
        #
        U10 = np.zeros((self.entrycount,TN),float)
        V10 = np.zeros((self.entrycount,TN),float)
        S  = np.zeros((self.entrycount,TN),float)
        D  = np.zeros((self.entrycount,TN),float)
        X   = np.zeros((self.entrycount,TN),float)
        Y   = np.zeros((self.entrycount,TN),float)

        #
        xinf=self.gribdata.x.shape[0]
        yinf=self.gribdata.x.shape[1]

        progStr = "Transmapping (U10,V10,WS,WD,WX,WY) {:3.0f}%"

        for i in range(self.entrycount):
            gi = self.fgmap[i,I_FG]
            gj = self.fgmap[i,J_FG] # her stóð i_fg
            xs = self.gribdata.x[ max(0,gi-nearN):min(xinf,gi+nearN+1), max(0,gj-nearN):min(yinf,gj+nearN+1) ]
            ys = self.gribdata.y[ max(0,gi-nearN):min(xinf,gi+nearN+1), max(0,gj-nearN):min(yinf,gj+nearN+1) ]
            x0 = self.getEntryX(i)
            y0 = self.getEntryY(i)
            d = u.d1norm(xs,ys,x0,y0)
            d = np.maximum(d,minDist)
            w = np.divide(1.0,np.square(d))
            wsum = np.sum(w)
            #
            for t in range(TN):
                u10vals = self.gribdata.u10[ max(0,gi-nearN):min(xinf,gi+nearN+1), max(0,gj-nearN):min(yinf,gj+nearN+1),t ]
                v10vals = self.gribdata.v10[ max(0,gi-nearN):min(xinf,gi+nearN+1), max(0,gj-nearN):min(yinf,gj+nearN+1),t ]
                wsvals = self.gribdata.ws[ max(0,gi-nearN):min(xinf,gi+nearN+1), max(0,gj-nearN):min(yinf,gj+nearN+1),t ]
                wdvals = self.gribdata.wd[ max(0,gi-nearN):min(xinf,gi+nearN+1), max(0,gj-nearN):min(yinf,gj+nearN+1),t ]
                wxvals = self.gribdata.wx[ max(0,gi-nearN):min(xinf,gi+nearN+1), max(0,gj-nearN):min(yinf,gj+nearN+1),t ]
                wyvals = self.gribdata.wy[ max(0,gi-nearN):min(xinf,gi+nearN+1), max(0,gj-nearN):min(yinf,gj+nearN+1),t ]
                u10 = np.sum(np.multiply(w, u10vals )) / wsum
                v10 = np.sum(np.multiply(w, v10vals )) / wsum
                ws  = np.sum(np.multiply(w, wsvals )) / wsum
                wd  = np.sum(np.multiply(w, wdvals )) / wsum
                wx  = np.sum(np.multiply(w, wxvals )) / wsum
                wy  = np.sum(np.multiply(w, wyvals )) / wsum
                U10[i,t] = u10
                V10[i,t] = v10
                S[i,t]   = ws
                D[i,t]   = wd
                WX[i,t]   = wx
                Y[i,t]   = wy

            # for END
            u.prog(i,self.entrycount-1,0.25,progStr)
            #X, Y= u.calcWindXY(self.windPolar.S,self.windPolar.D)
        # for END
        return U10, V10, S, D, X, Y
    # def END
#=============================================================================================================================
    def transmapWindPolarGauss(self):
        nearN = self.GaussNearN # Nearest neightbors
        sigmaCorrectionFactor = self.GaussCorrectionFactor
        cosLat = math.cos(self.GaussLat/180*math.pi)
        sigma = sigmaCorrectionFactor * cosLat * ( (HALF * self.GribCellWidthDeg * MinPerDeg) ) * self.GaussSigma  # sqrt(2) times [smallest halftwidth of cell]= 1.4142 * 5217 = 7378 m
        #sigma = 12000
        #sigma = 1000
        sigma2 = sigma**2
        print("Transmapping GAUSS from GRIB(u10,v10,ws,wd,wx,wy)[{},{},{}] to FVCOM(U10,V10,WS,WD,WX,WY)[{},{}] ...".format(self.gribdata.ws.shape[0],self.gribdata.ws.shape[1],self.gribdata.ws.shape[2], self.fvcomgrid.cellcount,self.gribdata.mjd.shape[0]))
        TN=self.gribdata.mjd.shape[0]
        #wfp=ForcingDataPolar()
        U10 = np.zeros((self.entrycount,TN),float)
        V10 = np.zeros((self.entrycount,TN),float)
        S  = np.zeros((self.entrycount,TN),float)
        D  = np.zeros((self.entrycount,TN),float)
        X   = np.zeros((self.entrycount,TN),float)
        Y   = np.zeros((self.entrycount,TN),float)

        #
        xinf=self.gribdata.x.shape[0]
        yinf=self.gribdata.x.shape[1]

        progStr = "Transmapping (U10,V10,WS,WD,WX,WY) {:3.0f}%"

        for i in range(self.entrycount):
            gi = self.fgmap[i,I_FG] # Mapping millum fvcom og grib
            gj = self.fgmap[i,J_FG] # Mapping millum fvcom og grib
            xs = self.gribdata.x[ max(0,gi-nearN):min(xinf,gi+nearN+1), max(0,gj-nearN):min(yinf,gj+nearN+1) ]
            ys = self.gribdata.y[ max(0,gi-nearN):min(xinf,gi+nearN+1), max(0,gj-nearN):min(yinf,gj+nearN+1) ]
            x0 = self.getEntryX(i)
            y0 = self.getEntryY(i)
            #d = u.d1norm(xs,ys,x0,y0)
            d2 = u.d2norm(xs,ys,x0,y0) # TODO Move this outside for optimization ...
            w  = np.exp(-d2/sigma2)
            wsum = np.sum(w)

            for t in range(TN):
                u10vals = self.gribdata.u10[ max(0,gi-nearN):min(xinf,gi+nearN+1), max(0,gj-nearN):min(yinf,gj+nearN+1),t ]
                v10vals = self.gribdata.v10[ max(0,gi-nearN):min(xinf,gi+nearN+1), max(0,gj-nearN):min(yinf,gj+nearN+1),t ]
                wsvals = self.gribdata.ws[ max(0,gi-nearN):min(xinf,gi+nearN+1), max(0,gj-nearN):min(yinf,gj+nearN+1),t ]
                wdvals = self.gribdata.wd[ max(0,gi-nearN):min(xinf,gi+nearN+1), max(0,gj-nearN):min(yinf,gj+nearN+1),t ]
                wxvals = self.gribdata.wx[ max(0,gi-nearN):min(xinf,gi+nearN+1), max(0,gj-nearN):min(yinf,gj+nearN+1),t ]
                wyvals = self.gribdata.wy[ max(0,gi-nearN):min(xinf,gi+nearN+1), max(0,gj-nearN):min(yinf,gj+nearN+1),t ]

                u10 = np.sum(np.multiply(w, u10vals )) / wsum
                v10 = np.sum(np.multiply(w, v10vals )) / wsum
                ws  = np.sum(np.multiply(w, wsvals )) / wsum
                wd  = np.sum(np.multiply(w, wdvals )) / wsum
                wx  = np.sum(np.multiply(w, wxvals )) / wsum
                wy  = np.sum(np.multiply(w, wyvals )) / wsum

                U10[i,t] = u10
                V10[i,t] = v10
                S[i,t]   = ws
                D[i,t]   = wd
                X[i,t]   = wx
                Y[i,t]   = wy

            # for END

            u.prog(i,self.entrycount-1,0.25,progStr)

        # for END
        return U10, V10, S, D, X, Y
    # def END
    #====================================================================================
    #====================================================================================
    #
    def transmapEleToNodeValues(self,fieldList):
        if ("ws" in fieldList):
            self.WS_EN = np.zeros((self.fvcomgrid.nodecount,self.getMJDCount()),float)
            progStr = "Element-Node ({}) transmapping".format(", ".join(fieldList).strip())+" {:4.0f}%"
            for i in range(self.fvcomgrid.nodecount):
                for t in range(self.getMJDCount()):
                    k=self.enmap[i]-1 # These values are 1-indexed, and must be 0-indexed
                    self.WS_EN[i,t]=self.WS[k,t]
                # for t END
                u.prog(i,self.fvcomgrid.nodecount-1,0.25,progStr)
            # for i END

        return self.WS_EN
    # def END

    #====================================================================================
    #====================================================================================
    #
    def transmapNodeValues(self,fieldList,method):
        if ( method == "1D" ):
            MSLP, T2, CDRX, TPX = self.transmap1D(fieldList)
        elif ( method == "simple" ):
            MSLP, T2, CDRX, TPX = self.transmapSimple(fieldList)
        elif ( method == "gauss" ):
            MSLP, T2, CDRX, TPX = self.transmapGauss(fieldList)
        else:
            print("ERROR: Invalid mapping method: [{}]. Exiting.".format(method))
            MSLP = None
            T2 = None
            CDRX = None
            TPX = None
        # if END
        #
        # Store values in self
        self.MSLP   = MSLP
        self.T2   = T2
        self.CDRX = CDRX
        self.TPX  = TPX

        return self.MSLP, self.T2, self.CDRX, self.TPX
    # def END

    #====================================================================================
    #=============================================================================================================================
    def transmapSimple(self,fields):
        print("Transmapping SIMPLE from GRIB(ws,wd)[{},{},{}] to FVCOM(WS,WD)[{},{}] ...".format(self.gribdata.ws.shape[0],self.gribdata.ws.shape[1],self.gribdata.ws.shape[2], self.fvcomgrid.cellcount,self.gribdata.mjd.shape[0]))
        TN=self.gribdata.mjd.shape[0]
        #
        # Local variable initialization
        MSLP = None
        T2   = None
        CDRX = None
        TPX  = None
        if "mslp" in fields: MSLP = np.zeros((self.entrycount,TN),float)
        if "t2"   in fields: T2   = np.zeros((self.entrycount,TN),float)
        if "cdrx" in fields: CDRX = np.zeros((self.entrycount,TN),float)
        if "tpx"  in fields: TPX  = np.zeros((self.entrycount,TN),float)
        #
        progStr = "Node ({}) transmapping".format(", ".join(fields).strip())+" {:4.0f}%"
        #
        for i in range(self.entrycount):
            for t in range(TN):
                gi=self.fgmap[i,I_FG]
                gj=self.fgmap[i,J_FG] # her stóð i_fg
                MSLP[i,t] = self.gribdata.mslp[gi,gj,t]
                T2[i,t]   = self.gribdata.t2[gi,gj,t]
                CDRX[i,t] = self.gribdata.cdrx[gi,gj,t]
                TPX[i,t]  = self.gribdata.tpx[gi,gj,t]
            # for END
            u.prog(i,self.entrycount-1,0.25,progStr)
        # for END
        return MSLP, T2, CDRX, TPX
    # def END
#=============================================================================================================================
#
#=============================================================================================================================
#=============================================================================================================================
    def transmap1D(self, fields):
        minDist = 250.0 # m
        nearN = 1 # Nearest neightbors

        print("Transmapping 1D from GRIB({})[{},{},{}] to FVCOM(WS,WD)[{},{}] ...".format(", ".join(fields),self.gribdata.ws.shape[0],self.gribdata.ws.shape[1],self.gribdata.ws.shape[2], self.fvcomgrid.cellcount,self.gribdata.mjd.shape[0]))
        TN=self.gribdata.mjd.shape[0]
        #
        # Local variable initialization
        MSLP = None
        T2   = None
        CDRX = None
        TPX  = None
        if "mslp" in fields: MSLP = np.zeros((self.entrycount,TN),float)
        if "t2"   in fields: T2   = np.zeros((self.entrycount,TN),float)
        if "cdrx" in fields: CDRX = np.zeros((self.entrycount,TN),float)
        if "tpx"  in fields: TPX  = np.zeros((self.entrycount,TN),float)
        #
        progStr = "Node ({}) transmapping {:4.0f}%".format(", ".join(fields).strip())
        #
        xinf=self.gribdata.x.shape[0]
        yinf=self.gribdata.x.shape[1]
        for i in range(self.entrycount): # For each node/element in FVCOM do: Find best matching element
            gi = self.fgmap[i,I_FG]
            gj = self.fgmap[i,J_FG] # her stóð i_fg
            xs = self.gribdata.x[ max(0,gi-nearN):min(xinf,gi+nearN+1), max(0,gj-nearN):min(yinf,gj+nearN+1) ]
            ys = self.gribdata.y[ max(0,gi-nearN):min(xinf,gi+nearN+1), max(0,gj-nearN):min(yinf,gj+nearN+1) ]
            x0 = self.getEntryX(i)
            y0 = self.getEntryY(i)
            d = u.d1norm(xs,ys,x0,y0)
            d = np.maximum(d,minDist)
            w = np.divide(1.0,np.square(d)) # Statistical weigth
            wsum = np.sum(w)                # Statistical weigth SUM / normalization value
            #
            for t in range(TN):
                vals  = self.gribdata.mslp[ max(0,gi-nearN):min(xinf,gi+nearN+1), max(0,gj-nearN):min(yinf,gj+nearN+1),t ]
                mslp  = np.sum(np.multiply(w,vals)) / wsum

                vals  = self.gribdata.t2[ max(0,gi-nearN):min(xinf,gi+nearN+1), max(0,gj-nearN):min(yinf,gj+nearN+1),t ]
                t2    = np.sum(np.multiply(w,vals)) / wsum

                vals  = self.gribdata.cdrx[ max(0,gi-nearN):min(xinf,gi+nearN+1), max(0,gj-nearN):min(yinf,gj+nearN+1),t ]
                cdrx  = np.sum(np.multiply(w,vals)) / wsum

                vals  = self.gribdata.tpx[ max(0,gi-nearN):min(xinf,gi+nearN+1), max(0,gj-nearN):min(yinf,gj+nearN+1),t ]
                tpx   = np.sum(np.multiply(w,vals)) / wsum

                MSLP[i,t] = mslp
                T2[i,t]   = t2
                CDRX[i,t] = cdrx
                TPX[i,t]  = tpx

            # for END
            #
            u.prog(i,self.entrycount-1,0.25,progStr)
            #if ( i % int(self.entrycount/10)  == 0 ): print("{:4.0f}%".format(int(100*i/self.fvcomgrid.cellcount)))
        # for END
        return MSLP, T2, CDRX, TPX
    # def END
#=============================================================================================================================
    def transmapGauss(self, fields):
        nearN = self.GaussNearN # Nearest neightbors
        sigmaCorrectionFactor = self.GaussCorrectionFactor
        cosLat = math.cos(self.GaussLat/180*math.pi)
        sigma = sigmaCorrectionFactor * cosLat * ( (HALF * self.GribCellWidthDeg * MinPerDeg) ) * self.GaussSigma  # sqrt(2) times= 7378 m
        #sigma = 12000
        #sigma = 1000
        sigma2 = sigma**2
        print("Transmapping Gaussian from GRIB({})[{},{},{}] to FVCOM[{},{}] ...".format(", ".join(fields),self.gribdata.ws.shape[0],self.gribdata.ws.shape[1],self.gribdata.ws.shape[2], self.fvcomgrid.cellcount,self.gribdata.mjd.shape[0]))
        TN=self.gribdata.mjd.shape[0]
        #
        #
        # Local variable initialization
        MSLP = None
        T2   = None
        CDRX = None
        TPX  = None
        if "mslp" in fields: MSLP = np.zeros((self.entrycount,TN),float)
        if "t2"   in fields: T2   = np.zeros((self.entrycount,TN),float)
        if "cdrx" in fields: CDRX = np.zeros((self.entrycount,TN),float)
        if "tpx"  in fields: TPX  = np.zeros((self.entrycount,TN),float)
        #
        progStr = "Node ({}) transmapping {{:4.0f}}%".format(", ".join(fields).strip())
        #
        xinf=self.gribdata.x.shape[0]
        yinf=self.gribdata.x.shape[1]

        for i in range(self.entrycount):
            gi = self.fgmap[i,I_FG] # Mapping millum fvcom og grib
            gj = self.fgmap[i,J_FG] # Mapping millum fvcom og grib
            xs = self.gribdata.x[ max(0,gi-nearN):min(xinf,gi+nearN+1), max(0,gj-nearN):min(yinf,gj+nearN+1) ]
            ys = self.gribdata.y[ max(0,gi-nearN):min(xinf,gi+nearN+1), max(0,gj-nearN):min(yinf,gj+nearN+1) ]
            x0 = self.getEntryX(i)
            y0 = self.getEntryY(i)
            #d = u.d1norm(xs,ys,x0,y0)
            d2 = u.d2norm(xs,ys,x0,y0) # TODO Move this outside for optimization ...
            w  = np.exp(-d2/sigma2) # Statistical weigth
            wsum = np.sum(w)        # Statistical weigth SUM / normalization value

            for t in range(TN):
                vals  = self.gribdata.mslp[ max(0,gi-nearN):min(xinf,gi+nearN+1), max(0,gj-nearN):min(yinf,gj+nearN+1),t ]
                mslp  = np.sum(np.multiply(w,vals)) / wsum

                vals  = self.gribdata.t2[ max(0,gi-nearN):min(xinf,gi+nearN+1), max(0,gj-nearN):min(yinf,gj+nearN+1),t ]
                t2    = np.sum(np.multiply(w,vals)) / wsum

                vals  = self.gribdata.cdrx[ max(0,gi-nearN):min(xinf,gi+nearN+1), max(0,gj-nearN):min(yinf,gj+nearN+1),t ]
                cdrx  = np.sum(np.multiply(w,vals)) / wsum

                vals  = self.gribdata.tpx[ max(0,gi-nearN):min(xinf,gi+nearN+1), max(0,gj-nearN):min(yinf,gj+nearN+1),t ]
                tpx   = np.sum(np.multiply(w,vals)) / wsum

                MSLP[i,t] = mslp
                T2[i,t]   = t2
                CDRX[i,t] = cdrx
                TPX[i,t]  = tpx
            # for END

            u.prog(i,self.entrycount-1,0.25,progStr)

        # for END
        return MSLP, T2, CDRX, TPX
    # def END
    #=============================================================================================================================
    #
    #=============================================================================================================================
    #=============================================================================================================================
    def showColorbar(self):
        #self.p_cbar = self.p_plt.colorbar(self.p_tripcolor, ticks=self.p_levels, format='%.4f')
        if ( (max(abs(self.p_ticks))>1000) or (max(abs(self.p_ticks))<0.001) ):
            p_colorbartickmask='%.3e'
        elif max(abs(self.p_ticks))<0.01 :
            p_colorbartickmask='%.4f'
        elif max(abs(self.p_ticks))<0.1 :
            p_colorbartickmask='%.3f'
        else :
            p_colorbartickmask='%.2f'
        #
        self.p_cbar = plt.colorbar(self.p_tripcolor, ticks=self.p_ticks, format=p_colorbartickmask, label = self.p_colorbarlabel)
        #self.p_cbar = self.p_plt.colorbar(self.p_tripcolor)
    # def END
    #=============================================================================================================================
    #
    #=============================================================================================================================
    #===================================================================================================================================
    def setVectorDelta(self, vxd, vyd):
        self.p_vectorxdelta = vxd
        self.p_vectorydelta = vyd
    # def END
    #=============================================================================================================================
    #=============================================================================================================================
    def setColormap(self, cm):
        self.p_colormap=mpl.colormaps[cm]
    #def END
    #=============================================================================================================================
    #=============================================================================================================================

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
#=============================================================================================================================
#=============================================================================================================================
#=============================================================================================================================
#=============================================================================================================================
class ForcingDataPolar():
    def __init__(self):
        self.T = np.zeros((),float) # Time series
        self.S = np.zeros((),float) # Magnitude of property, could be WS for WindSpeed
        self.D = np.zeros((),float) # Angle of property, could be WD for WindDirection
    # class END
#=============================================================================================================================
#
#=============================================================================================================================
#=============================================================================================================================
class ForcingDataCartesian():
    def __init__(self):
        self.T = np.zeros((),float) # Time series
        self.X = np.zeros((),float) # X of property, could be WX for WindSpeed
        self.Y = np.zeros((),float) # Y of property, could be WY for WindDirection
    # class END
#=============================================================================================================================
#
#=============================================================================================================================
#=============================================================================================================================
class ForcingDataCartesianUV():
    def __init__(self):
        self.T = np.zeros((),float) # Time series
        self.U = np.zeros((),float) # X of property, could be WX for WindSpeed
        self.V = np.zeros((),float) # Y of property, could be WY for WindDirection
    # class END
#=============================================================================================================================
#
#=============================================================================================================================
#=============================================================================================================================
