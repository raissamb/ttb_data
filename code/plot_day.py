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


dta_folder = Path("../output/proc_data/formatted_dta_tables/")
wdc_folder = Path("../output/proc_data/wdc_hmv_tables/")
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


a1 = wdc[wdc['DOY'] == 245]
a2 = a1["Datetime_UTC0"].dt.hour
a3 = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 0, 1, 2]

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
    figname = f"{date}_{comp}_hmv_TTB_data.png"
    
    # Plot
    fig, ax = plt.subplots()
    ax.scatter(x2, y1, color = "blue", label = label1)
    #ax.scatter(a3, y1, color = "green", marker= "s", label = "dta shift")
    #ax.scatter(x2, y2, color = "red", marker= "*", label = label2)
    ax.set(xlabel = "Time (hours)", ylabel = unit, 
           title= f"{comp} in {date}")
        #title= f"{comp} in {date} Timeshifted + 3")
    ax.set_ylim(min(y1) - ymin, max(y1) + ymax)
    #plt.xticks(rotation=90) 
    ax.legend()
    plt.tight_layout()
    plt.show()
    fig.savefig(folder/figname, dpi=300, bbox_inches="tight")




# Plot single day
#doy = 245
doy = 257
plot_scatter2_hmv_day(dta, wdc, "dta", "wdc", doy, "H", "nT", output_folder, 10, 10)

# Plot list of days
#doylist = list(range(245,367)) #245 a 366 sep-dec
#doylist = list(range(245,265)) # september
#for item in doylist:
#    plot_scatter2_hmv_day(dta, wdc, "dta", "wdc", item, "H", "nT", output_folder, 10, 10)


