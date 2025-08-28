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


dta_folder = Path("../output/data/formatted_dta_tables/")
wdc_folder = Path("../output/data/wdc_hmv_tables/")
output_folder = Path("../output/plot_hmv_day/")

dtafiles = []
ut.list_files_in_folder(dtafiles, dta_folder)

wdcfiles = []
ut.list_files_in_folder(wdcfiles, wdc_folder)

dta = pd.read_csv(dta_folder/dtafiles[0])
dta["Dates"] = pd.to_datetime(dta["Dates"])
#dta.info()

wdc = pd.read_csv(wdc_folder/wdcfiles[0])
wdc["Datetime_UTC0"] = pd.to_datetime(wdc["Datetime_UTC0"])
#wdc.info()



def plot_scatter2_hmv_day(df1, df2, label1, label2, doy, comp, unit, folder, ymax, ymin):
    
    # df1
    aux1 = df1[df1['DOY'] == doy]
    x1 = aux1["Dates"].dt.hour
    y1 = aux1[comp]
    
    # df2
    aux2 = df2[df2['DOY'] == doy]
    x2 = aux2["Datetime_UTC0"].dt.hour
    y2 = aux2[comp]

    date = aux2["Datetime_UTC0"].dt.date.iat[0]
    figname = f"{date}_{comp}_hmv_{label1}_{label2}_nofixdate.png"
    
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





# Plot single day
#plot_scatter2_hmv_day(dta, wdc, "dta", "wdc", 256, "H", "nT", output_folder, 10, 10)

# Plot list of days
#doylist = list(range(245,367)) #245 a 366 sep-dec
# doylist = list(range(245,265)) # september
# for item in doylist:
#     plot_scatter2_hmv_day(dta, wdc, "dta", "wdc", item, "H", "nT", output_folder, 10, 10)


