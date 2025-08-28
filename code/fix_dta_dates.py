#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 27 15:45:10 2025

@author: raissamb
"""

# ficou ainda mais distante os picos, precisar ajeitar isso

from pathlib import Path
import pandas as pd
import module_utils as ut
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import timedelta
import numpy as np

# Paths and files
dta_folder = Path("../output/proc_data/formatted_dta_tables/")
wdc_folder = Path("../output/proc_data/wdc_hmv_tables/")
output_folder = Path("../output/plot_hmv_day/")

dtafiles = []
ut.list_files_in_folder(dtafiles, dta_folder)

dta = pd.read_csv(dta_folder/dtafiles[0])
dta["Dates"] = pd.to_datetime(dta["Dates"], format="%Y-%m-%d")
hours = list(range(0,24)) 
col_hours = hours * int((len(dta)/24))
dta["Hours"] = col_hours 
dta["Datetime"] = dta['Dates'] + pd.to_timedelta(dta["Hours"], unit='h')

# Get y m d in columns
#dta["Year"] = dta["Dates"].dt.year
dta["Month"] = dta["Dates"].dt.month
dta["Day"] = dta["Dates"].dt.day


doy = 245
day_orig = dta.loc[dta["DOY"] == doy]
l1 = day_orig.index[0]
l2 = day_orig.index[-1]
i1 = l1 - 2
i2 = l2 - 2
day_mod = dta.loc[i1:i2].copy()


shifth = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 0]

#x3 = day_mod["Datetime"].dt.hour
x3 = shifth
y3 = day_mod["H"]



######### Plot
wdcfiles = []
ut.list_files_in_folder(wdcfiles, wdc_folder)
wdc = pd.read_csv(wdc_folder/wdcfiles[0])
wdc["Datetime_UTC0"] = pd.to_datetime(wdc["Datetime_UTC0"])

def plot_scatter2_hmv_day(df1, df2, x3, y3, label1, label2, doy, comp, unit, folder, ymax, ymin):
    
    # df1
    aux1 = df1[df1['DOY'] == doy]
    x1 = aux1["Datetime"].dt.hour
    y1 = aux1[comp]
    print("y1: ", len(aux1))
    
    # df2
    aux2 = df2[df2['DOY'] == doy]
    x2 = aux2["Datetime_UTC0"].dt.hour
    y2 = aux2[comp]
    print("y2: ", len(aux2))
    print("y3: ", len(y3))

    date = aux2["Datetime_UTC0"].dt.date.iat[0]
    figname = f"{date}_{comp}_hmv_{label1}_{label2}_add3.png"
    
    # Plot
    fig, ax = plt.subplots()
    ax.scatter(x1, y1, color = "blue", label = label1)
    ax.scatter(x3, y3, color = "green", marker= "s", label = "dta shift")
    ax.scatter(x2, y2, color = "red", marker= "*", label = label2)
    ax.set(xlabel = "Time (hours)", ylabel = unit, 
           title= f"{comp} in {date}")
        #title= f"{comp} in {date} Timeshifted + 3")
    ax.set_ylim(min(y1) - ymin, max(y1) + ymax)
    #plt.xticks(rotation=90) 
    ax.legend()
    plt.tight_layout()
    plt.show()
    #fig.savefig(folder/figname, dpi=300, bbox_inches="tight")
    
    my_nested_list = [y1, y2, y3]
    return np.array(my_nested_list).T




# Plot single day
#doy = 245
#doy = 256
teste = plot_scatter2_hmv_day(dta, wdc, x3, y3, "dta", "wdc", doy, "H", "nT", output_folder, 10, 10)


# Plot list of days
#doylist = list(range(245,367)) #245 a 366 sep-dec
#doylist = list(range(245,265)) # september
#for item in doylist:
#    plot_scatter2_hmv_day(dta, wdc, "dta", "wdc", item, "H", "nT", output_folder, 10, 10)



"""

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
hours = list(range(0,24))  * 366
nhours = hours[:-3]
d1["Hours_UTC0"] = nhours 
# faltam 3 rows que devem estar na tabela do proximo ano

d1["DatesUTC0"] = d1["DatesUTC0"] + pd.to_timedelta(d1["Hours_UTC0"], unit='h')

d1.to_csv("t4.csv", index=False, na_rep=np.nan, header=True)



x1 = d1["DatesUTC0"].dt.hour


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
    
    
    
plot_scatter2_hmv_day(d1, wdc, "dta", "wdc", 256, "H", "nT", output, 10, 10)




PARA AJEITAR DATA E HORA DEPOIS, FIX Z SPIKE DEPOIS

utc0 = utc0 = list(range(0, 24))



# fix date and time
year_to_check = hconcat["Dates"].dt.year.iat[0]
year_dates = ut.get_dates_in_year(year_to_check)
all_dates = [element for element in year_dates for _ in range(24)]

tab = hconcat["Dates"]
c = year_dates[1:]

#del all_dates[3:24] # delete first 21 hours from the first day in the year
#next_date = [f"{year_to_check + 1}-01-01"] * 21
#finaldates = all_dates + next_date

#hconcat["Corrected_Date"] =  finaldates
#hconcat["Corrected_Date"] = pd.to_datetime(hconcat["Corrected_Date"])
#hconcat.info()
#hconcat["Datetime_UTC0"] = hconcat["Corrected_Date"] + pd.to_timedelta(hconcat["UTC-3"], unit='h')
# hconcat.to_csv("hteste.csv", index=False, na_rep=np.nan, header=True)

# Fix errors in tables

# Z: 25/06/1964 
df_final.at[4244, "Z"] = np.nan
"""