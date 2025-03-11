#!/bin/bash
python3 buildwindECMWF.py -ecmwf basepath=/opt/fvcom/cron/sims/d/x/xiSim501/CRN/crn2025-01-15/input,gridfile=fvcom_lgr_san_grd.dat,T0=60698,T9=60699,heatingactive=1,saveimages=1,winddirmod360=1,mappingmethod=gauss
