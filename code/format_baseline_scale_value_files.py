# -*- coding: utf-8 -*-
"""
Formatted Observatory Metadata Ingestion
"""

import pandas as pd
from pathlib import Path
import module_utils as ut
import numpy as np

# 1. Path Resolution (Streamlined)
# .parents[1] steps up exactly two levels from the current file
PROJECT_HOME = Path(__file__).resolve().parents[1]
DATA_FOLDER = PROJECT_HOME / "data" / "raw_data" / "metadata_yearbooks" 

baseline_folder = PROJECT_HOME / "data" / "formatted_baselines"
baseline_folder.mkdir(parents=True, exist_ok=True)

scale_folder = PROJECT_HOME / "data" / "formatted_scale_values"
scale_folder.mkdir(parents=True, exist_ok=True)

# 2. Dynamic File Filtering (Replaces brittle files[0:3] logic)
all_files = list(DATA_FOLDER.glob("*.csv"))
baselines_files = [f for f in all_files if "baseline" in f.name.lower()]
scale_values_files = [f for f in all_files if "scale" in f.name.lower()]

### BASELINES
dfs_baselines = []
for file_path in baselines_files:
    df = pd.read_csv(file_path).dropna()
    
    # Safety gate: skip processing if dropna() emptied the dataframe
    if df.empty:
        continue
    
    # Fix dates and get decimal year
    df["Date"] = pd.to_datetime(df["Date"], format='%d-%m-%Y')
    df["Date_baseline_means"] = pd.to_datetime(df["Date_baseline_means"], format='%d-%m-%Y')
    df["Decimal_year"] = ut.calculate_decimal_year(df["Date_baseline_means"])
    df["Month"] = df["Date_baseline_means"].dt.month
    
    # Get year and component dynamically
    year = df["Date_baseline_means"].dt.year.iat[0]
    comp = df["Component"].iat[0]
    
    if comp == "D":
        df["Baseline_means_dd"] = df["Baseline_means_degree"] + (df["Baseline_means_minute"] / 60.0)
    
    filename = f"baseline_{year}_{comp}.csv"
    ut.save_formatted_file(filename, df, baseline_folder)
    dfs_baselines.append(df)


### SCALE VALUES
dfs_scale = []
for file_path in scale_values_files:
    df = pd.read_csv(file_path).dropna()
    
    if df.empty:
        continue
        
    df["Date"] = pd.to_datetime(df["Date"], format='%d-%m-%Y')
    df["Decimal_year"] = ut.calculate_decimal_year(df["Date"])
    df["Month"] = df["Date"].dt.month
    
    # Get year and component dynamically
    year = df["Date"].dt.year.iat[0]
    comp = df["Component"].iat[0]
    
    filename = f"scale_values_{year}_{comp}.csv"
    ut.save_formatted_file(filename, df, scale_folder)
    dfs_scale.append(df)
