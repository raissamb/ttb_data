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

# 1. Force resolve the absolute path to this utility script file first
CURRENT_FILE_PATH = Path(__file__).resolve()

# 2. Step back out of the modules/ directory to find your core 'code/' directory level
CODE_ROOT = CURRENT_FILE_PATH.parent

#import module_utils as ut

# 3. Derive the absolute repository workspace root directory location
PROJECT_HOME = CODE_ROOT.parent
DATA_FOLDER = PROJECT_HOME / "data" / "raw_data" / "metadata_yearbooks" 

# 4. Define output folders
baseline_folder = PROJECT_HOME / "data" / "formatted_baselines"
baseline_folder.mkdir(parents=True, exist_ok=True)

scale_folder = PROJECT_HOME / "data" / "formatted_scale_values"
scale_folder.mkdir(parents=True, exist_ok=True)

# Get all files in directory
files = ut.list_files_in_folder(Path(DATA_FOLDER))
baselines_files = files[0:3]
scale_values_files = files[3:7]

### BASELINES
dfs_baselines = []
for item in baselines_files:
    df = pd.read_csv(DATA_FOLDER/item)
    df = df.dropna()
    
    # Fix dates and get decimal year
    df["Date"] = pd.to_datetime(df["Date"], format='%d-%m-%Y')
    df["Date_baseline_means"] = pd.to_datetime(df["Date_baseline_means"], format='%d-%m-%Y')
    df["Decimal_year"] = ut.calculate_decimal_year(df["Date_baseline_means"])
    df["Month"] = df["Date_baseline_means"].dt.month
    
    # Get year and component
    year = df["Date_baseline_means"].dt.year.iat[0]
    comp = df["Component"].iat[0]
    
    if comp == "D":
        df["Baseline_means_dd"] = df["Baseline_means_degree"] + (df["Baseline_means_minute"]/60)
    
    filename = f"baseline_{year}_{comp}.csv"
    ut.save_formatted_file(filename, df, baseline_folder)
    
    # result
    dfs_baselines.append(df)


### SCALE VALUES
dfs_scale = []
for item in scale_values_files:
    df = pd.read_csv(DATA_FOLDER/item)
    df = df.dropna()
    df["Date"] = pd.to_datetime(df["Date"], format='%d-%m-%Y')
    #df["Decimal_year"] = df["Date"].apply(ut.to_decimal_year)
    df["Decimal_year"] = ut.calculate_decimal_year(df["Date"])
    df["Month"] = df["Date"].dt.month
    
    # Get year and component
    year = df["Date"].dt.year.iat[0]
    comp = df["Component"].iat[0]
    filename = f"scale_values_{year}_{comp}.csv"
    ut.save_formatted_file(filename, df, scale_folder)
    
    dfs_scale.append(df)


