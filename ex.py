# -*- coding: utf-8 -*-
"""
Created on Mon Sep 21 13:15:28 2020

@author: cjcho
"""
import sys
from netCDF4 import Dataset as NetCDFFile
import numpy as np
from datetime import datetime,timedelta
import ttide as tt
import time

import warnings

if not sys.warnoptions:
    warnings.simplefilter("ignore")

start_time=time.clock()

#Model file load
MDL_file=r'Y:\BGKim\haramoinc_analysis/Water_height_TideBed_1km_108std_st1.nc'
#MDL_file='../data/MOHID_WH_1km_2018fmt.nc' #201905
mnc=NetCDFFile(MDL_file)
MDL_lat2=mnc.variables['t_lat'][:]
MDL_lon2=mnc.variables['t_lon'][:]
MDL_tide=mnc.variables['t_WH'][:]
MDL_times=mnc.variables['t_times'][:]; MDL_times=np.array(MDL_times)
mnc.variables.keys()
#MDL_hour=mnc.variables['Hour'][:]
MDL_mask=np.squeeze(MDL_tide[0,:,:]) #mask with nan
#MDL_lon2,MDL_lat2=np.meshgrid(MDL_lon,MDL_lat)
MDL_time=np.array([datetime(int(i[0]),int(i[1]),int(i[2]),int(i[3]),int(i[4]),int(i[5])) for i in MDL_times])

mnc.close()
###############
MDL_file=r'Y:\BGKim\haramoinc_analysis/MOHID_WH_1km_2018fmt.nc'
mnc=NetCDFFile(MDL_file)
mnc.variables.keys()
MDL_lat=mnc.variables['lat'][:]
MDL_lon=mnc.variables['lon'][:]
MDL_tide=mnc.variables['tide'][:]
MDL_day=mnc.variables['Day'][:]
MDL_hour=mnc.variables['Hour'][:]
mnc.close()
MDL_mask=np.squeeze(MDL_tide[0,:,:]) #mask with nan
MDL_lon2,MDL_lat2=np.meshgrid(MDL_lon,MDL_lat)
MDL_time=np.array([datetime(1,1,1,0,0,0)+timedelta(days=MDL_day[i]-1.,seconds=np.float(MDL_hour[i])*3600) for i in range(len(MDL_day))])
MDL_mask=np.squeeze(MDL_tide[0,:,:]) #mask with nan
#MDL_lon2,MDL_lat2=np.meshgrid(MDL_lon,MDL_lat)
#################
toolbar_width=20

HA_list=['M2','S2','K1','O1']

start_time=time.clock()
t_stp=np.size(MDL_lat2,0)*np.size(MDL_lat2,1)
status='progress...'
count=0
#인천 (126.5921, 37.4519), 목포 (126.3755, 34.7797), 묵호(129.1163,37.5503), 부산(129.0354, 35.0962)
cal_amp=np.zeros((4,np.size(MDL_lat2,0),np.size(MDL_lat2,1)),dtype=np.float)*np.nan #M2, S2, K1, O1
cal_pha=cal_amp.copy(); cal_snr=cal_amp.copy()
for ri in range(np.size(MDL_lat2,0)):
    cnt_lat=MDL_lat2[ri,0]
    if cnt_lat==37.55:
        break
    for ci in range(np.size(MDL_lat2,1)):
        cnt_lon=MDL_lon2[0,ci]
        if cnt_lon==129.12:
            break
cnt_val=MDL_mask[ri,ci]
cnt_tide=MDL_tide[:,ri,ci]

tide_result=tt.t_tide(cnt_tide,out_style=None,lat=35,dt=1,stime=MDL_time[0])
tide_result['z0']
import pandas as pd
#pd.DataFrame(index=tfit_e['nameu'],data=tfit_e['tidecon'])
#dates.date2num(pd.date_range('2000-1-01 00:00:00','2020-01-01 00:00:00',freq='H'))
import ttide.time as dates2
pred1=tide_result['z0']+tide_result(np.array([dates2.date2num(i) for i in pd.date_range('2000-1-01 00:00:00','2020-01-01 00:00:00',freq='H')]))
#pd.DataFrame(pred1).plot()
pr_df=pd.DataFrame(index=pd.date_range('2000-1-01 00:00:00','2020-01-01 00:00:00',freq='H'),data={'pred':pred1})
pr_df=pr_df.reset_index()

"""
import matplotlib.pyplot as plt
plt.plot(pd.to_datetime(MDL_time),cnt_tide)
pr_df['index']=pd.to_datetime(pr_df['index'])
pr_df=pr_df.set_index('index')
plt.plot(pr_df['2019'].index,pr_df['2019'].pred)
"""
#pr_df.to_csv(r'C:\Users\cjcho\Desktop/tide_묵호.csv')
pr_df['관측기간']=pr_df['index']
pr_df=pr_df.set_index(['관측기간'])

plt.plot(pr_df['2000'].index,pr_df['2000'].values)
te=pd.read_csv(r'D:\DB\KOOFS\조위관측소/인천_DT_78_201901_KR.txt',skiprows=3,sep='\t',na_values=['-'])
te['관측시간']=pd.to_datetime(te['관측시간'])
te=te.set_index(['관측시간'])
plt.plot(te['조위(cm)'].dropna().index,te['조위(cm)'].dropna())
plt.plot(te['조위(cm)'].dropna().index+pd.to_timedelta(31*15,unit='h'),te['조위(cm)'].dropna())
per=te[['조위(cm)']].join(pr_df[['pred']],how='inner')
np.nansum(abs(per['조위(cm)']-per['pred']))/per.shape[0]
np.sqrt(np.nansum((per['조위(cm)']-per['pred'])**2)/per.shape[0])
