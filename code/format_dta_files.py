#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 23 13:42:15 2025

@author: raissamb
"""

import pandas as pd
from pathlib import Path
import module_format_data as fd
import glob
import re


input_folder = Path("../data/raw_data/ttb_staff_data/Dados64/")

files = []
files = fd.list_files_in_folder(files, input_folder)

files_h = []
pattern = "H.DTA$"


def find_pattern(pattern, input_list, output_list): 
    for item in input_list:
        if re.search(pattern, item): 
            output_list.append(item)



find_pattern(pattern, files, files_h)
header = ["info", 
          "0-1h","1-2h", "2-3h", "3-4h", "4-5h", "5-6h", 
         "6-7h", "7-8h", "8-9h", "9-10h", "10-11h", "11-12h",
         "12-13h" ,"13-14h", "14-15h", "15-16h", "16-17h", "17-18h", 
         "18-19h", "19-20h", "20-21h" , "21-22h", "22-23h", "23-24h"]

h1964 = []
hnans = []

for item in files_h:
    df = pd.read_csv(input_folder/item, names=["All"])
    has_nan = df.isna().any().any()
    hnans.append(has_nan)

    j = 0
    k = 10
    for i in range(25):
        
        df[header[i]] = df["All"].str.slice(j, k)
        j = k
        k = k + 5
        
    
    df["info"] = df["info"].str.replace('ttb', '19')
    df["info"] = df["info"].str.replace('H', '')
    df["Year"] = df["info"].str.slice(0,4)
    df["Month"] = df["info"].str.slice(4,6)
    df["Day"] = df["info"].str.slice(6,8)
    df["Date"] = pd.to_datetime(df[['Year', 'Month', 'Day']])
    
    df_mod = df.drop(columns=['All', "info", "Year", "Month", "Day"], axis=1)
    
    new_order = ["Date", 
                 "0-1h","1-2h", "2-3h", "3-4h", "4-5h", "5-6h", 
             "6-7h", "7-8h", "8-9h", "9-10h", "10-11h", "11-12h",
             "12-13h" ,"13-14h", "14-15h", "15-16h", "16-17h", "17-18h", 
             "18-19h", "19-20h","20-21h" ,"21-22h", "22-23h", "23-24h"]

    # Reorder the DataFrame
    df_final = df_mod[new_order]
    
    # Convert columns at index 0 and 2 (col_0 and col_2) to float
    #df_final.iloc[:, [1, 25]] = df_final.iloc[:, [1, 25]].astype('float')
    
    del new_order[0]
    for item in new_order:
        df_final[item] = pd.to_numeric(df[item], errors='coerce')
    
    
    #df_reindex = 
    
    
    
    h1964.append(df_final)





#def flat_tables():


teste = h1964[0]
#teste.info()
date= teste.iat[0,0]
hmv = teste.iloc[0:1, 1:25].values.tolist()
flattened_list = [item for sublist in hmv for item in sublist]
dates = [date] * 24
hours = []
for i in range(0,24):
    hours.append(i)



dc = {"Dates": dates,    'H_hmv': flattened_list}
df1 = pd.DataFrame(dc)
df1["hours"] = hours

df1['full_datetime'] = df1['Dates'] + pd.to_timedelta(df1['hours'], unit='h')

df1.info()


"""




df_modified = df.copy()
df_modified["info"] = df_modified["info"].str.replace('ttb', '19')
df_modified["info"] = df_modified["info"].str.replace('H', '')
df_modified["Year"] = df_modified["info"].str.slice(0,4)
df_modified["Month"] = df_modified["info"].str.slice(4,6)
df_modified["Day"] = df_modified["info"].str.slice(6,8)
df_modified["Date"] = pd.to_datetime(df_modified[['Year', 'Month', 'Day']])

df_final = df_modified.drop(columns=['All', "info", "Year", "Month", "Day"], axis=1)


df = pd.read_csv(input_folder/files_h[11], names=["All"])


j = 0
k = 10
for i in range(24):
    
    df[header[i]] = df["All"].str.slice(j, k)
    j = k
    k = k + 5
    
"""