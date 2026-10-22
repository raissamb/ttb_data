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
EXTRACTED_DATA = PROJECT_HOME / "data" / "formatted_extracted_data"
BASELINE_FOLDER = PROJECT_HOME / "data" / "formatted_baselines"
BASELINE_COEFFS_FOLDER = PROJECT_HOME / "output" / "plot_fit_baselines"
SCALEV_FOLDER = PROJECT_HOME / "data" / "formatted_scale_values"
SCALEV_COEFFS_FOLDER = PROJECT_HOME / "output" / "plot_fit_scale_values"
TTB_FOLDER = PROJECT_HOME / "data" / "formatted_dta_data"
IAGA_FOLDER = PROJECT_HOME / "data" / "formatted_iaga_data"

# Output
output_folder = PROJECT_HOME / "output" / "early_result_data_extraction"
output_folder.mkdir(parents=True, exist_ok=True)




def plot_component_comparisons(date_axis, yvar1: np.ndarray, yvar2: np.ndarray, yvar3: np.ndarray,
                               x_col: str,  y_col: str, title: str, 
    save_path: str|Path, show: bool = False) -> None:
    """
    Generates a scatter plot from two dataframe columns and saves it to disk.
    """
    
    # 1. Create the figure context
    plt.figure(figsize=(10, 6))
    
    # 2. Plot the data
    plt.plot(date_axis, yvar1, label = "TTB", linestyle="-")
    plt.plot(date_axis, yvar2, label = "Candiate_fit", linestyle="--")
    plt.plot(date_axis, yvar3, label = "Candidate_eq", linestyle="-.")
    plt.xticks(rotation=45, ha='right')
    
    # 3. Add Labels and Title
    plt.title(title, fontsize=14)
    plt.xlabel(x_col, fontsize=12)
    plt.ylabel(y_col, fontsize=12)
    
    # 4. Add a grid
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()
    
    # 5. Save the figure
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300) 
    
    # 6. Handling Display vs. Memory
    if show:
        plt.show()
    else:
        plt.close()

    print(f"Plot saved successfully to: {save_path}")



# Read extracted data 
#files = ut.list_files_in_folder(EXTRACTED_DATA)
time_marking_file = EXTRACTED_DATA / "combined_H_time_markings.csv"
pixel_coords_file = EXTRACTED_DATA / "pixels_coords_H.csv"


# Set target day and create subsets dfs
target_day = "1964-09-13"
folder_id = "n640913"
df1 = pd.read_csv(pixel_coords_file)
df2 = pd.read_csv(time_marking_file)

df_px = df1[df1['folder_id'] == folder_id]
df_tmark_lt = df2[df2['date_local_utc3']==target_day]
df_tmark_lt = df_tmark_lt.sort_values(by=['datetime_local_utc3'])
df_tmark_utc0 = df2[df2['date_utc']==target_day]
df_tmark_utc0 = df_tmark_utc0.sort_values(by=['datetime_utc'])

# Plot pixel coords
#ut.plot_pixel_coordinates(df_px, "column", "row_trace", "Pixel coordinates for H in {target_day}", f"{output_folder}/pixel_coords_H_{target_day}.png")

 
# Build time series for test day
##Decimal year considering 1h intervals for test day
#Flexibility: If you decide to test that 30-minute interval again (t_range = 0.5), 
# you simply change the arguments to periods=48, freq="30min".

# 1. Generate 24 hourly timestamps starting from midnight on the target date
time_series = pd.date_range(start=target_day, periods=24, freq="h")

# 2. Construct the DataFrame directly
df_time = pd.DataFrame({'Time': time_series})

# 3. Apply your existing vectorized function
df_time["Decimal_year"] = ut.calculate_decimal_year(df_time["Time"])



## Fit Baseline equations: working
baseline_files = ut.list_files_in_folder(BASELINE_FOLDER)
baseline_eqs = ut.fit_metadata_equations(baseline_files, BASELINE_FOLDER, is_baseline=True)

## Fit Scale Value equations
scale_files = ut.list_files_in_folder(SCALEV_FOLDER)
scale_eqs = ut.fit_metadata_equations(scale_files, SCALEV_FOLDER, is_baseline=False)

# 1. Ensure the 'H' equations were successfully generated
if 'H' in baseline_eqs and 'H' in scale_eqs:
    
    # 2. Pass the entire Decimal_year column into the equations
    df_time["Baseline_H_fit"] = baseline_eqs["H"](df_time["Decimal_year"])
    df_time["ScaleValue_H_fit"] = scale_eqs["H"](df_time["Decimal_year"])
    
else:
    print("Error: 'H' component equations were not found in the metadata.")




# Delete one row from extracted data
t1 = df_tmark_lt.drop([74])
#t1 = df_tmark_lt.drop([75])
h = t1["delta_height_mm"].to_numpy()
df_time["Height_mm"] = h


## Scale value using equation behind magnetogram
# H = Baseline + (ScaleValue * n), n = height
# ScaleValue = S0 + (DeltaD * S0) + (a * n)

# S0: valor tabelado em 3.138
# (DeltaD * S0): tabelado em -0.0173
# a: valor tabelado em 0.00122
S0 = 3.138
DeltaD_S0 = -0.0173
a = 0.00122

df_time["ScaleValue_H_eq"] = (S0 + (DeltaD_S0) + (a * h))
df_time["Candidate_H_from_fit"] = df_time["Baseline_H_fit"] + (df_time["ScaleValue_H_fit"] * h)
df_time["Candidate_H_from_eq"] = df_time["Baseline_H_fit"] + (df_time["ScaleValue_H_eq"] * h)


# #%% Get time series for test
# date_n = "1964-09-13"
# timezone = "Datetime_UTC-3"


#%% Read TTB data: working
#timezone = "Datetime_UTC0"
timezone = "Datetime_UTC-3"
ttb_files = ut.list_files_in_folder(Path(TTB_FOLDER), ".csv")
ttb_hmv = pd.read_csv(TTB_FOLDER/ttb_files[0]).dropna()
ttb_hmv["Datetime_UTC0"] = pd.to_datetime(ttb_hmv["Datetime_UTC0"])
ttb_hmv["Datetime_UTC-3"] = pd.to_datetime(ttb_hmv["Datetime_UTC-3"])
ttb_testday = ttb_hmv[ttb_hmv[timezone].dt.date == pd.to_datetime(target_day).date()]
ttb_h = ttb_testday["H"].to_numpy()



# build time df for comparison
df_time["TTB_H"] = ttb_h

date_axis = df_time["Time"]
h_pred_fit = df_time["Candidate_H_from_fit"].to_numpy()
h_pred_eq = df_time["Candidate_H_from_eq"].to_numpy()




plot_component_comparisons(date_axis, 
                           ttb_h,
                           h_pred_fit, 
                           h_pred_eq,
                           "Datetime (Y-M-D-H)",  
                           "nT", 
                           f"Comparison of TTB H and candidates for {target_day}", 
                           f"{output_folder}/comparison_H.png")












### Comment V1 dado 21/10/2026
# # remove rows
# df_time2 = df_time.drop([6,7,8,9])
# t1 = df_tmark_lt.drop([65,66])
# h = t1["delta_height_mm"].to_numpy()
# df_time2["Height_mm"] = h


# ## Scale value using equation behind magnetogram
# # H = Baseline + (ScaleValue * n), n = height
# # ScaleValue = S0 + (DeltaD * S0) + (a * n)

# # S0: valor tabelado em 3.138
# # (DeltaD * S0): tabelado em -0.0173
# # a: valor tabelado em 0.00122
# S0 = 3.138
# DeltaD_S0 = -0.0173
# a = 0.00122

# df_time2["ScaleValue_H_eq"] = (S0 + (DeltaD_S0) + (a * h))

# df_time2["Candidate_H_from_fit"] = df_time2["Baseline_H_fit"] + (df_time2["ScaleValue_H_fit"] * h)
# df_time2["Candidate_H_from_eq"] = df_time2["Baseline_H_fit"] + (df_time2["ScaleValue_H_eq"] * h)


# # #%% Get time series for test
# # date_n = "1964-09-13"
# # timezone = "Datetime_UTC-3"


# #%% Read TTB data: working
# #timezone = "Datetime_UTC0"
# timezone = "Datetime_UTC-3"
# ttb_files = ut.list_files_in_folder(Path(TTB_FOLDER), ".csv")
# ttb_hmv = pd.read_csv(TTB_FOLDER/ttb_files[0]).dropna()
# ttb_hmv["Datetime_UTC0"] = pd.to_datetime(ttb_hmv["Datetime_UTC0"])
# ttb_hmv["Datetime_UTC-3"] = pd.to_datetime(ttb_hmv["Datetime_UTC-3"])
# ttb_testday = ttb_hmv[ttb_hmv[timezone].dt.date == pd.to_datetime(target_day).date()]


# t2 = ttb_testday.drop([6150, 6151, 6152, 6153])
# ttb_h = t2["H"].to_numpy()

# # build time df for comparison
# df_time2["TTB_H"] = ttb_h

# date_axis = df_time2["Time"]
# h_pred_fit = df_time2["Candidate_H_from_fit"].to_numpy()
# h_pred_eq = df_time2["Candidate_H_from_eq"]





# plot_component_comparisons(date_axis, 
#                            ttb_h,
#                            h_pred_fit, 
#                            h_pred_eq,
#                            "Datetime (Y-M-D-H)",  
#                            "nT", 
#                            f"Comparison of TTB H and candidates for {target_day}", 
#                            f"{output_folder}/comparison_H.png")
