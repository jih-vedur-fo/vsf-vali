#adddye.py
from netCDF4 import Dataset
import numpy as np
import sys
import fvcomlibutil as u

# Open the existing hotstart file
hotstart_file = "hotstart.nc"
DEBUG         = False

nargs = len(sys.argv)
cmdparams = []
params = []
for i in range(nargs):
    cmdparams.append(sys.argv[i])
# for i END
if len(cmdparams)>1:
        params=u.parse_kv_pairs(cmdparams[1])
# if END



if ("debug" in params):            DEBUG            = bool(int(params["debug"]))
if ("hotstartfile" in params):     hotstart_file    = params["hotstartfile"]


nc = Dataset(hotstart_file, "a")

# Get dimensions
nele = len(nc.dimensions['nele'])  # Number of elements
node = len(nc.dimensions['node'])  # Number of nodes
time = len(nc.dimensions['time'])  # Number of time steps
siglay = len(nc.dimensions['siglay'])  # Number of sigma layers

# Create a new dye variable (adjust as needed)
dye_init = np.zeros((time,siglay, node))  # Initial dye concentration at zero

# Add DYE variable
dye_var = nc.createVariable('DYE', 'f4', ('time', 'siglay', 'node'))
dye_var.units = 'kg/m3'
dye_var.long_name = 'Dye Concentration'
dye_var[:] = dye_init  # Assign initial values

nc.close()
print("DYE field successfully added!")
