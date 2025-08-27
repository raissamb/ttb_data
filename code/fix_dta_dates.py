#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 27 15:45:10 2025

@author: raissamb
"""

from pathlib import Path
import pandas as pd
import module_utils as ut
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import timedelta
import numpy as np

# Paths and files
ttb_folder = Path("../output/dta_to_tables/")

dta = pd.read_csv(ttb_folder/"dta_ttb_1964.csv")
dta["Dates"] = pd.to_datetime(dta["Dates"], format="%Y-%m-%d")
dta["DatesUTC0"] = dta["Dates"].copy()

# # get rows with utc-3 21, 22 23
# # Select rows where 'City' is 'New York'
# filtered_df = dta.loc[dta['UTC-3'] == 21]
# original_date = filtered_df["Dates"].tolist()
# utcdate = []
# for item in original_date:
#      yesterday = item - timedelta(days = 1)
#      utcdate.append(yesterday)


# for index, row in dta.iterrows():
#     if [dta.loc[dta['UTC-3'] == 21]]:
#         #dta["DatesUTC0"] = dta["Dates"] - timedelta(days = 1)

dta.loc[dta['UTC-3'] == 21, "DatesUTC0"] = dta["Dates"] - timedelta(days = 1)
dta.loc[dta['UTC-3'] == 22, "DatesUTC0"] = dta["Dates"] - timedelta(days = 1)
dta.loc[dta['UTC-3'] == 23, "DatesUTC0"] = dta["Dates"] - timedelta(days = 1)
dta["New_DOY"] = dta["DatesUTC0"].dt.dayofyear
dta["DatesUTC0"] = pd.to_datetime(dta["DatesUTC0"])


d1 = dta.copy()
d1 = d1.iloc[3:]
d1 = d1.reset_index()

d1.to_csv("t4.csv", index=False, na_rep=np.nan, header=True)

# for i in range(0, 366):
#     a1 = d1.loc[d1['New_DOY'] == i]
#     a1["DatesUTC0"] = a1["DatesUTC0"] + pd.Timedelta(hours=1)




#x1 = dta["DatesUTC0"].dt.hour

dta.info()

wdc_folder= Path("../output/wdc_hmv_tables/")
output = Path("../output/plot_hmv_day/")
wdc = pd.read_csv(wdc_folder/"wdc_ttb_1964.csv")
wdc["Datetime_GMT0"] = pd.to_datetime(wdc["Datetime_GMT0"])

x2 = wdc["Datetime_GMT0"].dt.hour

def plot_scatter2_hmv_day(df1, df2, label1, label2, doy, comp, unit, folder, ymax, ymin):
    
    # df1
    aux1 = df1[df1['New_DOY'] == doy]
    x1 = aux1["DatesUTC0"].dt.hour
    y1 = aux1[comp]
    
    # df2
    aux2 = df2[df2['DOY'] == doy]
    x2 = aux2["Datetime_GMT0"].dt.hour
    y2 = aux2[comp]

    date = aux2["Datetime_GMT0"].dt.date.iat[0]
    figname = f"{date}_{comp}_hmv_{label1}_{label2}.png"
    
    # Plot
    fig, ax = plt.subplots()
    ax.scatter(x1, y1, color = "blue", label = label1)
    ax.scatter(x2, y2, color = "red", label = label2)
    ax.set(xlabel = "Time (hours)", ylabel = unit, 
           title= f"{comp} in {date} WDC")
    ax.set_ylim(min(y1) - ymin, max(y1) + ymax)
    #plt.xticks(rotation=90) 
    ax.legend()
    plt.tight_layout()
    plt.show()
    fig.savefig(folder/figname, dpi=300, bbox_inches="tight")
    
    
    
#plot_scatter2_hmv_day(dta, wdc, "dta", "wdc", 256, "H", "nT", output, 10, 10)