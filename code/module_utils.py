# -*- coding: utf-8 -*-
"""
Created on Wed Aug 20 19:16:05 2025

@author: raissa
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


############################### UTILS

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



def calculate_decimal_year(dt_series):
    year = dt_series.dt.year
    start_of_year = pd.to_datetime(year, format='%Y')
    start_of_next_year = pd.to_datetime(year + 1, format='%Y')
    
    # Elapsed time divided by total time in that specific year (handles leap years)
    return year + (dt_series - start_of_year) / (start_of_next_year - start_of_year)


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


################## DATA FORMATTING

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
    #df["Information"] = df["Information"].astype(str).str.replace('ttb', '19')
    df["Information"] = df["Information"].astype(str).str.replace(pat={"ttb": "19", "TTB": "19"})
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



def combine_baseline_time_marking_files(filename: str, base_path: Path, output_path: str | Path):
    """
    Scans subdirectories for a specific file and combines them into a single DataFrame.
    """
    base_dir = Path(base_path)
    all_dataframes = []
    
    # Iterate through all items in the base directory
    for folder_path in sorted(base_dir.iterdir()):
        # Check if it's a directory (the folder_id)
        if folder_path.is_dir():
            folder_id = folder_path.name
            target_file = folder_path / filename
            
            # Check if the target file exists in this folder
            if target_file.exists():
                try:
                    # Read the file
                    df = pd.read_csv(target_file)
                    
                    # Add a column to identify which folder_id the data came from
                    df['folder_id'] = folder_id 
                    
                    all_dataframes.append(df)
                    print(f"Successfully read: {target_file}")
                except Exception as e:
                    print(f"Error reading {target_file}: {e}")

    # Combine all individual dataframes into one unique dataframe
    if all_dataframes:
        combined_df = pd.concat(all_dataframes, ignore_index=True)
        
        # Create the output directory if it doesn't exist
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Save the combined dataframe to the output path
        combined_df = combined_df.sort_values(by=["datetime_utc"])
        combined_df = combined_df.loc[:,
                                      ["component",
                                       "datetime_utc",
                                       "date_utc",
                                       "time_utc",
                                       "datetime_local_utc3",
                                       "date_local_utc3",
                                       "time_local_utc3",
                                       "column",
                                       "row_baseline",
                                       "row_trace",
                                       "delta_height_mm",
                                       "marker_type",           
                                       "folder_id"
]]
        combined_df.to_csv(output_path, index=False)
        print(f"\nAll files combined successfully! Saved to: {output_path}")
        return combined_df
    else:
        print("\nNo files found matching the criteria.")
        return None


def combine_pixels_coords_files(filename: str, base_path: Path, output_path: str | Path):
    """
    Scans subdirectories for a specific file, combines them into a single DataFrame,
    and sorts the result to maintain coordinate order.
    """
    base_dir = Path(base_path)
    all_dataframes = []
    
    # Use sorted() to ensure folders are processed in alphabetical/numerical order
    for folder_path in sorted(base_dir.iterdir()):
        if folder_path.is_dir():
            folder_id = folder_path.name
            target_file = folder_path / "diffs" / filename
            
            if target_file.exists():
                try:
                    df = pd.read_csv(target_file)
                    df['folder_id'] = folder_id 
                    all_dataframes.append(df)
                    print(f"Successfully read: {target_file}")
                except Exception as e:
                    print(f"Error reading {target_file}: {e}")

    if all_dataframes:
        # Combine all dataframes
        combined_df = pd.concat(all_dataframes, ignore_index=True)
        
        # Sort by folder_id to guarantee the overarching sequence. 
        # Using kind='mergesort' ensures a stable sort, keeping the original pixel coordinate order intact within each folder group.
        combined_df = combined_df.sort_values(by=['folder_id'], kind='mergesort').reset_index(drop=True)
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        combined_df.to_csv(output_path, index=False)
        print(f"\nAll files combined successfully! Saved to: {output_path}")
        return combined_df
    else:
        print("\nNo files found matching the criteria.")
        return None



import pandas as pd

def remove_duplicate_mark(
    df: pd.DataFrame, 
    drop: str = "last", 
    time_col: str = "datetime_utc"
) -> pd.DataFrame:
    """
    Removes duplicated hour markers where day transitions overlap.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing the baseline time markings.
    drop : str, default 'last'
        Which pixel marker to drop among the duplicates:
        - 'last' or 'last_pixel' (drops the last_pixel row, keeping first_pixel).
        - 'first' or 'first_pixel' (drops the first_pixel row, keeping last_pixel).
    time_col : str, default 'datetime_utc'
        Column name used to identify duplicate timestamps.
        Can also be 'datetime_local_utc3' or 'time_local_utc3'.
        
    Returns
    -------
    pd.DataFrame
        Cleaned DataFrame with 24 hourly marks and reset index.
    """
    df_clean = df.copy()
    
    # Normalize input argument
    drop_choice = drop.strip().lower()
    if "last" in drop_choice:
        target_marker = "last_pixel"
    elif "first" in drop_choice:
        target_marker = "first_pixel"
    else:
        raise ValueError("Argument 'drop' must be either 'last'/'last_pixel' or 'first'/'first_pixel'.")
    
    # Identify duplicated timestamps
    is_duplicate = df_clean.duplicated(subset=[time_col], keep=False)
    
    # Filter by marker_type if available; fallback to positional deduplication
    if "marker_type" in df_clean.columns and (df_clean.loc[is_duplicate, "marker_type"] == target_marker).any():
        drop_mask = is_duplicate & (df_clean["marker_type"] == target_marker)
        df_clean = df_clean[~drop_mask]
    else:
        # Positional fallback: 'last_pixel' is the first chronological row (keep='last')
        # 'first_pixel' is the second chronological row (keep='first')
        keep_mode = "last" if target_marker == "last_pixel" else "first"
        df_clean = df_clean.drop_duplicates(subset=[time_col], keep=keep_mode)
        
    return df_clean.reset_index(drop=True)











def fit_metadata_equations(file_paths, folder_path, is_baseline=True, degree=1):
    """
    Reads metadata files, identifies the component dynamically, 
    and returns a dictionary of callable equations (np.poly1d).
    """
    equations = {}
    
    for file_name in file_paths:
        file_path = Path(folder_path) / file_name
        df = pd.read_csv(file_path).dropna()
        
        if df.empty:
            continue
            
        # 1. Identify the component dynamically straight from the data
        comp = df["Component"].iat[0]
        
        # 2. Determine target column dynamically
        if is_baseline:
            target_col = 'Baseline_means_dd' if comp == 'D' else 'Baseline_means_nT'
        else:
            # Dynamically search for any column containing "Scale_value"
            target_col = next((col for col in df.columns if 'Scale_value' in col), None)
            
        if target_col is None or target_col not in df.columns:
            print(f"Warning: Expected target column not found for {comp} in {file_name}")
            continue
            
        x = df["Decimal_year"].values
        y = df[target_col].values
        
        # 3. Perform the fit and create a callable function object
        coeffs = np.polyfit(x, y, degree)
        fit_eq = np.poly1d(coeffs)
        
        # Map the equation to the specific component
        equations[comp] = fit_eq
        
    return equations


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
    yvar = df[y_col].to_numpy()
    plt.scatter(xvar, yvar, c='blue', alpha=0.7, edgecolors='k')
    #plt.xlim(0,6025)
    plt.xticks(np.arange(0, 6000, 500))
    
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



























