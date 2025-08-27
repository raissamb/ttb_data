#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 27 14:56:21 2025

@author: raissamb
"""

from pathlib import Path
import pandas as pd
import module_utils as ut
import matplotlib.pyplot as plt
from datetime import datetime

# Paths and files
ttb_folder = Path("../output/dta_to_tables/")
wdc_folder= Path("../output/wdc_hmv_tables/")
output = Path("../output/plot_hmv_day/")

dta = pd.read_csv(ttb_folder/"dta_ttb_1964.csv")
dta["Dates"] = pd.to_datetime(dta["Dates"], format="%Y-%m-%d")

wdc = pd.read_csv(wdc_folder/"wdc_ttb_1964.csv")
wdc["Datetime_GMT0"] = pd.to_datetime(wdc["Datetime_GMT0"])



def plot_scatter2_hmv_day(df1, df2, label1, label2, doy, comp, unit, folder, ymax, ymin):
    
    # df1
    aux1 = df1[df1['DOY'] == doy]
    x1 = aux1["Dates"].dt.hour
    y1 = aux1[comp]
    
    # df2
    aux2 = df2[df2['DOY'] == doy]
    x2 = aux2["Datetime_GMT0"].dt.hour
    y2 = aux2[comp]

    date = aux2["Datetime_GMT0"].dt.date.iat[0]
    figname = f"{date}_{comp}_hmv_{label1}_{label2}.png"
    
    # Plot
    fig, ax = plt.subplots()
    ax.scatter(x2, y1, color = "blue", label = label1)
    ax.scatter(x2, y2, color = "red", label = label2)
    ax.set(xlabel = "Time (hours)", ylabel = unit, 
           title= f"{comp} in {date} WDC")
    ax.set_ylim(min(y1) - ymin, max(y1) + ymax)
    #plt.xticks(rotation=90) 
    ax.legend()
    plt.tight_layout()
    plt.show()
    fig.savefig(folder/figname, dpi=300, bbox_inches="tight")



doylist = list(range(245,367)) #245 a 366


for item in doylist:
    plot_scatter2_hmv_day(dta, wdc, "dta", "wdc", item, "H", "nT", output, 10, 10)











# x1 = dta["Dates"]
# y1 = dta["H"]
# x2 = wdc["Datetime_GMT0"]
# y2 = wdc["H"]
# #x3 = t3["Datetime_Fix"].dt.hour
# #y3 = t3["H"]
# label1= "dta"
# label2= "wdc"


# # Plot
# fig, ax = plt.subplots()
# ax.scatter(x1, y1, color = "blue", marker='x', label = label1)
# ax.scatter(x2, y2, color = "red", label = label2)
# #ax.scatter(x3, y3, color = "green", marker="s", label = label3)
# ax.set(xlabel = "Time (hours)", ylabel = "nT", 
#        title= f"H")
# plt.xticks(x2)
# ax.legend()
# plt.tight_layout()
# plt.show()