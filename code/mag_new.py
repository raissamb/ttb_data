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
EXTRACTED_DATA_KN = PROJECT_HOME / "data" / "formatted_extracted_data_keanu"

#EXTRACTED_DATA_DIFF_RMB = PROJECT_HOME / "data" / "raw_data" / "extracted_data_raissa"


BASELINE_FOLDER = PROJECT_HOME / "data" / "formatted_baselines"
BASELINE_COEFFS_FOLDER = PROJECT_HOME / "output" / "plot_fit_baselines"

SCALEV_FOLDER = PROJECT_HOME / "data" / "formatted_scale_values"
SCALEV_COEFFS_FOLDER = PROJECT_HOME / "output" / "plot_fit_scale_values"

ttb_folder = PROJECT_HOME / "data" / "formatted_dta_data"

# Output
output_folder = PROJECT_HOME / "output" / "early_result_data_extraction"
output_folder.mkdir(parents=True, exist_ok=True)



#%% Get time series for test
date_n = "1964-09-13"
timezone = "Datetime_UTC-3"

##Decimal year considering 1h intervals for test day
#Flexibility: If you decide to test that 30-minute interval again (t_range = 0.5), 
# you simply change the arguments to periods=48, freq="30min".

# 1. Generate 24 hourly timestamps starting from midnight on the target date
time_series = pd.date_range(start="1964-09-13", periods=24, freq="h")

# 2. Construct the DataFrame directly
df_time = pd.DataFrame({'Time': time_series})

# 3. Apply your existing vectorized function
df_time["Decimal_year"] = ut.calculate_decimal_year(df_time["Time"])



#%% Read TTB data: working
#timezone = "Datetime_UTC0"
ttb_files = ut.list_files_in_folder(Path(ttb_folder), ".csv")
ttb_hmv = pd.read_csv(ttb_folder/ttb_files[0]).dropna()
ttb_hmv["Datetime_UTC0"] = pd.to_datetime(ttb_hmv["Datetime_UTC0"])
ttb_hmv["Datetime_UTC-3"] = pd.to_datetime(ttb_hmv["Datetime_UTC-3"])
ttb_testday = ttb_hmv[ttb_hmv[timezone].dt.date == pd.to_datetime(date_n).date()]



## Fit Baseline equations: working
baseline_files = ut.list_files_in_folder(BASELINE_FOLDER)
baseline_eqs = ut.fit_metadata_equations(baseline_files, BASELINE_FOLDER, is_baseline=True)

## Fit Scale Value equations
scale_files = ut.list_files_in_folder(SCALEV_FOLDER)
scale_eqs = ut.fit_metadata_equations(scale_files, SCALEV_FOLDER, is_baseline=False)

# 1. Ensure the 'H' equations were successfully generated
if 'H' in baseline_eqs and 'H' in scale_eqs:
    
    # 2. Pass the entire Decimal_year column into the equations
    df_time["Baseline_H"] = baseline_eqs["H"](df_time["Decimal_year"])
    df_time["ScaleValue_H"] = scale_eqs["H"](df_time["Decimal_year"])
    
else:
    print("Error: 'H' component equations were not found in the metadata.")



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
diffs_kn = pd.read_csv(EXTRACTED_DATA_KN/"keanu_H_ttb_1964.csv")
folder1 = "n640913"
folder2 = "n640912"
#df_kn = diffs_kn[(diffs_kn["folder_id"] == folder1) | (diffs_kn["folder_id"] == folder2)]

df_kn = diffs_kn[(diffs_kn["folder_id"] == folder1)] 


### Source: 30min folder
df30min_kn = pd.read_csv(EXTRACTED_DATA_KN/"keanu_30min_H_1964.csv")
df30min_target = df30min_kn[df30min_kn["folder_id"] == folder1]

# find 1h mark for curve0: H
df30min_curve = df30min_target[["folder_id","Dist_mm_0", "Column_Px_0"]]
df30min_curve = df30min_curve.dropna()

df_1h = df30min_curve.iloc[::2]
height_mm = df_1h["Dist_mm_0"]




#%% Candidate component curve
# hmv = bhl + (sh * h)























