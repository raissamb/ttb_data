#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 23 13:42:15 2025

@author: raissamb

Depois ajeitar para fazer para outros anos alem de 1964

"""

import pandas as pd
from pathlib import Path
import module_utils as ut
import numpy as np

input_folder = Path("../data/raw_data/ttb_staff_data/Dados64/")
output_folder = Path("../output/hmv_tables/")

# Get all files in directory
files = []
files = ut.list_files_in_folder(files, input_folder)

# ==================== Process for H component
files_h = []
pattern = "H.DTA$"

# Find only files for H component
ut.find_pattern(pattern, files, files_h)

# Create dataframes and mark NaN values
hdfs = []
hnans = []
ut.create_dfs_component(input_folder, files_h, hnans, hdfs)

# Transform dfs into HMV tables for one year (original)
h_hmv = []
ut.create_hmv_tables_year_v2(hdfs, "H", h_hmv)
hconcat = pd.concat(h_hmv)

# fix date and time
first3dates = hconcat["Dates"].iat[0] 
#dates_list = 
#hconcat["Corrected_Date"] = 


def get_dates_in_year(year):
    """
    Generates a list of all dates within a specified year.

    Args:
        year (int): The year for which to retrieve the dates.

    Returns:
        list: A list of datetime.date objects, representing each day of the year.
    """
    dates_list = []
    start_date = date(year, 1, 1)
    # Determine the end date (December 31st of the given year)
    end_date = date(year, 12, 31)

    current_date = start_date
    while current_date <= end_date:
        dates_list.append(current_date)
        current_date += timedelta(days=1)
    return dates_list

# Example usage:
year_to_check = 2024
all_dates = get_dates_in_year(year_to_check)




# Create one df for year for a component
#h_hmvs_list = []
#h_hmv_df = pd.DataFrame()
#h_hmv_df = ut.concat_hmv_tables(h_hmv, "H", h_hmv_df)
#"""



"""
# ==================== Process for D component
files_d = []
pattern = "D.DTA$"
# Find only files for Z component
ut.find_pattern(pattern, files, files_d)

# Create dataframes and mar NaN values
ddfs = []
dnans = []
ut.create_dfs_component(input_folder, files_d, dnans, ddfs)

# Conversion for declination values: from decimal arcmin to arcmin to decimal degree
for item in ddfs:
    df = item
    column_headers_list = df.columns.tolist()
    del column_headers_list[0]
    
    for item in column_headers_list:
        # declination is negative in TTB, dta files have no signal to show it
        df[item] = ((df[item] / 10) / 60) * (-1)

   
# Transform dfs into HMV tables for one year
d_hmv = []
ut.create_hmv_tables_year(ddfs, "D", d_hmv) 
        
# Create one df for year for a component
d_hmv_df = pd.DataFrame()
d_hmv_df = ut.concat_hmv_tables(d_hmv, "D", d_hmv_df)  




# ==================== Process for Z component
files_z = []
pattern = "Z.DTA$"
# Find only files for Z component
ut.find_pattern(pattern, files, files_z)

# Create dataframes and mar NaN values
zdfs = []
znans = []
ut.create_dfs_component(input_folder, files_z, znans, zdfs)

# Transform dfs into HMV tables for one year
z_hmv = []
ut.create_hmv_tables_year(zdfs, "Z", z_hmv)

# Create one df for year for a component
#z_hmvs_list = []
z_hmv_df = pd.DataFrame()
z_hmv_df = ut.concat_hmv_tables(z_hmv, "Z" , z_hmv_df)


# Concat all the components dfs into an unique df for a year
df_all = h_hmv_df.copy()
df_all["D"] = d_hmv_df["D"]
df_all["Z"] = z_hmv_df["Z"]
df_all["Hours_in_year"] = list(range(1, len(df_all) + 1))
df_all.rename(columns={'Datetime': 'Datetime_GMT-3'}, inplace=True)



# Save final df
header_order = ["Datetime_GMT-3", "DOY", "H", "D" ,"Z", 
                "Hours_in_day", "Hours_in_year" ,"Data_source"]
df_final = df_all[header_order].copy()
df_final = df_final.reset_index()
del df_final["index"]

# Fix errors in tables

# Z: 25/06/1964 
df_final.at[4244, "Z"] = np.nan


ut.save_formatted_file("dta_ttb1964.csv", df_final, output_folder)

"""