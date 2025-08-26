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


wdc = pd.read_csv("wdc4sep.csv")
wdc["Datetime_GMT0"] = pd.to_datetime(wdc["Datetime_GMT0"], format="%Y-%m-%d %H:%M:%S")

dta = pd.read_csv("ttb4sep.csv")
dta["Datetime_GMT0"] = pd.to_datetime(dta["Datetime_GMT0"], format="%Y-%m-%d %H:%M:%S")
dta = dta.sort_values(by='Datetime_GMT0')


label1= "dta"
label2="wdc"
unit = "nT"
comp = "H"
ymin = 10
ymax = 10

date = wdc["Datetime_GMT0"].dt.date.iat[0]
x1 = dta["Datetime_GMT0"].dt.hour
y1 = dta["H"]
x2 = wdc["Datetime_GMT0"].dt.hour
y2 = wdc["H"]

# Plot
fig, ax = plt.subplots()
ax.scatter(x1, y1, color = "blue", marker='x', label = label1)
ax.scatter(x2, y2, color = "red", label = label2)
ax.set(xlabel = "Time (hours)", ylabel = unit, 
       title= f"{comp} in {date}")
ax.set_ylim(min(y1) - ymin, max(y1) + ymax)
plt.xticks(x2)
ax.legend()
plt.tight_layout()
plt.show()