# -*- coding: utf-8 -*-
"""
Created on Sat Aug 30 11:55:37 2025

@author: raiss
"""

import pandas as pd
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from io import StringIO


# 1. Force resolve the absolute path to this utility script file first
CURRENT_FILE_PATH = Path(__file__).resolve()

# 2. Step back out of the modules/ directory to find your core 'code/' directory level
CODE_ROOT = CURRENT_FILE_PATH.parent

import module_utils as ut

# 3. Derive the absolute repository workspace root directory location
PROJECT_HOME = CODE_ROOT.parent

# Data folders
EXTRACTED_DATA_DIFF = PROJECT_HOME / "data" / "extracted_data" / "n640913" / "diffs"
EXTRACTED_DATA = PROJECT_HOME / "data" / "extracted_data" / "n640913" / "30min"

BASELINE_FOLDER = PROJECT_HOME / "data" / "formatted_baselines"
BASELINE_COEFFS_FOLDER = PROJECT_HOME / "output" / "plot_fit_baselines"

SCALEV_FOLDER = PROJECT_HOME / "data" / "formatted_scale_values"
SCALEV_COEFFS_FOLDER = PROJECT_HOME / "output" / "plot_fit_scale_values"

ttb_folder = PROJECT_HOME / "data" / "formatted_dta_data"

# Output
output_folder = PROJECT_HOME / "output" / "early_result_data_extraction"
output_folder.mkdir(parents=True, exist_ok=True)



#%% Process Extracted data 
"""
descricao das linhas
base0: linha de base H
curve0: H
curve1: D
curve2: ta pegando Z e a outra linha de base para 1964-09-13

descricao do arquivo curve0base0.txt em diffs
- altura da curva de medicao (em pixels)
- média da posicao linha do pixel da baseline, 
- posicao coluna da curva de medicao (pixels), que é a msm posicao coluna para linha de base
- distancia em mm entre a curva e a media da linha da linha de basel
"""

### --- DISTANCES FROM MEASUREMENT TO BASELINE IN MM


### Source: diffs folder
diff_files =  ut.list_files_in_folder(Path(EXTRACTED_DATA_DIFF))
diff_f = diff_files[1]
df_ext_diffs = ut.format_extracted_data(diff_f, Path(EXTRACTED_DATA_DIFF))
curve_row = df_ext_diffs["Curve_row_px"].to_numpy()
bl_row = df_ext_diffs["Mean_baseline_row_px"].to_numpy()
bl_curve_col = df_ext_diffs["Mean_baseline_Curve_col_px"].to_numpy()
height_mm = df_ext_diffs["Dist_Curve_Mean_baseline_mm"].to_numpy()
## Build the plot
ut.plot_one_scatter(df_ext_diffs, 
                    "Mean_baseline_Curve_col_px", 
               "Curve_row_px", 
               "Px", 
               output_folder/"fig_H_comp_px_diffs_folder.png")




### Source: 30min diffs folder
files =  ut.list_files_in_folder(Path(EXTRACTED_DATA))
file = files[0]
df_ext =  pd.read_csv(Path(EXTRACTED_DATA)/ file, 
                      names=['Dist_mm', 'Column_Pixel_Position'])

# Find 1h marks
df_1h = df_ext.iloc[::2]
#df_1h = df.iloc[1::2]
#h = df_1h["Dist_mm"]
horig = df_ext["Dist_mm"]
horig.loc[len(horig)] = -35.2   #nao lembro pq disso
h = horig




#%% TTB data
date = "1964-09-13"
timezone = "Datetime_UTC-3"
#timezone = "Datetime_UTC0"
ttb_files = ut.list_files_in_folder(Path(ttb_folder), ".csv")
ttb_hmv = pd.read_csv(ttb_folder/ttb_files[0]).dropna()
ttb_hmv["Datetime_UTC0"] = pd.to_datetime(ttb_hmv["Datetime_UTC0"])
ttb_hmv["Datetime_UTC-3"] = pd.to_datetime(ttb_hmv["Datetime_UTC-3"])
ttb_testday = ttb_hmv[ttb_hmv[timezone].dt.date == pd.to_datetime(date).date()]


#%% Get time series for test
##Decimal year considering 1h intervals for test day
day_time = []
start_date = datetime(1964, 9, 13, 0, 0, 0)
end_date = datetime(1964, 9, 14, 0, 0, 0)
current_date = start_date
t_range = 1
#t_range = 0.5
while current_date < end_date:
    day_time.append(current_date)
    current_date += timedelta(hours=t_range)

###Create dataframe for test
df_time = pd.DataFrame(day_time, columns=['Time'])
df_time["Time"] = pd.to_datetime(df_time["Time"])
df_time["Decimal_year"] = ut.calculate_decimal_year(df_time["Time"])


#%% Fit Baselines
baseline_files = ut.list_files_in_folder(Path(BASELINE_FOLDER))
bl_coeffs, year = ut.process_baseline_fit(baseline_files, 
                                          Path(BASELINE_FOLDER), 
                                          Path(BASELINE_COEFFS_FOLDER), False)


#%% Fit Scale values
scale_files = ut.list_files_in_folder(Path(SCALEV_FOLDER))
sv_coeffs = ut.process_scale_values_fit(scale_files, 
                                        SCALEV_FOLDER, 
                                        SCALEV_COEFFS_FOLDER, False)

#%% Magnetograma H eqs caption
#Scale value for H following TTB 1964 magnetogram metadata and formula:
# H = Baseline + Scale_value * distance_mm
# Scale_value = S0 + (DeltaD * S0) + a * n
# S0: valor tabelado em 3.138
# (DeltaD * S0): tabelado em -0.0173
# a: valor tabelado em 0.00122
S0 = 3.138
DeltaD_S0 = -0.0173
a = 0.00122
sh = []
for i in h:
    var = S0 + DeltaD_S0 + a * i
    sh.append(var)


#%% Time series Baseline
# following y = ax +b 
#blh = 2.06267 * t + 24170.3, where t is time for Sep-Oct data
#blh = -30.473 * t + 88095.5, where t is time for all year data
blh = []
for t in df_time["Decimal_year"]:
    value = ( bl_coeffs[0,0] * t) + bl_coeffs[0,1] 
    blh.append(value)

df_time["H_baseline_values"] = blh


#%% Time series Scale value
# following y = ax +b 
#sh = 0.177097 * t - 344.807, #where t is time for Sep-Oct data
#sh = 0.0132377 * t - 22.8773, #where t is time for all year data
sh = []
for t in df_time["Decimal_year"]:
    value = (sv_coeffs[0,0] * t) + sv_coeffs[0,1] 
    sh.append(value)

df_time["H_scale_values"] = sh

#%% Candidate
# hmv = bhl + sh * h
hmv = []
for i,j,k in zip(blh, sh, h):
    res = i + (j * k)
    hmv.append(res)

df_time["H"] = hmv
#ut.scatterplot(df_time, "Time", "H", "Test_H", output_folder/"fig_H_prelim_result_HMV_13_09_1964.png") 

#%% Plot
comp = "H"
x_data = ttb_testday[timezone]
y1_data = ttb_testday[comp]
y2_data = df_time[comp]

savepath = output_folder / f"fig_{comp}_{date}_{timezone}_comparison.png",
ut.plot_two_scatter(x_data, y1_data, y2_data, 
                     "Time (datetime)", 
                     "TTB (nT)", 
                     "Predicted (nT)", 
                     f"TTB at {date} in {timezone}: H component",
                     savepath,
                     False)


