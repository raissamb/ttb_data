import pandas as pd
from pathlib import Path
import numpy as np
import module_utils as ut
import matplotlib.pyplot as plt

input_folder = Path("../data/metadata_yearbooks/")
output_folder = Path("../output/baselines_scale_values/")


# Get all files in directory
files = []
files = ut.list_files_in_folder(files, input_folder)
baselines = files[0:3]
scale_values = files[3:7]

### BASELINES FOR 1964 SEPT-DECEMBER
dfs_baselines = []
for item in baselines:
    df = pd.read_csv(input_folder/item)
    df = df.dropna()
    df["date"] = pd.to_datetime(df["date"], format='%d-%m-%Y')
    df["date_baseline_means"] = pd.to_datetime(df["date_baseline_means"], format='%d-%m-%Y')
    df["decimal_year"] = df["date_baseline_means"].apply(ut.to_decimal_year)
    dfs_baselines.append(df)


year = df["date_baseline_means"].dt.year.iat[0]


# Fit D
daux = dfs_baselines[0]
daux["baseline_means_dd"] = daux["baseline_means_degree"] + daux["baseline_means_minute"]
dx = daux["decimal_year"]
dy = daux["baseline_means_dd"]
#dcoeffs, dfit = ut.fit_data(dx, dy, 1)
#print(f"Fit function for D data: {dfit}")
dfigname = f"../output/baselines_scale_values/{year}_D_baseline.png"
ut.plot_fit(dx, dy, 1,"D", "Baseline", "dd", dfigname, 1, 1)

# Fit H
haux = dfs_baselines[1]
hx = haux["decimal_year"]
hy = haux["baseline_means_nT"]
hfigname = f"../output/baselines_scale_values/{year}_H_baseline.png"
ut.plot_fit(hx, hy, 1, "H", "Baseline", "nT", hfigname, 25, 25)

# Fit Z
zaux = dfs_baselines[2].drop(dfs_baselines[2].loc[48:54].index) 
#zaux = zzaux.drop(zzaux.loc[48:54].index) 
zx = zaux["decimal_year"]
zy = zaux["baseline_means_nT"]
zcoeffs, zfit = ut.fit_data(zx, zy, 1)
#print(f"Fit function for Z data: {zfit}")
zfigname = f"../output/baselines_scale_values/{year}_Z_baseline.png"
ut.plot_fit(zx, zy, 1,"Z", "Baseline", "nT", zfigname, 75, 50)


### SCALE VALUES FOR 1964 SEPT-DECEMBER
dfs_scale = []
for item in scale_values:
    df = pd.read_csv(input_folder/item)
    df = df.dropna()
    df["date"] = pd.to_datetime(df["date"], format='%d-%m-%Y')
    df["decimal_year"] = df["date"].apply(ut.to_decimal_year)
    dfs_scale.append(df)



# Fit D
daux_scale = dfs_scale[0]
dx_scale = daux_scale["decimal_year"]
dy_scale = daux_scale["scale_value(min/mm)"]
dfigname_scale = f"../output/baselines_scale_values/{year}_D_scale.png"
ut.plot_fit(dx_scale, dy_scale, 1, "D", "Scale Values", "min/mm", dfigname_scale, 0.04, 0.04)

# Fit H
haux_scale = dfs_scale[1]
hx_scale = haux_scale["decimal_year"]
hy_scale = haux_scale["scale_value(min/mm)"]
hfigname_scale = f"../output/baselines_scale_values/{year}_H_scale.png"
ut.plot_fit(hx_scale, hy_scale, 1, "H", "Scale Values", "min/mm", hfigname_scale, 0.05, 0.05)

# Fit Z
zaux_scale = dfs_scale[2]
zx_scale = zaux_scale["decimal_year"]
zy_scale = zaux_scale["scale_value(nT/mm)"]
zfigname_scale = f"../output/baselines_scale_values/{year}_Z_scale.png"
ut.plot_fit(zx_scale, zy_scale, 1, "Z", "Scale Values", "nT/mm", zfigname_scale, 1, 1)


