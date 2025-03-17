import numpy as np
#
#
#

#def END
#
#=======================================================
def date2MJD(d):
    dateform = "%Y-%m-%d"
    d = dt.strptime(d,dateform)
    d0 = dt.strptime('1858-11-17',dateform)
    delta = d - d0
    #print("Delta d : {}".format(delta.days))
    return delta.days
#def END
#
#=======================================================
# Convert datestring to MJD (float)
def datestr2MJD(dstr):
    dateform = "%Y-%m-%d"
    d  = dt.strptime(dstr,dateform)
    d0 = dt.strptime('1858-11-17',dateform)
    delta = d - d0
    #print("Delta d : {}".format(delta.days))
    return delta.days
#def END
#
#=======================================================
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
#def END
#
#=======================================================
# Convert datetimestring to MJD (float)
def datetimestr2MJD(dtstr):
    datetimeform = "%Y-%m-%d %H:%M:%S"
    d  = dt.strptime(dtstr,datetimeform)
    d0 = dt.strptime('1858-11-17 00:00:00',datetimeform)
    delta = d - d0
    res = delta.days + delta.seconds/86400
    print("Delta d : {}".format(res))
    return res
#def END
#
#=======================================================
# Convert numpy datetime64 to MJD
def datetime64ToMJD(dt64):
    # Reference date: MJD 0 corresponds to 1858-11-17
    mjd_epoch = np.datetime64('1858-11-17T00:00:00')

    # Compute days since the MJD epoch
    mjd = (dt64 - mjd_epoch) / np.timedelta64(1, 'D')

    return mjd
#
# # Example usage
# dt = np.datetime64('2024-03-17T12:00:00')  # Example date
# mjd = datetime64_to_mjd(dt)
# print(f"MJD: {mjd}")
#
#def END
#
#=======================================================
# Convert MJD to numpy datetime64
def MJDToDatetime64(mjd):
    # Reference date: MJD 0 corresponds to 1858-11-17
    mjd_epoch = np.datetime64('1858-11-17T00:00:00')

    # Convert MJD to datetime64 by adding the number of days
    dt64 = mjd_epoch + np.timedelta64(int(mjd), 'D') + np.timedelta64(int((mjd % 1) * 86400), 's')

    return dt64
#
# # Example usage
# mjd = 60380.5  # Example MJD
# dt = mjd_to_datetime64(mjd)
# print(f"Datetime64: {dt}")
#def END
#
#=======================================================

