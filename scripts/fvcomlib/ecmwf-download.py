import fvcomlibecmwf as e

DownloadNewData = True

if ( DownloadNewData ):
    e.download_ecmwf_data()
    e.copyToArchive()


