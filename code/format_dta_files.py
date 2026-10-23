#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 23 13:42:15 2025

@author: raissamb

Depois ajeitar para fazer para outros anos alem de 1964

"""

import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import numpy as np


# 1. Force resolve the absolute path to this utility script file first
CURRENT_FILE_PATH = Path(__file__).resolve()

# 2. Step back out of the modules/ directory to find your core 'code/' directory level
CODE_ROOT = CURRENT_FILE_PATH.parent

import module_utils as ut

# 3. Derive the absolute repository workspace root directory location
PROJECT_HOME = CODE_ROOT.parent
DATA_FOLDER = PROJECT_HOME / "data" / "raw_data" / "ttb_staff_data" / "Dados64"

# 4. Define output folders
OUT_FOLDER = PROJECT_HOME / "data" / "formatted_dta_data" 
OUT_FOLDER.mkdir(parents=True, exist_ok=True)


all_tables = []

if __name__ == "__main__":
    # Define your data directory (defaults to current working directory '.' here)
    data_dir = Path(DATA_FOLDER)
    
    component = ["H", "Z", "D"]
    patterns = ["*H.DTA", "*Z.DTA", "*D.DTA"]

    # Path.glob yields a generator of Path objects matching the pattern
    for comp, pat in zip(component, patterns):
        target_files = list(data_dir.glob(pat))
    
        if not target_files:
            print(f"No files found matching pattern in {data_dir.resolve()}")
        else:
            print(f"Found {len(target_files)} files to process.")
            #df = ut.parse_ttb_dta_files(target_files, comp)
            log_filename = Path(OUT_FOLDER / f"log_{comp}_parsing_errors.txt")
            df = ut.parse_ttb_dta_files(target_files, comp, log_filename)

            
            print("\nParsing Complete. DataFrame Summary:")
            #print(final_df.info())
            
            df["Data_source"] = "DTA_files"
            all_tables.append(df)


df_year = all_tables[0].copy()
df_year["Z"] = all_tables[1]["Z"]
df_year["D"] = all_tables[2]["D"]

# Time management: UTC0 and UTC-3
# The module already outputs absolute UTC0, so we just derive the local representation from it:
df_year["Datetime_UTC-3"] = df_year["Datetime_UTC0"].dt.tz_convert('Etc/GMT+3')


ts = pd.Timestamp(df_year.iat[0, 0])
year = ts.year

# Save table
order = ["Datetime_UTC0", "Datetime_UTC-3", 
         "H", "Z", "D", 
         #"DOY_UTC0", "DOY_UTC-3", 
         #"Hours_in_day_UTC0", "Hours_in_day_UTC-3",
         "Data_source"]
df_year = df_year[order]
df_year.to_csv(OUT_FOLDER / f"dta_ttb_{year}.csv", index=False, na_rep=np.nan)
        