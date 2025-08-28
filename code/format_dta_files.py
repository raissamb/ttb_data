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
#import numpy as np
#from datetime import date, timedelta
import os

# Files and paths
output_folder = Path("../output/data/formatted_dta_tables/")
dir_path = Path("../data/raw_data/ttb_staff_data/")

# # MAJOR LOOP
# # list of data folders
# flist = [
#     f for f in os.listdir(dir_path) if os.path.isdir(os.path.join(dir_path, f))
# ]
# flist.sort()


flist = ["Dados64"]

for item in flist:
    input_folder = Path(f"../data/raw_data/ttb_staff_data/{item}/")
    
    # Get all files in directory
    files = []
    ut.list_files_in_folder(files, input_folder)

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
    ut.create_hmv_tables_year_v2(zdfs, "Z", z_hmv)
    zconcat = pd.concat(z_hmv)

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
    ut.create_hmv_tables_year_v2(ddfs, "D", d_hmv) 
    dconcat = pd.concat(d_hmv)

    # Check size for each yearly table
    print(True if len(hconcat) == len(dconcat) and len(dconcat) == len(zconcat) else False)

    df_all = hconcat.copy()
    df_all["D"] = dconcat["D"]
    df_all["Z"] = zconcat["Z"]
    df_all["Data_source"] = "TTB_staff_DTA_files"
    # Extract the day of the year and create a new column
    df_all["DOY"] = df_all["Dates"].dt.dayofyear
    
    # Save final df
    order = ["Dates", "DOY", "Interval", "UTC-3", "H", "D" ,"Z", "Data_source"]
    df_all = df_all[order]
    df_all = df_all.reset_index()
    del df_all["index"]

    name = f"dta_ttb_{df_all['Dates'].dt.year.iat[0]}.csv"
    ut.save_formatted_file(name, df_all, output_folder)


