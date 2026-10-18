# -*- coding: utf-8 -*-
"""
Created on Wed Aug 20 19:16:05 2025

@author: raiss
"""

from datetime import datetime
#import calendar
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
from pathlib import Path
from typing import Optional
from datetime import date, timedelta
import io
from io import StringIO
import logging


############################### FILES

#%% new
def list_files_in_folder(folder_path: str | Path, extension: Optional[str] = None) -> list[str]:
    """
    Lists files in a directory, optionally filtering by extension.
    
    Parameters
    ----------
    folder_path : str
        The path to the folder to search.
    extension : str, optional
        The file extension to look for (e.g., "csv" or ".txt").
        If None, lists all files.
        
    Returns
    -------
    List[str]
        A list of filenames found.
    """
    folder = Path(folder_path)
    
    # Safety check: does the folder exist?
    if not folder.exists():
        print(f"Error: The folder '{folder_path}' does not exist.")
        return []

    # 1. Determine the search pattern
    if extension:
        # Ensure extension starts with a dot (e.g., "csv" -> ".csv")
        if not extension.startswith("."):
            extension = f".{extension}"
        pattern = f"*{extension}"
    else:
        # If no extension provided, look for everything
        pattern = "*"

    # 2. Search and filter
    # .glob() finds matches, .is_file() ensures we don't pick up sub-folders
    files = [f.name for f in folder.glob(pattern) if f.is_file()]
    
    return sorted(files)


def apply_validity_threshold(df: pd.DataFrame, component: str, thresholds: dict = None) -> pd.DataFrame:
    """
    Filters out non-physical outliers by replacing them with NaN based on acceptable min/max bounds.
    """
    if thresholds is None:
        # Default physical thresholds for Tatuoca observatory
        thresholds = {
            "H": (20000, 35000),
            "Z": (5000, 10000),
            "D": (-45, 0)
        }
        
    if component in thresholds:
        min_val, max_val = thresholds[component]
        
        # Identify outliers and replace with NaN
        outliers_mask = (df[component] < min_val) | (df[component] > max_val)
        df.loc[outliers_mask, component] = np.nan
        
    return df


def parse_ttb_dta_files(file_list: list, 
                        component: str, 
                        log_filename: str | Path = "parsing_errors.txt",
                        thresholds: dict = None) -> pd.DataFrame:
    """
    Parses a list of monthly TTB geomagnetic data files into a single, continuous DataFrame
    and records formatting anomalies to a log file.
    
    Parameters:
    file_list (iterable of Path): List or generator of pathlib.Path objects.
    component: Name of the magnetic component to be parsed.
    log_filename: Destination path for the text log file.
    
    Returns:
    pd.DataFrame: Cleaned dataframe with 'Datetime_UTC0' and the target component column.
    """
    # 1. Configure the Logger
    log_path = Path(log_filename)
    logger = logging.getLogger("ttb_parser")
    logger.setLevel(logging.WARNING)
    logger.handlers.clear() # Clear existing handlers to prevent duplicate logging if run repeatedly

    # Create handlers: one for the file, one for the terminal console
    file_handler = logging.FileHandler(log_path, mode='w', encoding='utf-8')
    console_handler = logging.StreamHandler()

    # Set clear formatting for log entries
    formatter = logging.Formatter('%(asctime)s - [%(levelname)s] - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.info(f"Starting parsing process for component: {component}")
    
    all_records = []
    
    for file_path in sorted(file_list):
        filename = file_path.name  
        
        with file_path.open('r') as f:
            lines = f.readlines()
            
        # STEP 1: Pre-parse and validate the dates for typos (e.g., the Feb 29th duplicate)
        parsed_dates = []
        for line_idx, line in enumerate(lines, start=1):
            line = line.strip()
            if not line:
                parsed_dates.append(None)
                continue
                
            header = line[:10]
            try:
                dt = datetime(int(f"19{header[3:5]}"), int(header[5:7]), int(header[7:9]))
                parsed_dates.append(dt)
            except ValueError:
                parsed_dates.append(None)
                logger.error(f"Invalid date format in {filename} at line {line_idx}: '{header}'.")

        # Typo Check: Look for pattern [Day A] -> [Day A + 2] -> [Day A + 2]
        for i in range(1, len(parsed_dates) - 1):
            if parsed_dates[i] and parsed_dates[i-1] and parsed_dates[i+1]:
                if parsed_dates[i] == parsed_dates[i+1] and (parsed_dates[i] - parsed_dates[i-1]).days == 2:
                    corrected_date = parsed_dates[i-1] + timedelta(days=1)
                    logger.warning(f"Typo auto-corrected in {filename} (Line {i+1}): Changed duplicate {parsed_dates[i].date()} to {corrected_date.date()}")
                    parsed_dates[i] = corrected_date

        # STEP 2: Extract hourly block using the validated dates
        for line_idx, (line, base_date) in enumerate(zip(lines, parsed_dates), start=1):
            line = line.strip()
            if not line or not base_date:
                continue
                
            data_block = line[10:]
            char_per_meas = 5
            
            for hour in range(24):
                val_str = data_block[hour * char_per_meas : (hour + 1) * char_per_meas].ljust(char_per_meas)
                record_datetime = base_date + timedelta(hours=hour)
                
                if '*' in val_str or val_str.strip() == '':
                    final_val = np.nan
                else:
                    try:
                        final_val = float(val_str)
                    except ValueError:
                        final_val = np.nan
                
                all_records.append({'Datetime_UTC0': record_datetime, component: final_val})
                    
    df = pd.DataFrame(all_records)
    
    if not df.empty:
        df["Datetime_UTC-3"] = df["Datetime_UTC0"].dt.tz_localize('Etc/GMT+3')
        df["Datetime_UTC0"] = df["Datetime_UTC-3"].dt.tz_convert('UTC')
        
        if component == "D":
            # Convert tenths of minutes to degrees, and apply negative sign 
            # to match the true physical Southern Hemisphere orientation (like TXT files)
            df["D"] = -((df["D"] / 10) / 60)
            
        df = df.sort_values('Datetime_UTC0').drop_duplicates(subset=['Datetime_UTC0'], keep='last')
        
        full_calendar = pd.date_range(start=df['Datetime_UTC0'].min(), end=df['Datetime_UTC0'].max(), freq='h')
        
        missing_hours = full_calendar.difference(df['Datetime_UTC0'])
        if not missing_hours.empty:
            logger.warning(f"Calendar check found {len(missing_hours)} genuinely missing hourly records. Filling gaps with NaNs.")
            
        df = df.set_index('Datetime_UTC0').reindex(full_calendar).rename_axis('Datetime_UTC0').reset_index()
        
        # --- NEW: Apply independent physical validity filter ---
        df = apply_validity_threshold(df, component, thresholds)

    logger.info(f"Parsing complete. Log saved to: {log_path.resolve()}")
    return df


def format_table_txt_data(data_folder, file):
    # Define exact character widths for each column:
    # 1. Information: 10 chars
    # 2. Type: 3 chars
    # 3. Code1: 3 chars
    # 4. Base_value: 4 chars
    # 5-28. 24 hourly values: exactly 4 chars each
    # 29. Variation_mean: 4 chars
    col_widths = [10, 3, 3, 4] + [4] * 24 + [4]
    
    # Read the text file using fixed-width parsing
    df = pd.read_fwf(data_folder / file, widths=col_widths, header=None)
    
    # Safely replace the 9999 numeric missing flags with NaN mathematically
    df = df.replace(9999, np.nan)

    # Assign logical column names based on the 29-column structure
    col_names = ['Information', 'Type', 'Code1', 'Base_value'] + \
                [f'Hour_{i:02d}' for i in range(1, 25)] + \
                ['Variation_mean']

    # Validate and apply columns
    if len(df.columns) == len(col_names):
        df.columns = col_names
    else:
        print(f"Expected {len(col_names)} columns, but found {len(df.columns)}.")
        
    # Replace and remove strings using Regex to strip any H, D, or Z letter safely
    df["Information"] = df["Information"].astype(str).str.replace('ttb', '19')
    df["Information"] = df["Information"].str.replace(r'[HDZ]', '', regex=True)
   
    # Add date time in YYYY-MM-DD format
    df["Year"] = df["Information"].str.slice(0,4)
    df["Month"] = df["Information"].str.slice(4,6)
    df["Day"] = df["Information"].str.slice(6,8)
    df["Date"] = pd.to_datetime(df[['Year', 'Month', 'Day']])

    # --- FIX: Typo Auto-Correction (Feb 27 -> Feb 29 -> Feb 29 becomes 27 -> 28 -> 29) ---
    # Use to_numpy(copy=True) to create a writable array instead of a read-only memory view
    dates = df["Date"].to_numpy(copy=True)
    
    for i in range(1, len(dates) - 1):
        if pd.notna(dates[i]) and pd.notna(dates[i-1]) and pd.notna(dates[i+1]):
            # If current day equals next day, and the gap from previous day is 2 days
            if dates[i] == dates[i+1] and (dates[i] - dates[i-1]).astype('timedelta64[D]') == np.timedelta64(2, 'D'):
                dates[i] = dates[i-1] + np.timedelta64(1, 'D')
                
    df["Date"] = dates
    
    return df


def create_hmv_from_txt_file(df: pd.DataFrame, component: str, output_dir: str | Path, thresholds: dict = None):
    df2 = df[["Date"]].copy()
    hours = [f'Hour_{i:02d}' for i in range(1, 25)]

    var = 0 # initialize variable 
    for item in hours:
        if component == "H":
            var = (df["Base_value"] * 100) + df[item]
        elif component == "Z":
            var = (df["Base_value"] * 100) + df[item]
        elif component == "D":
            var = df["Base_value"] + (0.1 * (df[item] / 60))
        df2[item] = var
    
    df_long = df2.melt(id_vars=['Date'], var_name='Hour_Col', value_name=component)
    df_long['Hour'] = df_long['Hour_Col'].str.extract(r"(\d+)").astype(int) - 1
    
    df_long['Date'] = pd.to_datetime(df_long['Date'])
    df_long['Datetime_Local_Naive'] = df_long['Date'] + pd.to_timedelta(df_long['Hour'], unit='h')
    df_long['Datetime'] = df_long['Datetime_Local_Naive'].dt.tz_localize('Etc/GMT+3').dt.tz_convert('UTC')
    
    df_final = df_long[['Datetime', component]].sort_values(by='Datetime').reset_index(drop=True)
    df_final['Datetime'] = df_final['Datetime'].dt.tz_localize(None)
    
    # Fill missing hourly gaps with NaNs against a continuous calendar
    df_final = df_final.drop_duplicates(subset=['Datetime'], keep='last')
    full_calendar = pd.date_range(start=df_final['Datetime'].min(), end=df_final['Datetime'].max(), freq='h')
    df_final = df_final.set_index('Datetime').reindex(full_calendar).rename_axis('Datetime').reset_index()

    # --- NEW: Apply independent physical validity filter ---
    df_final = apply_validity_threshold(df_final, component, thresholds)

    # Re-derive Local Time AFTER gap-filling so NaNs get proper timestamps
    df_final['Datetime_Local'] = df_final['Datetime'].dt.tz_localize('UTC').dt.tz_convert('Etc/GMT+3').dt.tz_localize(None)
    
    cols = ['Datetime', 'Datetime_Local', component]
    df_final = df_final[cols]
    
    return df_final












# def format_table_txt_data(data_folder, file):
#     with open(data_folder / file, "r", encoding="utf-8") as f:
#         raw_data = f.read()
        
#     # Detach the glued missing values
#     cleaned_data = raw_data.replace('9999', ' NaN ')

#     # Read the cleaned text into a pandas DataFrame using whitespace parsing
#     # FIX: Added 'r' before '\s+' to designate a raw string
#     df = pd.read_csv(io.StringIO(cleaned_data), sep=r'\s+', header=None, engine='python')

#     # Assign logical column names based on the 29-column structure
#     col_names = ['Information', 'Type', 'Code1', 'Base_value'] + \
#                 [f'Hour_{i:02d}' for i in range(1, 25)] + \
#                 ['Variation_mean']

#     # Validate and apply columns
#     if len(df.columns) == len(col_names):
#         df.columns = col_names
#     else:
#         print(f"Expected {len(col_names)} columns, but found {len(df.columns)}.")
        
    
#     # replace and remove strings
#     df["Information"] = df["Information"].str.replace('ttb', '19')
#     df["Information"] = df["Information"].str.replace('H', '')
   
#     # Add date time in YYYY-MM-DD format
#     df["Year"] = df["Information"].str.slice(0,4)
#     df["Month"] = df["Information"].str.slice(4,6)
#     df["Day"] = df["Information"].str.slice(6,8)
#     df["Date"] = pd.to_datetime(df[['Year', 'Month', 'Day']])
    

    
#     return df


# def create_hmv_from_txt_file(df: pd.DataFrame, component: str, output_dir: str | Path):
#     df2 = df[["Date"]].copy()
#     hours = [f'Hour_{i:02d}' for i in range(1, 25)]
    
#     # Get HMV
#     for item in hours:
#         var = df["Base_value"]*100 + df[item]
#         df2[item] = var
    
     
#     # Melt the dataframe from wide to long format
#     df_long = df2.melt(id_vars=['Date'], var_name='Hour_Col', value_name=component)
    
#     # Extract the hour number from the column name (e.g., "Hour_01" -> 1)
#     # Subtract 1 so that Hour_01 corresponds to 00:00, Hour_02 to 01:00, ..., Hour_24 to 23:00
#     df_long['Hour'] = df_long['Hour_Col'].str.extract("(\d+)").astype(int) - 1
    
#     ## Convert the Date column to actual datetime objects
#     df_long['Date'] = pd.to_datetime(df_long['Date'])
    
#     # Create the local Datetime column by adding the hour as a timedelta
#     df_long['Datetime_Local_Naive'] = df_long['Date'] + pd.to_timedelta(df_long['Hour'], unit='h')
    
#     # Localize to UTC-3 (Tatuoca) then convert to absolute UTC
#     df_long['Datetime'] = df_long['Datetime_Local_Naive'].dt.tz_localize('Etc/GMT+3').dt.tz_convert('UTC')
    
#     # Select only the needed columns and sort chronologically
#     df_final = df_long[['Datetime', 'Datetime_Local_Naive', component]].sort_values(by='Datetime').reset_index(drop=True)
    
#     # Rename to match downstream expectations
#     df_final = df_final.rename(columns={'Datetime_Local_Naive': 'Datetime_Local'})
    
#     # Make them timezone-naive again so they save identically to before (but shifted to correct alignment)
#     df_final['Datetime'] = df_final['Datetime'].dt.tz_localize(None)
    
#     # # Get Decimal Year
#     # # Calculate the start of the year and the start of the next year for each row
    
#     # start_of_year = pd.to_datetime(year, format='%Y')
#     # start_of_next_year = pd.to_datetime(year + 1, format='%Y')

#     # # Calculate the Decimal Year
#     # # This accurately accounts for leap years by dividing the elapsed time by the total time in that specific year
#     # df_final['Decimal_Year_Local'] = year + (df_final['Datetime_Local'] - start_of_year) / (start_of_next_year - start_of_year)
    
#     # Apply the function to both GMT and Local datetime columns
#     df_final['Decimal_Year_GMT'] = calculate_decimal_year(df_final['Datetime'])
#     df_final['Decimal_Year_Local'] = calculate_decimal_year(df_final['Datetime_Local'])
    
    
#     # Reorder columns to place Decimal_Year next to the other time columns
#     cols = ['Datetime', 'Decimal_Year_GMT', 'Datetime_Local', 'Decimal_Year_Local', component]
#     df_final = df_final[cols]
    
#     # Get year
#     year = df_final['Datetime'].dt.year

#     # Save file
#     df_final.to_csv(Path(output_dir) / f"formatted_{component}_{year[0]}_data.csv", index=False,  na_rep='NaN') 
    
#     return df_final




def calculate_decimal_year(dt_series):
    year = dt_series.dt.year
    start_of_year = pd.to_datetime(year, format='%Y')
    start_of_next_year = pd.to_datetime(year + 1, format='%Y')
    
    # Elapsed time divided by total time in that specific year (handles leap years)
    return year + (dt_series - start_of_year) / (start_of_next_year - start_of_year)











# def parse_ttb_dta_files(file_list: list, component: str) -> pd.DataFrame:
#     """
#     Parses a list of monthly TTB geomagnetic data files into a single, continuous DataFrame.
    
#     Parameters:
#     file_list (iterable of Path): List or generator of pathlib.Path objects.
#     component: Name of the magnetic component to be parsed.
    
#     Returns:
#     pd.DataFrame: Cleaned dataframe with 'Datetime' and 'H' columns.
#     """
#     all_records = []
    
#     # Sorting pathlib objects compares their string paths chronologically/alphabetically
#     for file_path in sorted(file_list):
#         filename = file_path.name  # Clean string filename for logging
        
#         # pathlib handles file opening directly through the Path object
#         with file_path.open('r') as f:
#             for line_idx, line in enumerate(f, start=1):
#                 line = line.strip()
#                 if not line:
#                     continue
                
#                 # 1. Parse the 10-character metadata header
#                 header = line[:10]
#                 year_short = header[3:5]  # "64" -> 1964
#                 month_str = header[5:7]   # "01"
#                 day_str = header[7:9]     # "01"
                
#                 try:
#                     base_date = datetime(int(f"19{year_short}"), int(month_str), int(day_str))
#                 except ValueError:
#                     print(f"[ERROR] Invalid date format in {filename} at line {line_idx}: {header}. Skipping line.")
#                     continue
                
#                 # 2. Extract the data block
#                 data_block = line[10:]
#                 expected_measurements = 24
#                 char_per_meas = 5
                
#                 for hour in range(expected_measurements):
#                     start_char = hour * char_per_meas
#                     end_char = start_char + char_per_meas
#                     val_str = data_block[start_char:end_char]
                    
#                     if len(val_str) < char_per_meas:
#                         val_str = val_str.ljust(char_per_meas)
                    
#                     record_datetime = base_date + timedelta(hours=hour)
                    
#                     if '*' in val_str:
#                         if val_str != '*****':
#                             print(f"[WARNING] Non-standard gap string '{val_str}' encountered "
#                                   f"in {filename} (Line {line_idx}, Hour {hour:02d}:00). Corrected to NaN.")
#                         final_val = np.nan
#                     else:
#                         try:
#                             final_val = float(val_str)
#                         except ValueError:
#                             print(f"[WARNING] Malformed value '{val_str}' encountered "
#                                   f"in {filename} (Line {line_idx}, Hour {hour:02d}:00). Corrected to NaN.")
#                             final_val = np.nan
                    
#                     all_records.append({
#                         'Datetime_UTC0': record_datetime,
#                         component: final_val
#                     })
                    
#     df = pd.DataFrame(all_records)
#     df["Datetime_UTC0"] = df["Datetime_UTC0"].dt.tz_localize('UTC')
    
#     if component == "D":
#         df["D"] = (df["D"] / 10) / 60
    
#     if not df.empty:
#         df = df.sort_values('Datetime_UTC0').reset_index(drop=True)
    
#     return df



def format_extracted_data(file: str, folder: str | Path) -> pd.DataFrame:
    
    folderpath = Path(folder)
    with open(folderpath/ file, "r", encoding="utf-8") as f:
        raw_data = f.read()
        
    cleaned_data = raw_data.replace("(", "").replace(")", "")
    cleaned_data = cleaned_data.replace(' - ', ',')

    # Transform into df
    df_ext =  pd.read_csv(StringIO(cleaned_data))
    df_ext.columns=["Curve_row_px", 
                    "Mean_baseline_row_px",
                    "Mean_baseline_Curve_col_px",
                    "Dist_Curve_Mean_baseline_mm"]
    
    df_ext["Dist_Curve_Mean_baseline_mm"] = abs(df_ext["Dist_Curve_Mean_baseline_mm"])
    
    return df_ext


def component_fit_plot(df: pd.DataFrame, x_col:str, y_col: str, degree: int,
                  component: str, datatype: str, unit: str, year: int,
                  ylims: list[int],
                  output_folder: str | Path,
                  show: bool = False):
    
    # Fit
    x = df[x_col]
    y = df[y_col]
    coeffs = np.polyfit(x, y, degree)
    fit = np.poly1d(coeffs)
    
    # Plot
    figname = Path(output_folder) / f"fig_fit_{datatype}_{component}_{year}.png"
    
    fig, ax = plt.subplots()
    ax.scatter(x, y, color = "blue", label = datatype)
    ax.plot(x, fit(x), color = "red", label = "Fit")

    ax.set(xlabel = "Time (decimal years)", ylabel = unit, 
           title= f"Fit for {component} {datatype}: {fit}")
    
    # Set Y axis limits
    ymin = ylims[0]
    ymax = ylims[1]
    
    ax.set_ylim(min(y) - ymin, max(y) + ymax)
    ax.set_xlim(min(x) - 0.01, max(x) + 0.01)
    plt.xticks(rotation=45)
    plt.ticklabel_format(axis='x', style='plain', useOffset=False)
    ax.legend()
    plt.tight_layout()
    
    # 1. Save the figure first (works perfectly behind the scenes without rendering)
    fig.savefig(figname, dpi=300, bbox_inches="tight")
    
    # 2. Handling Display vs. Memory cleanly
    if show:
        plt.show()
    else:
        plt.close(fig)  # Explicitly closes this specific figure canvas

    return coeffs


def process_baseline_fit(files: list, pathfolder: Path, 
                         out_folder: Path,
                         show: bool = False) -> tuple[np.ndarray, int]:
    dfs_baselines = []
    
    for item in files:
        df = pd.read_csv(pathfolder / item)
        df = df.dropna()
        df["Date"] = pd.to_datetime(df["Date"])
        df["Date_baseline_means"] = pd.to_datetime(df["Date_baseline_means"])
                
        # Get year and component
        year = df["Date_baseline_means"].dt.year.iat[0]
        
        # result
        dfs_baselines.append(df)
        
    # Fit
    # D
    aux = dfs_baselines[0]
    dfit = component_fit_plot(aux, "Decimal_year", "Baseline_means_dd", 1,
                         "D", "Baseline", "dd", 
                         year, [0.02, 0.02], out_folder,
                         show)  
        
    # H
    aux = dfs_baselines[1]
    hfit = component_fit_plot(aux, "Decimal_year", "Baseline_means_nT", 1,
                         "H", "Baseline", "nT", year, [25,25], out_folder, 
                         show)

    # Z
    aux = dfs_baselines[1]
    zfit = component_fit_plot(aux, "Decimal_year", "Baseline_means_nT", 1,
                         "Z", "Baseline", "nT", year, [75,50], out_folder, 
                         show)

    # save baseline coeffs
    arr = np.stack((hfit, zfit, dfit), axis=0) 
    np.savetxt(out_folder / f"baseline_coeffs_hzd_{year}.dat", arr)
    
    return arr, year


def process_scale_values_fit(files: list, 
                             input_path: Path, 
                             output_path: Path, show: bool = False) -> np.ndarray:
    dfs_scale = []
    for item in files:
        df = pd.read_csv(input_path / item)
        df = df.dropna()
        df["Date"] = pd.to_datetime(df["Date"])

        # Get year and component
        year = df["Date"].dt.year.iat[0]
        
        # result
        dfs_scale.append(df)
        
    # D
    aux = dfs_scale[0]
    dfit_sv = component_fit_plot(aux, "Decimal_year", "Scale_value(min/mm)", 1,
                         "D", "Scale Values", "min/mm", year, [1, 1], 
                         output_path,
                         show)  

    # H
    aux = dfs_scale[1]
    hfit_sv = component_fit_plot(aux, "Decimal_year", "Scale_value(min/mm)", 1,
                         "H", "Scale Values", "min/mm", year, [25, 25], 
                         output_path,
                         show)  

    # Z
    aux = dfs_scale[2]
    zfit_sv = component_fit_plot(aux, "Decimal_year", "Scale_value(nT/mm)", 1,
                         "Z", "Scale Values", "nT/mm", year, [1, 1], 
                         output_path,
                         show)

    # save baseline coeffs
    arr = np.stack((hfit_sv, zfit_sv, dfit_sv), axis=0) 
    np.savetxt(output_path / f"scale_values_coeffs_hzd_{year}.dat", arr)
    
    return arr


#%% Plots

    
def plot_one_scatter(df: pd.DataFrame, x_col: str,  y_col: str, title: str, 
    save_path: str, show: bool = False) -> None:
    """
    Generates a scatter plot from two dataframe columns and saves it to disk.
    
    Parameters
    ----------
    df : pd.DataFrame
        The dataframe containing the data.
    x_col : str
        Name of the column for the X-axis.
    y_col : str
        Name of the column for the Y-axis.
    title : str
        Title of the plot.
    save_path : str
        Full path (including filename and extension) to save the image.
    """
    
    # 1. Create the figure context
    plt.figure(figsize=(10, 6))
    
    # 2. Plot the data
    # alpha=0.7 makes points semi-transparent (good for overlapping data)
    # edgecolors='k' adds a black border to each dot for better visibility
    xvar = df[x_col].to_numpy()
    yvar = df[y_col]
    plt.scatter(xvar, yvar, c='blue', alpha=0.7, edgecolors='k')
    
    # 3. Add Labels and Title
    plt.title(title, fontsize=14)
    plt.xlabel(x_col, fontsize=12)
    plt.ylabel(y_col, fontsize=12)
    #plt.colorbar(label="Color Intensity")
    
    # 4. Add a grid (makes reading values easier)
    plt.grid(True, linestyle='--', alpha=0.6)
    
    # 5. Save the figure
    # Ensure the directory exists before saving
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300) # dpi=300 is publication quality
    
    # 6. Handling Display vs. Memory
    if show:
        plt.show()
    else:
        plt.close()

    print(f"Plot saved successfully to: {save_path}")



def plot_two_scatter(x_data, y1_data, y2_data, 
                     x_label: str, 
                     y1_label: str, 
                     y2_label: str, 
                     title: str,
                     savepath: Path | str | tuple | list,
                     show: bool = False) -> None:
    """
    Plots two different Y variables against the same X-axis on a single plot.
    """
    plt.figure(figsize=(10, 6))
    
    plt.scatter(x_data, y1_data, color='blue', alpha=0.7, label=y1_label, edgecolors='k')
    plt.scatter(x_data, y2_data, color='red', alpha=0.7, label=y2_label, marker='s', edgecolors='k')
    
    plt.xlabel(x_label)
    plt.ylabel("Values") 
    plt.title(title)
    plt.legend()          
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.xticks(rotation=45, ha='right') 
    
    # --- Robust Path Handling Fix ---
    if isinstance(savepath, (tuple, list)):
        final_path = Path(*savepath) # Unpacks ("folder", "image.png") into Path("folder", "image.png")
    else:
        final_path = Path(savepath)
        
    # Ensure parent directories exist before saving so matplotlib doesn't throw a FileNotFoundError
    final_path.parent.mkdir(parents=True, exist_ok=True)
    
    plt.savefig(final_path, dpi=300, bbox_inches="tight")
    
    if show:
        plt.show()
    else:
        plt.close()
        
        

# def plot_two_scatter(x_data, y1_data, y2_data, 
#                      x_label: str, 
#                      y1_label:str, 
#                      y2_label:str, 
#                      title:str,
#                      savepath: Path | str | tuple | list,
#                      show: bool = False) -> None:
#     """
#     Plots two different Y variables against the same X-axis on a single plot.
#     """
#     # 1. Initialize the figure size
#     plt.figure(figsize=(10, 6))
    
#     # 2. Plot the first variable (Blue circles)
#     plt.scatter(x_data, y1_data, color='blue', alpha=0.7, label=y1_label, edgecolors='k')
    
#     # 3. Plot the second variable (Red squares)
#     plt.scatter(x_data, y2_data, color='red', alpha=0.7, label=y2_label, marker='s', edgecolors='k')
    
#     # 4. Add labels, legend, title, and grid
#     plt.xlabel(x_label)
#     plt.ylabel("Values")  # General label for the shared axis
#     plt.title(title)
#     plt.legend()          # Automatically displays the labels specified above
#     plt.grid(True, linestyle='--', alpha=0.6)
#     plt.xticks(rotation=45, ha='right') 
    
#     plt.savefig(Path(savepath), dpi=300, bbox_inches="tight")
    
#     # 5. Handling Display vs. Memory
#     if show:
#         plt.show()
#     else:
#         plt.close()
        
        


# def plot_hmv_surfaces(df: pd.DataFrame, 
#                       field_component: str,
#                       time_column: str = 'Datetime',
#                       year: int = None, 
#                       output_folder: Path | str = None,
#                       show: bool = False) -> None:
#     """
#     Generates a 3D surface plot of magnetic component amplitude by day of year and hour.
#     Dynamically extracts temporal features from the datetime column to keep datasets normalized.
#     """
#     # 1. Isolate valid data
#     df_plot = df.dropna(subset=[time_column, field_component]).copy()
    
#     # 2. Dynamically derive visual coordinates on the fly
#     df_plot['DOY'] = df_plot[time_column].dt.dayofyear
#     df_plot['Hour'] = df_plot[time_column].dt.hour
    
#     if year is None:
#         year = df_plot[time_column].dt.year.iloc[0]
        
#     days = df_plot['DOY'].to_numpy()
#     hours = df_plot['Hour'].to_numpy()
#     comp = df_plot[field_component].to_numpy()

#     # 3. Figure properties
#     unit = "dd" if field_component.upper() == "D" else "nT"
#     title = f"TTB ({time_column}) in {year}: {field_component} Component"

#     fig = plt.figure(figsize=(10, 8))
#     ax = plt.axes(projection='3d')
    
#     # 4. Generate the Surface
#     # Added edgecolor='none' and alpha to smooth the heavy meshing artifacts seen in raw data
#     surf = ax.plot_trisurf(days, hours, comp, cmap="plasma", edgecolor='none', alpha=0.9)
    
#     ax.set_xlabel("Day of Year")
#     ax.set_ylabel("Hour of Day")
#     ax.set_zlabel(f"Amplitude ({unit})")
#     ax.set_title(title)
    
#     # Optional: Adjust viewing angle for better separation of the daily peaks
#     ax.view_init(elev=35, azim=-60)

#     plt.tight_layout()
    
#     # 5. Save and Render
#     if output_folder:
#         output_dir = Path(output_folder)
#         output_dir.mkdir(parents=True, exist_ok=True)
        
#         safe_time_name = time_column.replace("-", "").replace("_", "")
#         figname = output_dir / f"surface_{field_component}_{safe_time_name}_{year}.png"
#         fig.savefig(figname, dpi=300, bbox_inches="tight")
#         print(f"Surface plot saved to: {figname.name}")
    
#     if show:
#         plt.show()
#     else:
#         plt.close(fig)


def plot_histogram(variable: np.ndarray, 
                   comp: str, 
                   year: int, 
                   savepath: Path | str):
    fig, ax = plt.subplots()
    ax.hist(variable)
    ax.set(xlabel=f"{comp} values", ylabel="Distribution", 
           title=f"Histogram for {comp} in {year}")
    ax.grid()
    fig.savefig(Path(savepath), dpi=300, bbox_inches="tight")
    plt.show()
    plt.close()



#%% Old, to review

################################

def read_file(file):
    fread = open(file, 'r')
    lines = fread.readlines()
    return lines


def save_formatted_file(filename, data, folder):
    """
    Function to save files.

    Parameters
    ----------
    filename : TYPE
        DESCRIPTION.
    data : TYPE
        DESCRIPTION.
    folder : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    
    # Pandas format
    data.to_csv(folder/filename, index=False, na_rep=np.nan, header=True)
    
    # Numpy format
    #pathsave = Path(folder/filename)
    #np.savetxt(pathsave,
     #       data,
     #       delimiter =",",
     #       fmt ='% s')
     
############################### CONVERSIONS

# def to_decimal_year(dt):
#     """
#     Converts a datetime object to a decimal year.

#     Args:
#         dt (datetime): The datetime object to convert.

#     Returns:
#         float: The decimal year representation.
#     """
#     # Get the start of the year for the given datetime object
#     year_start = datetime(dt.year, 1, 1)

#     # Calculate the total number of days in the year
#     # This correctly handles leap years
#     days_in_year = 366 if calendar.isleap(dt.year) else 365

#     # Calculate the total seconds passed since the start of the year
#     total_seconds = (dt - year_start).total_seconds()

#     # Calculate the total seconds in the year
#     seconds_in_year = days_in_year * 24 * 60 * 60

#     # Return the decimal year
#     return dt.year + (total_seconds / seconds_in_year)


############################### FORMAT DATA


def find_pattern(pattern: str, input_list: list): 
    """
    Function to find pattern in list elements.

    Parameters
    ----------
    pattern : TYPE
        DESCRIPTION.
    input_list : TYPE
        DESCRIPTION.
    output_list : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    
    output_list = []
    for item in input_list:
        if re.search(pattern, item): 
            output_list.append(item)
            
    return output_list




def get_dates_in_year(year):
    """
    Generates a list of all dates within a specified year.

    Args:
        year (int): The year for which to retrieve the dates.

    Returns:
        list: A list of datetime.date objects, representing each day of the year.
    """
    dates_list = []
    start_date = date(year, 1, 1)
    # Determine the end date (December 31st of the given year)
    end_date = date(year, 12, 31)

    current_date = start_date
    while current_date <= end_date:
        dates_list.append(current_date)
        current_date += timedelta(days=1)
    return dates_list



############################### FIT
def fit_data(x, y, degree):
    coeff = np.polyfit(x, y, degree)
    fit_function = np.poly1d(coeff)
    
    return coeff, fit_function




     
############################### PLOTS

def plot_pixel_coordinates(df: pd.DataFrame, x_col: str,  y_col: str, title: str, 
    save_path: str|Path, show: bool = False) -> None:
    """
    Generates a scatter plot from two dataframe columns and saves it to disk.
    """
    
    # 1. Create the figure context
    plt.figure(figsize=(10, 6))
    
    # 2. Plot the data
    xvar = df[x_col].to_numpy()
    yvar = df[y_col]
    plt.scatter(xvar, yvar, c='blue', alpha=0.7, edgecolors='k')
    plt.xlim(0,6025)
    
    # --- NEW: Invert the Y axis to match image coordinates ---
    plt.gca().invert_yaxis()
    
    # 3. Add Labels and Title
    plt.title(title, fontsize=14)
    plt.xlabel(x_col, fontsize=12)
    plt.ylabel(y_col, fontsize=12)
    
    # 4. Add a grid
    plt.grid(True, linestyle='--', alpha=0.6)
    
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



def plot_two_scatter(x_data, y1_data, y2_data, 
                     x_label: str, 
                     y1_label: str, 
                     y2_label: str, 
                     title: str,
                     savepath: Path | str | tuple | list,
                     show: bool = False) -> None:
    """
    Plots two different Y variables against the same X-axis on a single plot.
    """
    plt.figure(figsize=(10, 6))
    
    plt.scatter(x_data, y1_data, color='blue', alpha=0.7, label=y1_label, edgecolors='k')
    plt.scatter(x_data, y2_data, color='red', alpha=0.7, label=y2_label, marker='s', edgecolors='k')
    
    plt.xlabel(x_label)
    plt.ylabel("Values") 
    plt.title(title)
    plt.legend()          
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.xticks(rotation=45, ha='right') 
    
    # --- Robust Path Handling Fix ---
    if isinstance(savepath, (tuple, list)):
        final_path = Path(*savepath) # Unpacks ("folder", "image.png") into Path("folder", "image.png")
    else:
        final_path = Path(savepath)
        
    # Ensure parent directories exist before saving so matplotlib doesn't throw a FileNotFoundError
    final_path.parent.mkdir(parents=True, exist_ok=True)
    
    plt.savefig(final_path, dpi=300, bbox_inches="tight")
    
    if show:
        plt.show()
    else:
        plt.close()