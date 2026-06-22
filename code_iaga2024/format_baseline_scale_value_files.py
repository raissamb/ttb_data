# -*- coding: utf-8 -*-
"""
Created on Sat Aug 30 10:11:12 2025

@author: raiss
"""

import pandas as pd
from pathlib import Path
import numpy as np
import module_utils as ut
import matplotlib.pyplot as plt

input_folder = Path("../data/metadata_yearbooks/")
output_folder = Path("../output/proc_data/baselines_scale_values_tables/")


# Get all files in directory
files = []
files = ut.list_files_in_folder(files, input_folder)
baselines = files[0:3]
scale_values = files[3:7]

### BASELINES
dfs_baselines = []
for item in baselines:
    df = pd.read_csv(input_folder/item)
    df = df.dropna()
    
    # Fix dates and get decimal year
    df["Date"] = pd.to_datetime(df["Date"], format='%d-%m-%Y')
    df["Date_baseline_means"] = pd.to_datetime(df["Date_baseline_means"], format='%d-%m-%Y')
    df["Decimal_year"] = df["Date_baseline_means"].apply(ut.to_decimal_year)
    df["Month"] = df["Date_baseline_means"].dt.month
    
    # Get year and component
    year = df["Date_baseline_means"].dt.year.iat[0]
    comp = df["Component"].iat[0]
    
    if comp == "D":
        df["Baseline_means_dd"] = df["Baseline_means_degree"] + (df["Baseline_means_minute"]/60)
    
    filename = f"baseline_{year}_{comp}.csv"
    ut.save_formatted_file(filename, df, output_folder)
    
    # result
    dfs_baselines.append(df)


### SCALE VALUES
dfs_scale = []
for item in scale_values:
    df = pd.read_csv(input_folder/item)
    df = df.dropna()
    df["Date"] = pd.to_datetime(df["Date"], format='%d-%m-%Y')
    df["Decimal_year"] = df["Date"].apply(ut.to_decimal_year)
    df["Month"] = df["Date"].dt.month
    
    # Get year and component
    year = df["Date"].dt.year.iat[0]
    comp = df["Component"].iat[0]
    filename = f"scale_values_{year}_{comp}.csv"
    ut.save_formatted_file(filename, df, output_folder)
    
    dfs_scale.append(df)