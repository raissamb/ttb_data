import pandas as pd
from pathlib import Path
import numpy as np
import module_utils as ut
import matplotlib.pyplot as plt

input_folder = Path("../output/proc_data/baselines_scale_values_tables/")
output_folder = Path("../output/plot_baselines_scale_values/")

# COLOCAR EM FUNCOES DEPOIS AS COISAS AQUI

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
    df["Date"] = pd.to_datetime(df["Date"])
    df["Date_baseline_means"] = pd.to_datetime(df["Date_baseline_means"])
    #df.info()
    
    # Get year and component
    year = df["Date_baseline_means"].dt.year.iat[0]
    
    # result
    dfs_baselines.append(df)


#### FIT FOR BASELINES SEP-OCT 1964
# Fit H 
h = dfs_baselines[1]
haux = h[h["Month"].isin([9, 10])]
hx = haux["Decimal_year"]
hy = haux["Baseline_means_nT"]
hcoeff = np.polyfit(hx, hy, 1)
print("H fit: ", np.poly1d(hcoeff))
hfigname = f"../output/plot_baselines_scale_values/Sep_Oct_{year}_H_fit_baseline.png"
ut.plot_fit(hx, hy, 1, "H", "Baseline", "nT", hfigname, 25, 25, "Sep-Oct data")


# Fit Z
z = dfs_baselines[2]
zaux = z[z["Month"].isin([9, 10])]
zx = zaux["Decimal_year"]
zy = zaux["Baseline_means_nT"]
zcoeff = np.polyfit(zx, zy, 1)
print("Z fit: ", np.poly1d(zcoeff))
zfigname = f"../output/plot_baselines_scale_values/Sep_Oct_{year}_Z_fit_baseline.png"
ut.plot_fit(zx, zy, 1,"Z", "Baseline", "nT", zfigname, 75, 50, "Sep-Oct data")


# Fit D
d = dfs_baselines[0]
daux = d[d["Month"].isin([9, 10])]
dx = daux["Decimal_year"]
dy = daux["Baseline_means_dd"]
dcoeff = np.polyfit(dx, dy, 1)
print("D fit: ", np.poly1d(dcoeff))
dfigname = f"../output/plot_baselines_scale_values/Sep_Oct_{year}_D_fit_baseline.png"
ut.plot_fit(dx, dy, 1,"D", "Baseline", "dd", dfigname, 1, 1, "Sep-Oct data")


### FIT FOR SCALE VALUES FOR 1964 SEP-OCT
dfs_scale = []
for item in scale_values:
    df = pd.read_csv(input_folder/item)
    df = df.dropna()
    df["Date"] = pd.to_datetime(df["Date"])
    #df.info()
    
    # Get year and component
    year = df["Date"].dt.year.iat[0]
    
    # result
    dfs_scale.append(df)


# Fit H
h2 = dfs_scale[1]
haux2 = h2[h2["Month"].isin([9, 10])]
hx2 = haux2["Decimal_year"]
hy2 = haux2["Scale_value(min/mm)"]
hcoeff2 = np.polyfit(hx2, hy2, 1)
print("H scale value fit: ", np.poly1d(hcoeff2))
hfigname = f"../output/plot_baselines_scale_values/Sep_Oct_{year}_H_fit_scale_values.png"
ut.plot_fit(hx2, hy2, 1, "H", "Scale Value", "min/mm", hfigname, 25, 25, "Sep-Oct data")

# Fit z
z2 = dfs_scale[2]
zaux2 = z2[z2["Month"].isin([9, 10])]
zx2 = zaux2["Decimal_year"]
zy2 = zaux2["Scale_value(nT/mm)"]
zcoeff2 = np.polyfit(zx2, zy2, 1)
print("Z scale value fit: ", np.poly1d(zcoeff2))
zfigname = f"../output/plot_baselines_scale_values/Sep_Oct_{year}_Z_fit_scale_values.png"
ut.plot_fit(zx2, zy2, 1, "Z", "Scale Value", "nT/mm", zfigname, 1, 1, "Sep-Oct data")

# Fit D
d2 = dfs_scale[0]
daux2 = d2[d2["Month"].isin([9, 10])]
dx2 = daux2["Decimal_year"]
dy2 = daux2["Scale_value(min/mm)"]
dcoeff2 = np.polyfit(dx2, dy2, 1)
print("D scale value fit: ", np.poly1d(dcoeff2))
dfigname = f"../output/plot_baselines_scale_values/Sep_Oct_{year}_D_fit_scale_values.png"
ut.plot_fit(dx2, dy2, 1, "D", "Scale Value", "min/mm", dfigname, 1, 1, "Sep-Oct data")







