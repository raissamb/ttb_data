#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 26 11:27:52 2025

@author: raissamb
"""

from pathlib import Path
import pandas as pd
import module_utils as ut
import matplotlib.pyplot as plt
from datetime import datetime

dta = pd.read_csv("t1_ttb.csv")
dta["Datetime"] = pd.to_datetime(dta["Datetime"], format="%Y-%m-%d %H:%M:%S")
#dta = dta.sort_values(by='Datetime_GMT0')

wdc = pd.read_csv("t2_wdc.csv")
wdc["Datetime"] = pd.to_datetime(wdc["Datetime"], format="%Y-%m-%d %H:%M:%S")

t3 = pd.read_csv("t3_manual.csv")
t3["Datetime_Fix"] = pd.to_datetime(t3["Datetime_Fix"], format="%Y-%m-%d %H:%M:%S")






label1= "dta"
label2="wdc"
label3= "manual"
unit = "nT"
comp = "H"
ymin = 10
ymax = 10

date = wdc["Datetime"].dt.date.iat[0]
x1 = dta["Datetime"].dt.hour
y1 = dta["H"]
x2 = wdc["Datetime"].dt.hour
y2 = wdc["H"]
x3 = t3["Datetime_Fix"].dt.hour
y3 = t3["H"]



# Plot
fig, ax = plt.subplots()
ax.scatter(x1, y1, color = "blue", marker='x', label = label1)
ax.scatter(x2, y2, color = "red", label = label2)
ax.scatter(x3, y3, color = "green", marker="s", label = label3)
ax.set(xlabel = "Time (hours)", ylabel = unit, 
       title= f"{comp} in {date}")
ax.set_ylim(min(y1) - ymin, max(y1) + ymax)
plt.xticks(x2)
ax.legend()
plt.tight_layout()
plt.show()