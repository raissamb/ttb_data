#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 25 10:32:21 2025

@author: raissamb
"""

from pathlib import Path
import pandas as pd
import module_utils as ut
import matplotlib.pyplot as plt
from datetime import datetime

# Paths and files
data_folder = Path("../output/hmv_tables/")
surface_folder = Path("../output/plot_surface_hmv/")
histogram_folder = Path("../output/plot_histograms_hmv/")
day_folder = Path("../output/plot_hmv_day/")
wdc_folder = Path("../output/wdc_hmv_tables/")

data_list = []
data_list = ut.list_files_in_folder(data_list, data_folder)

data_file = data_list[0]
df = pd.read_csv(data_folder/data_file)
df["Datetime_GMT-3"] = pd.to_datetime(df["Datetime_GMT-3"], format="%Y-%m-%d %H:%M:%S")

wdc_data_list = []
wdc_data_list = ut.list_files_in_folder(wdc_data_list, wdc_folder)
wdc_data_file = wdc_data_list[0]

wdc = pd.read_csv(wdc_folder/wdc_data_file)
wdc["Datetime_GMT0"] = pd.to_datetime(wdc["Datetime_GMT0"], format="%Y-%m-%d %H:%M:%S")

doy = 245
ut.plot_scatter2_hmv_day(df, wdc, "Staff data", "WDC", doy, "H", "nT", day_folder, 10, 10)
ut.plot_scatter2_hmv_day(df, wdc, "Staff data", "WDC", doy, "Z", "nT", day_folder, 10, 10)
ut.plot_scatter2_hmv_day(df, wdc, "Staff data", "WDC", doy, "D", "dd", day_folder, 0.2, 0.2)

"""
# staff data
aux1 = df[df['DOY'] == doy]
x1 = aux1["Datetime"].dt.hour
y1 = aux1[comp]
date = aux1["Datetime"].dt.date.iat[0]
f1 = f"{date}_{comp}.png"
# wdc data
aux2 = wdc[wdc['DOY'] == doy]
x2 = aux2["datetime"].dt.hour
y2 = aux2[comp]


# Data H
# Plot H
fig1, ax1 = plt.subplots()
ax1.scatter(x1, y1, color = "blue", label = "TTB Staff")
ax1.scatter(x2, y2, color = "red", label = "WDC")
ax1.set(xlabel = "Time (hours)", ylabel = unit, 
       title= f"HMV for {comp} in {date}")
ax1.set_ylim(min(y1) - ymin, max(y1) + ymax)
ax1.legend()
plt.tight_layout()
plt.show()
fig1.savefig(day_folder/f1, dpi=300, bbox_inches="tight")


"""









"""
# Plot time series for a single day
doy = 245
comp = "H"
unit = "nT"
ut.plot_scatter_hmv_day(df, doy, comp, unit, day_folder, 20, 20)

# Plot time series for a single day
doy = 245
comp = "Z"
unit = "nT"
ut.plot_scatter_hmv_day(df, doy, comp, unit, day_folder, 15, 15)

# Plot time series for a single day
doy = 245
comp = "D"
unit = "dd"
ut.plot_scatter_hmv_day(df, doy, comp, unit, day_folder, 0.05, 0.05)
"""