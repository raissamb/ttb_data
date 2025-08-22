#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 12 16:11:39 2025

@author: raissamb
"""

from pathlib import Path
import pandas as pd
import module_utils as ut
import matplotlib.pyplot as plt
from datetime import datetime

# Paths and files
data_folder = Path("../output/hmv_tables/")
surface_folder = Path("../output/plot_surface_hmv/")
histogram_folder = Path("../output/plot_histograms_hmv/")
day_folder = Path("../output/plot_hmv_day/")

data_list = []
data_list = ut.list_files_in_folder(data_list, data_folder)

data_file = data_list[0]
df = pd.read_csv(data_folder/data_file)
df["Datetime"] = pd.to_datetime(df["Datetime"], format="%Y-%m-%d %H:%M:%S")

## Plot surfaces
# ut.plot_hmv_surfaces("H", data_file, data_folder, surface_folder)
# ut.plot_hmv_surfaces("D", data_file, data_folder, surface_folder)
# ut.plot_hmv_surfaces("Z", data_file, data_folder, surface_folder)

## Plot histogram
#ut.plot_histogram(df["H"], "H", 1964, histogram_folder, "H1964.png")
#ut.plot_histogram(df["D"], "D", 1964, histogram_folder, "D1964.png")
#ut.plot_histogram(df["Z"], "Z", 1964, histogram_folder, "Z1964.png")

# Plot time series for a single day
doy = 2
comp = "H"
unit = "nT"
ut.plot_scatter_hmv_day(df, doy, comp, unit, day_folder)


