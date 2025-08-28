#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 25 10:49:35 2025
Process WDC data

@author: raissamb
"""

from pathlib import Path
import pandas as pd
import module_utils as ut
from datetime import datetime
import numpy as np

# Paths and files
data_folder = Path("../data/raw_data/ttb_data_wdcsite_1957-1999/csv_format/")
output = Path("../output/data/wdc_hmv_tables/")

data_list = []
data_list = ut.list_files_in_folder(data_list, data_folder)
y1964 = data_list[37:49]

dfs = []
for item in y1964 :
    df1 = pd.read_csv(data_folder/item, skiprows=5)
    df1["Data_source"] = "WDC"
    df1["datetime"] = pd.to_datetime(df1["datetime"])
    dfs.append(df1)
    
concat = pd.concat(dfs)
concat.info()
year = concat["datetime"].dt.year.iat[0]

concat["DOY"] = concat["datetime"].dt.dayofyear
concat["Hours_in_day"] = concat["datetime"].dt.hour
concat["Hours_in_year"] = list(range(1, len(concat) + 1))
concat = concat.replace({99999: np.nan})
concat.rename(columns={'datetime': 'Datetime_UTC0'}, inplace=True)

order = ["Datetime_UTC0", "DOY", "H", "D", "Z", "F", "Hours_in_day", "Hours_in_year", "Data_source"]
final = concat[order]

ut.save_formatted_file(f"wdc_ttb_{year}.csv", final, output)
