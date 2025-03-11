import numpy as np
import fvcomlibecmwf as ecmwf
import fvcomlibutil as u
from fvcomgribmap import FvcomGribMap, ForcingDataPolar, ForcingDataCartesian
import sys

TEPSILON = 1e-6
KELVIN = 273.15

class GRIBData:
    def __init__(self):
        self.timeBounds = [60000, 60010]
        self.timeBounds_unit = "MJD"
        self.latBounds  = [  0, 90]
        self.latBounds_unit = "deg"
        self.lonBounds  = [-45, 45]
        self.lonBounds_unit = "deg"
        self.timesteps  = np.zeros((0),dtype=float)
        self.timesteps_unit = "date"
        self.lat        = np.zeros((0,0),dtype=float) # Coordinate index order: lat,lon
        self.lat_unit   = "deg"
        self.lon        = np.zeros((0,0),dtype=float) # Coordinate index order: lat,lon
        self.lon_unit   = "deg"
        self.x          = np.zeros((0,0),dtype=float) # Coordinate index order: lat,lon
        self.x_unit     = "m"
        self.y          = np.zeros((0,0),dtype=float) # Coordinate index order: lat,lon
        self.y_unit     = "m"
        self.mslp       = np.zeros((0,0,0),dtype=float) # Mean sea level pressure, Pa
        self.mslp_unit  = "Pa"
        self.u10        = np.zeros((0,0,0),dtype=float) # 10 metre U wind component, m/s
        self.u10_unit   = "m/s"
        self.v10        = np.zeros((0,0,0),dtype=float) # 10 metre V wind component, m/s
        self.v10_unit   = "m/s"
        self.dpt2       = np.zeros((0,0,0),dtype=float) # 2 metre dewpoint temperature, °C/C (GRIB: K)
        self.dpt2_unit  = "°C"
        self.t2         = np.zeros((0,0,0),dtype=float) # 2 metre temperature, °C/C (GRIB: K)
        self.t2_unit    = "°C"
        self.cdr        = np.zeros((0,0,0),dtype=float)  # Clear-sky direct solar radiation at surface, J m**-2
        self.cdr_unit   = "J/m2"
        self.cdrx       = np.zeros((0,0,0),dtype=float) # Clear-sky direct solar radiation at surface, W m**-2
        self.cdrx_unit  = "W/m2"
        self.cbh        = np.zeros((0,0,0),dtype=float)  # Cloud base height
        self.cbh_unit   = "m"
        self.cp         = np.zeros((0,0,0),dtype=float)   # Convective precipitation, m
        self.cp_unit    = "m"
        self.lsp        = np.zeros((0,0,0),dtype=float)  # Large-scale precipitation, m
        self.lsp_unit   = "m"
        self.lspx       = np.zeros((0,0,0),dtype=float)  # DELTA Large-scale precipitation, m/s
        self.lspx_unit  = "m/s"
        self.sp         = np.zeros((0,0,0),dtype=float)   # Surface pressure, Pa
        self.sp_unit    = "Pa"
        self.tcc        = np.zeros((0,0,0),dtype=float)  # Total cloud cover, 0-1
        self.tcc_unit   = "0-1"
        self.vis        = np.zeros((0,0,0),dtype=float)  # Visibility, m
        self.vis_unit   = "m"
        self.tp         = np.zeros((0,0,0),dtype=float) # Total precipitation
        self.tp_unit    = "m"
        self.tpx        = np.zeros((0,0,0),dtype=float) # DELTA @ Total precipitation
        self.tpx_unit   = "m/s"
        self.c1         = np.zeros((0,0,0),dtype=float) # Low cloud cover, 0-1
        self.c1_unit    = "0-1"
        self.c2         = np.zeros((0,0,0),dtype=float) # Medium cloud cover, 0-1
        self.c2_unit    = "0-1"
        self.c3         = np.zeros((0,0,0),dtype=float) # High cloud cover, 0-1
        self.c3_unit    = "0-1"

        # Calculated values
        self.mjd        = np.zeros((0),dtype=float)
        self.mjd_unit   = "MJD"
        self.ws         = np.zeros((0,0,0),dtype=float) # 10 metre wind component speed, m/s
        self.ws_unit    = "m/s"
        self.wd         = np.zeros((0,0,0),dtype=float) # 10 metre wind angle
        self.wd_unit    = "deg"
        self.wx         = np.zeros((0,0,0),dtype=float) # Interpolated 10 metre U wind component, m/s
        self.wx_unit    = "m/s"
        self.wy         = np.zeros((0,0,0),dtype=float) # Interpolated 10 metre V wind component, m/s
        self.wy_unit    = "m/s"
        # Units

    #
    #======================================================================
    ##
    def loadData(self,time1, time2, lat1, lat2, lon1, lon2):
        #fromDateTime=u.MJD2datetime(T0)
        #toDateTime=u.MJD2datetime(T9)
        timeBounds = [time1, time2]
        latBounds  = [lat1, lat2]
        lonBounds  = [lon1, lon2]
        (self.timesteps,
         self.lat,
         self.lon,
         self.x,
         self.y,
         self.mslp, # Mean sea level pressure, Pa
         self.u10,  # 10 metre U wind component, m/s
         self.v10,  # 10 metre V wind component, m/s
         self.dpt2, # 2 metre dewpoint temperature, °C/C (GRIB: K)
         self.t2,   # 2 metre temperature, °C/C (GRIB: K)
         self.cdr,  # Clear-sky direct solar radiation at surface, J m**-2
         self.cdrx, # Clear-sky direct solar radiation at surface, W m**-2
         self.cbh,  # Cloud base height
         self.cp,   # Convective precipitation, m
         self.lsp,  # Large-scale precipitation, m
         self.lspx, # Large-scale precipitation, m/3h
         self.sp,   # Surface pressure, Pa
         self.tcc,  # Total cloud cover, 0-1
         self.vis,  # Visibility, m
         self.tp,   # Total precipitation, m H2O
         self.tpx,  # Precipitation, m/3h H20
         self.c1,   # Low cloud cover, 0-1
         self.c2,   # Medium cloud cover, 0-1
         self.c3    # High cloud cover, 0-1
         ) = ecmwf.get_ecmwf_FVCOMdata(time1, time2, lat1, lat2, lon1, lon2)
        #
        # Calculating MJD
        tmp_mjd = []
        print("Converting datetime to MJD ...")
        for i in range(len(self.timesteps)):
            tmp_mjd.append(u.datetime2MJD(self.timesteps[i]))
            print("{} -> {}".format(self.timesteps[i],tmp_mjd[i]))
        # for END
        self.mjd = np.array(tmp_mjd)
        #
        # Calculating WS and WD
        print("Calculating wind speed and direction ...")
        (self.ws, self.wd) = u.calcWindSpeedDirection(self.u10,self.v10)
        print("Calculating wind speed and direction ... Done")
        #
        # DPT2 Convert from Kelvin to Celsius
        if ((self.dpt2_unit=="C") or (self.dpt2_unit=="°C")):
            print("Converting DPT2 from Kelvin to Celsius ...")
            self.dpt2 = np.subtract(self.dpt2,KELVIN)
            print("Converting DPT2 from Kelvin to Celsius ... DONE")
        # if END
        #
        # T2 Convert from Kelvin to Celsius
        if ((self.t2_unit=="C") or (self.t2_unit=="°C")):
            print("Converting T2 from Kelvin to Celsius ...")
            self.t2 = np.subtract(self.t2,KELVIN)
            print("Converting T2 from Kelvin to Celsius ... DONE")
        # if END
        #
        # Converting CDRX from J/m2 (3h) to W/m2
        if (self.cdrx_unit=="W/m2"):
            print("Converting CDRX from J/m2 (3h) to W/m2 ...")
            self.cdrx=np.multiply(self.cdrx,1.0/(3.0*3600.0))
            print("Converting CDRX from J/m2 (3h) to W/m2 ... DONE.")
        #
        # Converting LSPX from m/3h to m/s
        if (self.tpx_unit=="m/s"):
            print("Converting LSPX from m/3h to m/s ...")
            self.tpx=np.multiply(self.tpx,1.0/(3.0*3600.0))
            print("Converting LSPX from m/3h to m/s ... DONE.")
        #
        # Converting TPX from m/3h to m/s
        if (self.tpx_unit=="m/s"):
            print("Converting TPX from m/3h to m/s ...")
            self.tpx=np.multiply(self.tpx,1.0/(3.0*3600.0))
            print("Converting TPX from m/3h to m/s ... DONE.")
        #


        self.printFieldSummary()
        #
        if False:
            t = min(self.u10.shape[2]-1,3)
            i = 10
            for j in range(20):
                print("WD ({:2d},{:2d}.{:2d}) u={:8.1f}  v={:8.1f}  v/u={:8.1f}  theta={:8.1f}  theta  ".format(i,j,t,self.u10[i,j,t],self.v10[i,j,t],self.v10[i,j,t]/self.u10[i,j,t],self.wd[i,j,t]))
            # for END
        # if END
        #sys.exit()
    # def END
    #
    #
    #======================================================================
    #
    def appendmjd(self, mjdval):
        self.mjd=np.append(self.mjd,mjdval)
    #
    #======================================================================
    #
    def appendwd(self, wdval):
        self.wd=np.dstack((self.wd,wdval))
    #
    #======================================================================
    #
    def appendws(self, wsval):
        self.ws=np.dstack((self.ws,wsval))
    #
    def appendEntry(self, entryArray,entryVal):
        return np.dstack((entryArray,entryVal))
    #
    #
    #======================================================================
    #
    #
    def calcWDmod360(self):
        self.wd = np.mod(self.wd,360.0)
    # def END
    #
    #======================================================================
    #
    def calcWindXY(self):
        self.wx, self.wy = u.calcWindXY(self.ws,self.wd)
    # def END

    #
    #======================================================================
    #  checkAppend(self,fieldList,endIndex,T9,TEXTRA)
    def checkAppend(self,endIndex,T9,TEXTRA):
        return self.checkAppendX([],endIndex,T9,TEXTRA)
    # def END
#
#======================================================================
#  checkAppend(self,fieldList,endIndex,T9,TEXTRA)
    def checkAppendX(self,fieldList,endIndex,T9,TEXTRA):

        print("Checking if additional time is needed...")
        if (self.mjd[endIndex] <= (T9+TEPSILON) ):
            # MJD
            self.appendmjd(T9+TEXTRA)
            #
            if "mslp" in fieldList or []==fieldList:
                field="mslp"
                print("BEFORE Shape of {} :  {}".format(field,self.mslp.shape))
                self.mslp=self.appendEntry(self.mslp,self.mslp[:,:,endIndex])
                print("AFTER  Shape of {} :  {}".format(field,self.mslp.shape))
            # if END
            if "u10" in fieldList or []==fieldList:
                field="u10"
                print("BEFORE Shape of {} :  {}".format(field,self.u10.shape))
                self.u10=self.appendEntry(self.u10,self.u10[:,:,endIndex])
                print("AFTER  Shape of {} :  {}".format(field,self.u10.shape))
            # if END
            if "v10" in fieldList or []==fieldList:
                field="v10"
                print("BEFORE Shape of {} :  {}".format(field,self.v10.shape))
                self.v10=self.appendEntry(self.v10,self.v10[:,:,endIndex])
                print("AFTER  Shape of {} :  {}".format(field,self.v10.shape))
            # if END
            if "dpt2" in fieldList or []==fieldList:
                field="dpt2"
                print("BEFORE Shape of {} :  {}".format(field,self.dpt2.shape))
                self.dpt2=self.appendEntry(self.dpt2,self.dpt2[:,:,endIndex])
                print("AFTER  Shape of {} :  {}".format(field,self.dpt2.shape))
            # if END
            if "t2" in fieldList or []==fieldList:
                field="t2"
                print("BEFORE Shape of {} :  {}".format(field,self.t2.shape))
                self.t2=self.appendEntry(self.t2,self.t2[:,:,endIndex])
                print("AFTER  Shape of {} :  {}".format(field,self.t2.shape))
            # if END
            if "cdr" in fieldList or []==fieldList:
                field="cdr"
                print("BEFORE Shape of {} :  {}".format(field,self.cdr.shape))
                self.cdr=self.appendEntry(self.cdr,self.cdr[:,:,endIndex])
                print("AFTER  Shape of {} :  {}".format(field,self.cdr.shape))
            # if END
            if "cdrx" in fieldList or []==fieldList:
                field="cdrx"
                print("BEFORE Shape of {} :  {}".format(field,self.cdrx.shape))
                self.cdrx=self.appendEntry(self.cdrx,self.cdrx[:,:,endIndex])
                print("AFTER  Shape of {} :  {}".format(field,self.cdrx.shape))
            # if END
            if "cbh" in fieldList or []==fieldList:
                field="cbh"
                print("BEFORE Shape of {} :  {}".format(field,self.cbh.shape))
                self.cbh=self.appendEntry(self.cbh,self.cbh[:,:,endIndex])
                print("AFTER  Shape of {} :  {}".format(field,self.cbh.shape))
            # if END

            if "cp" in fieldList or []==fieldList:
                field="cp"
                print("BEFORE Shape of {} :  {}".format(field,self.cp.shape))
                self.cp=self.appendEntry(self.cp,self.cp[:,:,endIndex])
                print("AFTER  Shape of {} :  {}".format(field,self.cp.shape))
            # if END
            if "lsp" in fieldList or []==fieldList:
                field="lsp"
                print("BEFORE Shape of {} :  {}".format(field,self.lsp.shape))
                self.lsp=self.appendEntry(self.lsp,self.lsp[:,:,endIndex])
                print("AFTER  Shape of {} :  {}".format(field,self.lsp.shape))
            # if END
            if "lspx" in fieldList or []==fieldList:
                field="lspx"
                print("BEFORE Shape of {} :  {}".format(field,self.lspx.shape))
                self.lspx=self.appendEntry(self.lspx,self.lspx[:,:,endIndex])
                print("AFTER  Shape of {} :  {}".format(field,self.lspx.shape))
            # if END
            if "sp" in fieldList or []==fieldList:
                field="sp"
                print("BEFORE Shape of {} :  {}".format(field,self.sp.shape))
                self.sp=self.appendEntry(self.sp,self.sp[:,:,endIndex])
                print("AFTER  Shape of {} :  {}".format(field,self.sp.shape))
            # if END
            if "tcc" in fieldList or []==fieldList:
                field="tcc"
                print("BEFORE Shape of {} :  {}".format(field,self.tcc.shape))
                self.tcc=self.appendEntry(self.tcc,self.tcc[:,:,endIndex])
                print("AFTER  Shape of {} :  {}".format(field,self.tcc.shape))
            # if END
            if "vis" in fieldList or []==fieldList:
                field="vis"
                print("BEFORE Shape of {} :  {}".format(field,self.vis.shape))
                self.vis=self.appendEntry(self.vis,self.vis[:,:,endIndex])
                print("AFTER  Shape of {} :  {}".format(field,self.vis.shape))
            # if END
            if "tp" in fieldList or []==fieldList:
                field="tp"
                print("BEFORE Shape of {} :  {}".format(field,self.tp.shape))
                self.tp=self.appendEntry(self.tp,self.tp[:,:,endIndex])
                print("AFTER  Shape of {} :  {}".format(field,self.tp.shape))
            # if END
            if "tpx" in fieldList or []==fieldList:
                field="tpx"
                print("BEFORE Shape of {} :  {}".format(field,self.tpx.shape))
                self.tpx=self.appendEntry(self.tpx,self.tpx[:,:,endIndex])
                print("AFTER  Shape of {} :  {}".format(field,self.tpx.shape))
            # if END
            if "c1" in fieldList or []==fieldList:
                field="c1"
                print("BEFORE Shape of {} :  {}".format(field,self.c1.shape))
                self.c1=self.appendEntry(self.c1,self.c1[:,:,endIndex])
                print("AFTER  Shape of {} :  {}".format(field,self.c1.shape))
            # if END
            if "c2" in fieldList or []==fieldList:
                field="c2"
                print("BEFORE Shape of {} :  {}".format(field,self.c2.shape))
                self.c2=self.appendEntry(self.c2,self.c2[:,:,endIndex])
                print("AFTER  Shape of {} :  {}".format(field,self.c2.shape))
            # if END
            if "c3" in fieldList or []==fieldList:
                field="c3"
                print("BEFORE Shape of {} :  {}".format(field,self.c3.shape))
                self.c3=self.appendEntry(self.c3,self.c3[:,:,endIndex])
                print("AFTER  Shape of {} :  {}".format(field,self.c3.shape))
            # if END
            #
            # Conversion fields - Calculated: WS, WD, (WX, WY)
            if "ws" in fieldList or []==fieldList:
                field = "ws"
                print("BEFORE Shape of {} :  {}".format(field,self.ws.shape))
                self.ws=self.appendEntry(self.ws,self.ws[:,:,endIndex])
                print("AFTER  Shape of {} :  {}".format(field,self.ws.shape))
            # if END
            if "wd" in fieldList or []==fieldList:
                field="wd"
                print("BEFORE Shape of {} :  {}".format(field,self.wd.shape))
                self.wd=self.appendEntry(self.wd,self.wd[:,:,endIndex])
                print("AFTER  Shape of {} :  {}".format(field,self.wd.shape))
            # if END
            print("Added new end record {} with MJD: {}.".format(fieldList,self.mjd[endIndex]))
            print("Extra End MJD:   {}".format(self.mjd[endIndex]))
            endIndex = endIndex + 1
        # if END
        return endIndex
    # def END
    #
    #
    #======================================================================
    #
    def  createRamps(self,fieldList,timestepsperday,kind="polar"):
        mjdl = [] # Time Series List
        #
        u10l   = [] # U-Wind
        v10l   = [] # V-Wind
        mslpl = [] # Mean sea level pressure List
        dpt2l = [] # # 2 metre dewpoint temperature, °C/C (GRIB: K)
        t2l   = [] # 2 metre temperature, °C/C (GRIB: K)
        cdrl  = [] # Temperature List
        cdrxl = [] # Temperature List
        cbhl   = []
        cpl   = []
        lspl   = []
        lspxl   = []
        spl   = []
        tccl   = []
        visl   = []
        tpl   = [] # Temperature List
        tpxl  = [] # Temperature List
        c1l   = []
        c2l   = []
        c3l   = []


        wsl = [] # Wind Speed List
        wdl = [] # Wind Direction List
        wsx = []
        wsy = []



        #
        # Creating ramps
        print("Creating ramps ...")
        for i in range(self.getMJDLen()-1):
            # STEPS
            nsteps = max(1,int(round((self.mjd[i+1] - self.mjd[i])*timestepsperday,0))) # Since MJD is in units of days, and we want
            npoints=nsteps+1
            print("From {:9.3f} to {:9.3f} in {} steps (d={:5.4f})".format(self.mjd[i],self.mjd[i+1],nsteps,(self.mjd[i+1]-self.mjd[i])/nsteps ))
            #
            # TIME
            tmp_mjd = u.ramp1D(self.mjd[i],self.mjd[i+1],npoints)
            mjdl.append(tmp_mjd)
            #
            #
            # MSLP
            if "mslp" in fieldList or []==fieldList:
                tmp_mslp = u.ramp3D(self.mslp[:,:,i],self.mslp[:,:,i+1],npoints)
                mslpl.append(tmp_mslp)
                #print("mslp")
            # U10
            if "u10" in fieldList or []==fieldList:
                tmp_u10 = u.ramp3D(self.u10[:,:,i],self.u10[:,:,i+1],npoints)
                u10l.append(tmp_u10)
                #print("u10")
            # V-Wind Speed
            if "v10" in fieldList or []==fieldList:
                tmp_v10 = u.ramp3D(self.v10[:,:,i],self.v10[:,:,i+1],npoints)
                v10l.append(tmp_v10)
            # DPT2
            if "dpt2" in fieldList or []==fieldList:
                #print("DPT2: {}".format(self.dpt2.shape))
                tmp_dpt2 = u.ramp3D(self.dpt2[:,:,i],self.dpt2[:,:,i+1],npoints)
                dpt2l.append(tmp_dpt2)
            # T2
            if "t2" in fieldList or []==fieldList:
                #print("T2: {}".format(self.t2.shape))
                tmp_t2 = u.ramp3D(self.t2[:,:,i],self.t2[:,:,i+1],npoints)
                t2l.append(tmp_t2)
                #print("t2 {}".format(len(t2l)))
            # CDR
            if "cdr" in fieldList or []==fieldList:
                tmp_cdr = u.ramp3D(self.cdr[:,:,i],self.cdr[:,:,i+1],npoints)
                cdrl.append(tmp_cdr)
            # CDRX
            if "cdrx" in fieldList or []==fieldList:
                tmp_cdrx = u.ramp3D(self.cdrx[:,:,i],self.cdrx[:,:,i+1],npoints)
                cdrxl.append(tmp_cdrx)
            # CBH
            if "cbh" in fieldList or []==fieldList:
                #print("CBH: {}".format(self.cbh.shape))
                tmp_cbh = u.ramp3D(self.cbh[:,:,i],self.cbh[:,:,i+1],npoints)
                cbhl.append(tmp_cbh)
                #print("...")
            # CP
            if "cp" in fieldList or []==fieldList:
                tmp_cp = u.ramp3D(self.cp[:,:,i],self.cp[:,:,i+1],npoints)
                cpl.append(tmp_cp)
            # LSP
            if "lsp" in fieldList or []==fieldList:
                tmp_lsp = u.ramp3D(self.lsp[:,:,i],self.lsp[:,:,i+1],npoints)
                lspl.append(tmp_lsp)
            # LSPX
            if "lspx" in fieldList or []==fieldList:
                tmp_lspx = u.ramp3D(self.lspx[:,:,i],self.lspx[:,:,i+1],npoints)
                lspxl.append(tmp_lspx)
            # SP
            if "sp" in fieldList or []==fieldList:
                tmp_sp = u.ramp3D(self.sp[:,:,i],self.sp[:,:,i+1],npoints)
                spl.append(tmp_sp)
            # TCC
            if "tcc" in fieldList or []==fieldList:
                tmp_tcc = u.ramp3D(self.tcc[:,:,i],self.tcc[:,:,i+1],npoints)
                tccl.append(tmp_tcc)
            # VIS
            if "vis" in fieldList or []==fieldList:
                tmp_vis = u.ramp3D(self.vis[:,:,i],self.vis[:,:,i+1],npoints)
                visl.append(tmp_vis)
            # TP
            if "tp" in fieldList or []==fieldList:
                tmp_tp = u.ramp3D(self.tp[:,:,i],self.tp[:,:,i+1],npoints)
                tpl.append(tmp_tp)
            # TPX
            if "tpx" in fieldList or []==fieldList:
                tmp_tpx = u.ramp3D(self.tpx[:,:,i],self.tpx[:,:,i+1],npoints)
                tpxl.append(tmp_tpx)
            # C1
            if "c1" in fieldList or []==fieldList:
                tmp_c1 = u.ramp3D(self.c1[:,:,i],self.c1[:,:,i+1],npoints)
                c1l.append(tmp_c1)
            # C2
            if "c2" in fieldList or []==fieldList:
                tmp_c2 = u.ramp3D(self.c2[:,:,i],self.c2[:,:,i+1],npoints)
                c2l.append(tmp_c2)
            # C3
            if "c3" in fieldList or []==fieldList:
                tmp_c3 = u.ramp3D(self.c3[:,:,i],self.c3[:,:,i+1],npoints)
                c3l.append(tmp_c3)


            #
            # Wind Speed
            if "ws" in fieldList or []==fieldList:
                tmp_ws = u.ramp3D(self.ws[:,:,i],self.ws[:,:,i+1],npoints)
                wsl.append(tmp_ws)
            #
            # Wind Direction
            if "wd" in fieldList or []==fieldList:
                tmp_wd = u.ramp3D(self.wd[:,:,i],self.wd[:,:,i+1],npoints)
                wdl.append(tmp_wd)
            #


        # for END
        #
        # === Converting to NumPy
        print("Creating new GRIBData object ...")

        gdr = GRIBData() # GRIB data format with Ramp data
        gdr.lat = np.copy(self.lat)
        gdr.lon = np.copy(self.lon)
        gdr.x = np.copy(self.x)
        gdr.y = np.copy(self.y)
        #
        # Time
        gdr.mjd = u.ramps1DJoin(mjdl) # Calculated
        #
        if "mslp" in fieldList or []==fieldList:
            gdr.mslp = u.ramps3DJoin(mslpl)
        #if END
        #
        if "u10" in fieldList or []==fieldList:
            gdr.u10 = u.ramps3DJoin(u10l)
        # if END
        #
        if "v10" in fieldList or []==fieldList:
            gdr.v10 = u.ramps3DJoin(v10l)
        # if END
        #
        if "dpt2" in fieldList or []==fieldList:
            gdr.dpt2 = u.ramps3DJoin(dpt2l)
        # if END
        #
        if "t2" in fieldList or []==fieldList:
            gdr.t2 = u.ramps3DJoin(t2l)
        # if END
        #
        if "cdr" in fieldList or []==fieldList:
            gdr.cdr = u.ramps3DJoin(cdrl)
        # if END
        #
        if "cdrx" in fieldList or []==fieldList:
            gdr.cdrx = u.ramps3DJoin(cdrxl)
        # if END
        #
        if "chb" in fieldList or []==fieldList:
            gdr.cbh = u.ramps3DJoin(cbhl)
        # if END
        #
        if "cp" in fieldList or []==fieldList:
            gdr.cp = u.ramps3DJoin(cpl)
        # if END
        #
        if "lsp" in fieldList or []==fieldList:
            gdr.lsp = u.ramps3DJoin(lspl)
        # if END
        #
        if "lspx" in fieldList or []==fieldList:
            gdr.lspx = u.ramps3DJoin(lspxl)
        # if END
        #
        if "sp" in fieldList or []==fieldList:
            gdr.sp = u.ramps3DJoin(spl)
        # if END
        #
        if "tcc" in fieldList or []==fieldList:
            gdr.tcc = u.ramps3DJoin(tccl)
        # if END
        #
        if "vis" in fieldList or []==fieldList:
            gdr.vis = u.ramps3DJoin(visl)
        # if END
        #
        if "tp" in fieldList or []==fieldList:
            gdr.tp = u.ramps3DJoin(tpl)
        # if END
        #
        if "tpx" in fieldList or []==fieldList:
            gdr.tpx = u.ramps3DJoin(tpxl)
        # if END
        #
        if "c1" in fieldList or []==fieldList:
            gdr.c1 = u.ramps3DJoin(c1l)
        # if END
        #
        if "c2" in fieldList or []==fieldList:
            gdr.c2 = u.ramps3DJoin(c2l)
        # if END
        #
        if "c3" in fieldList or []==fieldList:
            gdr.c3 = u.ramps3DJoin(c3l)
        # if END
        #
        if (kind == "polar"):
            gdr.ws = u.ramps3DJoin(wsl)
            gdr.wd = u.ramps3DJoin(wdl)
        else :
            gdr.wx = u.ramps3DJoin(wxl)
            gdr.wy = u.ramps3DJoin(wyl)
        # if END
        #

        return gdr
    #
    #======================================================================
    #
    def exportForcingData(self, stepStart, stepEnd):
        gdx = GRIBData()
        #gdx.timeBounds  = self.timeBounds
        gdx.latBounds   = np.copy(self.latBounds)
        gdx.lonBounds   = np.copy(self.lonBounds)
        gdx.timesteps   = np.copy(self.timeBounds)
        gdx.mjd         = np.copy(self.mjd)
        gdx.lat         = np.copy(self.lat)
        gdx.lon         = np.copy(self.lon)
        gdx.x           = np.copy(self.x)
        gdx.y           = np.copy(self.y)
        gdx.mslp        = self.mslp[:,:,stepStart:stepEnd+1]
        gdx.u10         = self.u10[:,:,stepStart:stepEnd+1]
        gdx.v10         = self.v10[:,:,stepStart:stepEnd+1]
        gdx.dpt2        = self.dpt2[:,:,stepStart:stepEnd+1]
        gdx.t2          = self.t2[:,:,stepStart:stepEnd+1]
        gdx.cdr         = self.cdr[:,:,stepStart:stepEnd+1]
        gdx.cdrx        = self.cdrx[:,:,stepStart:stepEnd+1]
        gdx.cbh         = self.cbh[:,:,stepStart:stepEnd+1]
        gdx.cp          = self.cp[:,:,stepStart:stepEnd+1]
        gdx.lsp         = self.lsp[:,:,stepStart:stepEnd+1]
        gdx.lspx        = self.lspx[:,:,stepStart:stepEnd+1]
        gdx.sp          = self.sp[:,:,stepStart:stepEnd+1]
        gdx.tcc         = self.tcc[:,:,stepStart:stepEnd+1]
        gdx.vis         = self.vis[:,:,stepStart:stepEnd+1]
        gdx.tp          = self.tp[:,:,stepStart:stepEnd+1]
        gdx.tpx         = self.tpx[:,:,stepStart:stepEnd+1]
        gdx.c1          = self.c1[:,:,stepStart:stepEnd+1]
        gdx.c2          = self.c2[:,:,stepStart:stepEnd+1]
        gdx.c3          = self.c3[:,:,stepStart:stepEnd+1]
        #Calculated
        gdx.mjd         = self.mjd[stepStart:stepEnd+1]
        gdx.ws          = self.ws[:,:,stepStart:stepEnd+1]
        gdx.wd          = self.wd[:,:,stepStart:stepEnd+1]
        return gdx
    #
    #======================================================================
    #  findLastTimeStep(self,startIndex,T9):
    def findLastTimeStep(self,startIndex,T9):
        i = startIndex
        endIndex = 0
        while (i < len(self.mjd) ):

            if (self.mjd[i] < (T9+TEPSILON)):
                endIndex = i
                print("New end value found: {}".format(self.mjd[endIndex]))

            if (self.mjd[i] > (T9+TEPSILON) and self.mjd[i-1] <= (T9+TEPSILON)):
                print("Best value found: {}".format(self.mjd[endIndex]))
                break
            i = i +1
        # END while (i < len(self.mjd) ):
        print("End MJD:   {}".format(self.mjd[endIndex]))
        return endIndex
    # def END
#
#==================================================================================================================================
#==================================================================================================================================
#
    def getField(self, fn):
        # Dictionary mapping field names to their respective unit attributes
        fields = {
            "timeBounds"    : self.timeBounds,
            "latBounds"     : self.latBounds,
            "lonBounds"     : self.lonBounds,
            "timesteps"     : self.timesteps,
            "lat"           : self.lat,
            "lon"           : self.lon,
            "x"             : self.x,
            "y"             : self.y,
            "mslp"          : self.mslp,
            "u10"           : self.u10,
            "v10"           : self.v10,
            "dpt2"          : self.dpt2,
            "t2"            : self.t2,
            "cdr"           : self.cdr,
            "cdrx"          : self.cdrx,
            "cbh"           : self.cbh,
            "cp"            : self.cp,
            "lsp"           : self.lsp,
            "lspx"          : self.lspx,
            "sp"            : self.sp,
            "tcc"           : self.tcc,
            "vis"           : self.vis,
            "tp"            : self.tp,
            "tpx"           : self.tpx,
            "c1"            : self.c1,
            "c2"            : self.c2,
            "c3"            : self.c3,
            "mjd"           : self.mjd,
            "ws"            : self.ws,
            "wd"            : self.wd,
            "wx"            : self.wx,
            "wy"            : self.wy
        }
        return fields.get(fn, None)
    # def END
#==================================================================================================================================
#==================================================================================================================================
#
    def getFieldUnit(self, fn):
        # Dictionary mapping field names to their respective unit attributes
        field_units = {
            "timeBounds": self.timeBounds_unit,
            "latBounds": self.latBounds_unit,
            "lonBounds": self.lonBounds_unit,
            "timesteps": self.timesteps_unit,
            "lat": self.lat_unit,
            "lon": self.lon_unit,
            "x": self.x_unit,
            "y": self.y_unit,
            "mslp": self.mslp_unit,
            "u10": self.u10_unit,
            "v10": self.v10_unit,
            "dpt2": self.dpt2_unit,
            "t2": self.t2_unit,
            "cdr": self.cdr_unit,
            "cdrx": self.cdrx_unit,
            "cbh": self.cbh_unit,
            "cp": self.cp_unit,
            "lsp": self.lsp_unit,
            "lspx": self.lspx_unit,
            "sp": self.sp_unit,
            "tcc": self.tcc_unit,
            "vis": self.vis_unit,
            "tp": self.tp_unit,
            "tpx": self.tpx_unit,
            "c1": self.c1_unit,
            "c2": self.c2_unit,
            "c3": self.c3_unit,
            "mjd": self.mjd_unit,
            "ws": self.ws_unit,
            "wd": self.wd_unit,
            "wx": self.wx_unit,
            "wy": self.wy_unit
        }
        return field_units.get(fn, None)
    # def END
#
#==================================================================================================================================
#==================================================================================================================================
#

    def getMJDLen(self):
        return len(self.mjd)
    # def END
#
#==================================================================================================================================
#==================================================================================================================================
#

    def getTimestepsLen(self):
        return len(self.timesteps)
    # def END
#
#==================================================================================================================================
#==================================================================================================================================
#

    def getILen(self):
        return self.lat.shape(1)
    # def END
#
#==================================================================================================================================
#==================================================================================================================================
#

    def getJLen(self):
        return self.lat.shape(1)
    # def END
#
#==================================================================================================================================
#==================================================================================================================================
#
    def printExample_ws_ws_u10_v10(self,dataname):
        m = 20
        n = 20
        print("Example of data : ")
        for i in range(self.getMJDLen()-1):
            print("{}[{}] ws:{:8.4f}  wd:{:8.4f}  u10:{:8.4f}  v10:{:8.4f} ".format(dataname,i,self.ws[m,n,i],self.wd[m,n,i],self.u10[m,n,i],self.v10[m,n,i]))
        # for END
    #def END
#
#
    def prFIf(self,fn):
        field = self.getField(fn)
        if field.size>0:
            return "{:4s} MAX : {:10.2f} {:4s}     {:4s} MIN  : {:10.2f} {:4s}   [{},{},{}]".format(fn.upper(), field.max(), self.getFieldUnit(fn), fn.upper(), field.min(), self.getFieldUnit(fn), field.shape[0], field.shape[1], field.shape[2])
        else:
            return "{:4s} MAX : {:10.2f} {:4s}     {:4s} MIN  : {:10.2f} {:4s}   [{},{},{}]".format(fn.upper(), np.nan, self.getFieldUnit(fn), fn.upper(), np.nan, self.getFieldUnit(fn), field.shape[0], field.shape[1], field.shape[2])


    def prFIe(self,fn):
        field = self.getField(fn)
        if field.size>0:
            return "{:4s} MAX : {:10.2e} {:4s}     {:4s} MIN  : {:10.2e} {:4s}   [{},{},{}]".format(fn.upper(), field.max(), self.getFieldUnit(fn), fn.upper(), field.min(), self.getFieldUnit(fn), field.shape[0], field.shape[1], field.shape[2])
        else:
            return "{:4s} MAX : {:10.2e} {:4s}     {:4s} MIN  : {:10.2e} {:4s}   [{},{},{}]".format(fn.upper(), np.nan, self.getFieldUnit(fn), fn.upper(), np.nan, self.getFieldUnit(fn), field.shape[0], field.shape[1], field.shape[2])

#
    def printFieldSummary(self):
        print("U10 shape: {}      V10 shape: {}".format(self.u10.shape,self.v10.shape))
        print("WS  shape: {}      WD  shape: {}".format(self.ws.shape,self.wd.shape))
        #
        print("MJD  MAX : {:10.2f} {:4s}     MJD  MIN  : {:10.2f} {:4s}".format(self.mjd.max(), self.mjd_unit, self.mjd.min(),  self.mjd_unit))
        print(self.prFIf("u10"))
        print(self.prFIf("v10"))
        print(self.prFIf("mslp"))
        print(self.prFIf("dpt2"))
        print(self.prFIf("t2"))
        print(self.prFIe("tp"))
        print(self.prFIe("tpx"))
        print(self.prFIe("cdr"))
        print(self.prFIe("cdrx"))
        print(self.prFIe("cbh"))
        print(self.prFIe("cp"))
        print(self.prFIe("lsp"))
        print(self.prFIe("lspx"))
        print(self.prFIf("sp"))
        print(self.prFIf("tcc"))
        print(self.prFIf("vis"))
        print(self.prFIf("c1"))
        print(self.prFIf("c2"))
        print(self.prFIf("c3"))
        print(self.prFIf("ws"))
        print(self.prFIf("wd"))
        print(self.prFIf("wx"))
        print(self.prFIf("wy"))

    #def END

#
#
#
#


    def printGRIBMatrix(self):
        xlen=self.x.shape[0]
        ylen=self.y.shape[1]
        yrange1 = [0, 1 ]
        yrange2 = [ylen-2, ylen-1]
        xrange1 = [0,8]
        xrange2 = [xlen-8,xlen]
        print("GRIB Grid 000 {:10d}{:12s}{:10d}{:14s}{:12d}{:10s}{:12d}"
            .format(yrange1[0]," ",yrange1[1]," ",yrange2[0]," ",yrange2[1]))
        for i in range(xrange1[0],xrange1[1]):
            strx="GRIB Grid {:3d} ".format(i+1)
            for j in yrange1:
                strx=strx+"({:8.0f}; {:8.0f})  ".format(self.x[i][j],self.y[i][j])
            strx = strx + "... "
            for j in yrange2:
                strx=strx+"({:8.0f}; {:8.0f})  ".format(self.x[i][j],self.y[i][j])
            print(strx)
        print("   ...   ")
        for i in range(xrange2[0],xrange2[1]):
            strx="GRIB Grid {:3d} ".format(i+1)
            for j in yrange1:
                strx=strx+"({:8.0f}; {:8.0f})  ".format(self.x[i][j],self.y[i][j])
            strx = strx + "... "
            for j in yrange2:
                strx=strx+"({:8.0f}; {:8.0f})  ".format(self.x[i][j],self.y[i][j])
            print(strx)
            # for END
        # for END


