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

###--- Using ---
if __name__ == "__main__":
    # Define your data directory (defaults to current working directory '.' here)
    data_dir = Path(DATA_FOLDER )
    
    component = ["H", "Z", "D"]
    patterns = ["*H.DTA", "*Z.DTA", "*D.DTA"]
    names = ["hmv_H_1964.csv", "hmv_Z_1964.csv", "hmv_D_1964.csv"]

    # Path.glob yields a generator of Path objects matching the pattern
    for comp, pat, name in zip(component, patterns, names):
        target_files = list(data_dir.glob(pat))
    
        if not target_files:
            print(f"No files found matching pattern in {data_dir.resolve()}")
        else:
            print(f"Found {len(target_files)} files to process.")
            final_df = ut.parse_ttb_dta_files(target_files, comp)
            
            print("\nParsing Complete. DataFrame Summary:")
            print(final_df.info())
            
            final_df["Data_source"] = "DTA_files"
            final_df.to_csv(OUT_FOLDER / name, index=False)



