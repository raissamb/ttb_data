# -*- coding: utf-8 -*-
"""
Created on Wed Aug 20 19:16:05 2025

@author: raiss
"""

from datetime import datetime
import calendar
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
from pathlib import Path
from typing import Optional
from datetime import date, timedelta
import io
from io import StringIO

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



def format_table_txt_data(data_folder, file):
    with open(data_folder / file, "r", encoding="utf-8") as f:
        raw_data = f.read()
        
    # Detach the glued missing values
    cleaned_data = raw_data.replace('9999', ' NaN ')

    # Read the cleaned text into a pandas DataFrame using whitespace parsing
    # FIX: Added 'r' before '\s+' to designate a raw string
    df = pd.read_csv(io.StringIO(cleaned_data), sep=r'\s+', header=None, engine='python')

    # Assign logical column names based on the 29-column structure
    col_names = ['Information', 'Type', 'Code1', 'Base_value'] + \
                [f'Hour_{i:02d}' for i in range(1, 25)] + \
                ['Variation_mean']

    # Validate and apply columns
    if len(df.columns) == len(col_names):
        df.columns = col_names
    else:
        print(f"Expected {len(col_names)} columns, but found {len(df.columns)}.")
        
    
    # replace and remove strings
    df["Information"] = df["Information"].str.replace('ttb', '19')
    df["Information"] = df["Information"].str.replace('H', '')
   
    # Add date time in YYYY-MM-DD format
    df["Year"] = df["Information"].str.slice(0,4)
    df["Month"] = df["Information"].str.slice(4,6)
    df["Day"] = df["Information"].str.slice(6,8)
    df["Date"] = pd.to_datetime(df[['Year', 'Month', 'Day']])
    

    
    return df


def create_hmv_from_txt_file(df: pd.DataFrame, component: str, output_dir: str | Path):
    df2 = df[["Date"]].copy()
    hours = [f'Hour_{i:02d}' for i in range(1, 25)]
    
    # Get HMV
    for item in hours:
        var = df["Base_value"]*100 + df[item]
        df2[item] = var
    
     
    # Melt the dataframe from wide to long format
    df_long = df2.melt(id_vars=['Date'], var_name='Hour_Col', value_name=component)
    
    # Extract the hour number from the column name (e.g., "Hour_01" -> 1)
    # Subtract 1 so that Hour_01 corresponds to 00:00, Hour_02 to 01:00, ..., Hour_24 to 23:00
    df_long['Hour'] = df_long['Hour_Col'].str.extract("(\d+)").astype(int) - 1
    
    ## Convert the Date column to actual datetime objects
    df_long['Date'] = pd.to_datetime(df_long['Date'])
    
    # Create the final Datetime column by adding the hour as a timedelta
    df_long['Datetime'] = df_long['Date'] + pd.to_timedelta(df_long['Hour'], unit='h')
    
    # Select only the needed columns and sort chronologically
    df_final = df_long[['Datetime', component]].sort_values(by='Datetime').reset_index(drop=True)
    
    # Create Datetime_Local by subtracting 3 hours (since 00:00 GMT = 21:00 Local)
    df_final['Datetime_Local'] = df_final['Datetime'] - pd.Timedelta(hours=3)
    
    # # Get Decimal Year
    # # Calculate the start of the year and the start of the next year for each row
    
    # start_of_year = pd.to_datetime(year, format='%Y')
    # start_of_next_year = pd.to_datetime(year + 1, format='%Y')

    # # Calculate the Decimal Year
    # # This accurately accounts for leap years by dividing the elapsed time by the total time in that specific year
    # df_final['Decimal_Year_Local'] = year + (df_final['Datetime_Local'] - start_of_year) / (start_of_next_year - start_of_year)
    
    # Apply the function to both GMT and Local datetime columns
    df_final['Decimal_Year_GMT'] = calculate_decimal_year(df_final['Datetime'])
    df_final['Decimal_Year_Local'] = calculate_decimal_year(df_final['Datetime_Local'])
    
    
    # Reorder columns to place Decimal_Year next to the other time columns
    cols = ['Datetime', 'Decimal_Year_GMT', 'Datetime_Local', 'Decimal_Year_Local', component]
    df_final = df_final[cols]
    
    # Get year
    year = df_final['Datetime'].dt.year

    # Save file
    df_final.to_csv(Path(output_dir) / f"formatted_{component}_{year[0]}_data.csv", index=False,  na_rep='NaN') 
    
    return df_final




def calculate_decimal_year(dt_series):
    year = dt_series.dt.year
    start_of_year = pd.to_datetime(year, format='%Y')
    start_of_next_year = pd.to_datetime(year + 1, format='%Y')
    
    # Elapsed time divided by total time in that specific year (handles leap years)
    return year + (dt_series - start_of_year) / (start_of_next_year - start_of_year)




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
    #ax.ticklabel_format(axis='x', style='plain')
    #ax.set_xticks(x)
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
    plt.show()
    fig.savefig(figname, dpi=300, bbox_inches="tight")
    
    # 5. Handling Display vs. Memory
    if show:
        plt.show()
    else:
        plt.close()

    return coeffs


def parse_ttb_dta_files(file_list: list, component: str):
    """
    Parses a list of monthly TTB geomagnetic data files into a single, continuous DataFrame.
    
    Parameters:
    file_list (iterable of Path): List or generator of pathlib.Path objects.
    component: Name of the magnetic component to be parsed.
    
    Returns:
    pd.DataFrame: Cleaned dataframe with 'Datetime' and 'H' columns.
    """
    all_records = []
    
    # Sorting pathlib objects compares their string paths chronologically/alphabetically
    for file_path in sorted(file_list):
        filename = file_path.name  # Clean string filename for logging
        
        # pathlib handles file opening directly through the Path object
        with file_path.open('r') as f:
            for line_idx, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                
                # 1. Parse the 10-character metadata header
                header = line[:10]
                year_short = header[3:5]  # "64" -> 1964
                month_str = header[5:7]   # "01"
                day_str = header[7:9]     # "01"
                
                try:
                    base_date = datetime(int(f"19{year_short}"), int(month_str), int(day_str))
                except ValueError:
                    print(f"[ERROR] Invalid date format in {filename} at line {line_idx}: {header}. Skipping line.")
                    continue
                
                # 2. Extract the data block
                data_block = line[10:]
                expected_measurements = 24
                char_per_meas = 5
                
                for hour in range(expected_measurements):
                    start_char = hour * char_per_meas
                    end_char = start_char + char_per_meas
                    val_str = data_block[start_char:end_char]
                    
                    if len(val_str) < char_per_meas:
                        val_str = val_str.ljust(char_per_meas)
                    
                    record_datetime = base_date + timedelta(hours=hour)
                    
                    if '*' in val_str:
                        if val_str != '*****':
                            print(f"[WARNING] Non-standard gap string '{val_str}' encountered "
                                  f"in {filename} (Line {line_idx}, Hour {hour:02d}:00). Corrected to NaN.")
                        final_val = np.nan
                    else:
                        try:
                            final_val = float(val_str)
                        except ValueError:
                            print(f"[WARNING] Malformed value '{val_str}' encountered "
                                  f"in {filename} (Line {line_idx}, Hour {hour:02d}:00). Corrected to NaN.")
                            final_val = np.nan
                    
                    all_records.append({
                        'Datetime': record_datetime,
                        component: final_val
                    })
                    
    df = pd.DataFrame(all_records)
    
    if component == "D":
        df["D"] = (df["D"] / 10) / 60
        df["Unit"] = "decimal_degree"
    else:
        df["Unit"] = "nT"
    
    if not df.empty:
        df = df.sort_values('Datetime').reset_index(drop=True)
    return df



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



def process_baseline_fit(files: list, pathfolder: Path, out_folder: Path) -> tuple[np.ndarray, int]:
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
                         "D", "Baseline", "dd", year, [0.02, 0.02], out_folder)  
        
    # H
    aux = dfs_baselines[1]
    hfit = component_fit_plot(aux, "Decimal_year", "Baseline_means_nT", 1,
                         "H", "Baseline", "nT", year, [25,25], out_folder)

    # Z
    aux = dfs_baselines[1]
    zfit = component_fit_plot(aux, "Decimal_year", "Baseline_means_nT", 1,
                         "Z", "Baseline", "nT", year, [75,50], out_folder)

    # save baseline coeffs
    arr = np.stack((hfit, zfit, dfit), axis=0) 
    np.savetxt(out_folder / f"baseline_coeffs_hzd_{year}.dat", arr)
    
    return arr, year


def process_scale_values_fit(files: list, input_path: Path, output_path: Path) -> np.ndarray:
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
                         "D", "Scale Values", "min/mm", year, [1, 1], output_path)  

    # H
    aux = dfs_scale[1]
    hfit_sv = component_fit_plot(aux, "Decimal_year", "Scale_value(min/mm)", 1,
                         "H", "Scale Values", "min/mm", year, [25, 25], output_path)  

    # Z
    aux = dfs_scale[2]
    zfit_sv = component_fit_plot(aux, "Decimal_year", "Scale_value(nT/mm)", 1,
                         "Z", "Scale Values", "nT/mm", year, [1, 1], output_path)

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
                     y1_label:str, 
                     y2_label:str, 
                     title:str,
                     savepath: Path | str,
                     show: bool = False):
    """
    Plots two different Y variables against the same X-axis on a single plot.
    """
    # 1. Initialize the figure size
    plt.figure(figsize=(10, 6))
    
    # 2. Plot the first variable (Blue circles)
    plt.scatter(x_data, y1_data, color='blue', alpha=0.7, label=y1_label, edgecolors='k')
    
    # 3. Plot the second variable (Red squares)
    plt.scatter(x_data, y2_data, color='red', alpha=0.7, label=y2_label, marker='s', edgecolors='k')
    
    # 4. Add labels, legend, title, and grid
    plt.xlabel(x_label)
    plt.ylabel("Values")  # General label for the shared axis
    plt.title(title)
    plt.legend()          # Automatically displays the labels specified above
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.xticks(rotation=45, ha='right') 
    
    plt.savefig(Path(savepath), dpi=300, bbox_inches="tight")
    
    # 5. Handling Display vs. Memory
    if show:
        plt.show()
    else:
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


def create_dfs_component(input_folder: Path, files_list: list):
    
    # Create lists
    nan_list = []
    dfs_list = []
    
    header = ["info", 
              "0-1h","1-2h", "2-3h", "3-4h", "4-5h", "5-6h", 
             "6-7h", "7-8h", "8-9h", "9-10h", "10-11h", "11-12h",
             "12-13h" ,"13-14h", "14-15h", "15-16h", "16-17h", "17-18h", 
             "18-19h", "19-20h", "20-21h" , "21-22h", "22-23h", "23-24h"]
    
    for item in files_list:
        df1 = pd.read_csv(input_folder/item, names=["All"])
        
        # check for NaN values
        has_nan = df1.isnull().values.any() 
        nan_list.append(has_nan)
        
        # Slice first column to create the HMV table and date into separate columns
        j = 0
        k = 10
        df = df1.copy()
        for i in range(25):
            
            df[header[i]] = df["All"].str.slice(j, k)
            j = k
            k = k + 5
            
        
        # Replace and remove strings
        df["info"] = df["info"].str.replace('ttb', '19')
        df["info"] = df["info"].str.replace('H', '')
        
        # Add date time in YYYY-MM-DD format
        df["Year"] = df["info"].str.slice(0,4)
        df["Month"] = df["info"].str.slice(4,6)
        df["Day"] = df["info"].str.slice(6,8)
        df["Date"] = pd.to_datetime(df[['Year', 'Month', 'Day']])
         
        df_mod = df.drop(columns=['All', "info", "Year", "Month", "Day"], axis=1)
        new_order = ["Date", 
                     "0-1h","1-2h", "2-3h", "3-4h", "4-5h", "5-6h", 
                 "6-7h", "7-8h", "8-9h", "9-10h", "10-11h", "11-12h",
                 "12-13h" ,"13-14h", "14-15h", "15-16h", "16-17h", "17-18h", 
                 "18-19h", "19-20h","20-21h" ,"21-22h", "22-23h", "23-24h"]

        # Reorder the DataFrame
        df_final = df_mod[new_order]
        
        # Convert columns to numeric type
        del new_order[0]
        for item in new_order:
            df_final[item] = pd.to_numeric(df[item], errors='coerce')
            
        # Replace 'NA' and empty strings with NaN
        df_final = df_final.replace({'NA': np.nan, '': np.nan, '*****': np.nan})
        
        # append result df to list
        dfs_list.append(df_final)
        
    return dfs_list, nan_list





def create_hmv_tables_year(input_dfs_list, component, output_dfs_list):
    """
    Function to create HMV tables per year.

    Parameters
    ----------
    input_dfs_list : TYPE
        DESCRIPTION.
    component : TYPE
        DESCRIPTION.
    output_dfs_list : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    hours = list(range(0,24))
    
    for item in input_dfs_list:
        df = item
        ndays = len(df)
        
        for i in range(0, ndays):
            date= df.iat[i, 0]
            hmv = df.iloc[i, 1:25].values.tolist()
            dates = [date] * 24
            
            # Create df in HMV column formata (each hour is a row)
            dc = {"Dates": dates, f'{component}': hmv}
            df1 = pd.DataFrame(dc)
            df1["Hours_in_day"] = hours
            df1["Datetime"] = df1['Dates'] + pd.to_timedelta(df1["Hours_in_day"], unit='h')
            
            # Drop columns
            df1 = df1.drop(columns=["Dates"], axis=1)
            
            # Save df to list
            output_dfs_list.append(df1)
            
            

def create_hmv_tables_year_v2(input_dfs_list, component, output_dfs_list):
    """
    Function to create HMV tables per year.

    Parameters
    ----------
    input_dfs_list : TYPE
        DESCRIPTION.
    component : TYPE
        DESCRIPTION.
    output_dfs_list : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    #hours = list(range(0,24))
    utc_local = [21, 22, 23, 0, 1, 2, 3, 4, 5,
                 6, 7, 8, 9, 10, 11, 12, 13,
                 14, 15, 16, 17, 18, 19, 20]

    for item in input_dfs_list:
        df = item
        ndays = len(df)
        
        col = df.columns.tolist()
        time = col[1:]
        
        for i in range(0, ndays):
            date= df.iat[i, 0]
            hmv = df.iloc[i, 1:25].values.tolist()
            dates = [date] * 24
            
            # Create df in HMV column formata (each hour is a row)
            dc = {"Dates": dates, f'{component}': hmv}
            df1 = pd.DataFrame(dc)
            df1["Interval"] = time
            df1["UTC-3"] = utc_local
            
            # Save df to list
            output_dfs_list.append(df1)
            
            
            
            
def concat_hmv_tables(hmv_tables, component, final_list):
    """
    Function to create one df per year per component with the following header:
        Datetime(YYYY-MM-DD-HH), Component_hmv, DOY, Data_source

    Parameters
    ----------
    hmv_tables : TYPE
        DESCRIPTION.
  
    final_list : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    # create one df per year
    df_concat = pd.concat(hmv_tables)
    
    # Get day of year: DOY
    days = list(range(1, len(hmv_tables) +1))
    doy = [i for i in days for _ in range(24)]

    df_concat["DOY"] = doy
    df_concat["Data_source"] = "TTB_staff_DTA_files"
    new_order = ["Datetime", f"{component}", "DOY", "Hours_in_day" ,"Data_source"]

    df_year = df_concat[new_order]
    #save_formatted_file(filename, df_year, output_folder)
    
    #final_list.append(df_year)
    final_list = df_year.copy()
    return final_list



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
def plot_hmv_surfaces(field_component, input_file, input_folder, output_folder):
    # Create main df
    df = pd.read_csv(input_folder/input_file)
    df = df.dropna()
    year = input_file[3:7]

    # Plot variables
    days = df["DOY"].to_numpy()
    hours = df["Hours_in_day"].to_numpy()
    comp = df[field_component].to_numpy()

    # Fig details
    if (field_component == "D"):
        unit = "dd"
    else:
        unit = "nT"

    #figname = f"../output/{field_component}_hmv_surface_{year}.png"
    figname = f"{output_folder}/{field_component}_hmv_surface_{year}.png"
    xlabel = "Days"
    ylabel = "Hours"
    zlabel = f"Amplitude {unit}"
    title = f"{field_component} component in {year} at TTB"

    # Figure
    fig = plt.figure()
    ax = plt.axes(projection='3d')
    ax.plot_trisurf(days, hours, comp, cmap="plasma")
    ax.set(xlabel=xlabel, ylabel=ylabel, zlabel=zlabel, title=title)
    plt.tight_layout()
    fig.savefig(figname, dpi=400, bbox_inches="tight")



    
    
def plot_histogram(variable, fcomp, year, output_folder, figname):
    fig, ax = plt.subplots()
    ax.hist(variable)
    ax.set(xlabel=f"{fcomp} values", ylabel="Distribution", 
           title=f"Histogram for {fcomp} in {year}")
    ax.grid()
    fig.savefig(output_folder/figname, dpi=400, bbox_inches="tight")
    plt.show()
    plt.close()
    
    
    
def plot_scatter_hmv_day(df, doy, comp, unit, folder, ymax, ymin):
    
    aux = df[df['DOY'] == doy]
    x = aux["Datetime"].dt.hour
    y = aux[comp]

    date = aux["Datetime"].dt.date.iat[0]
    figname = f"{comp}_{date}.png"
    
    # Plot
    fig, ax = plt.subplots()
    ax.scatter(x, y, color = "blue", label = "HMV")
    ax.set(xlabel = "Time (hours)", ylabel = unit, 
           title= f"{comp} in {date}")
    ax.set_ylim(min(y) - ymin, max(y) + ymax)
    plt.xticks(rotation=90) 
    ax.legend()
    plt.tight_layout()
    plt.show()
    fig.savefig(folder/figname, dpi=300, bbox_inches="tight")
    
    
def plot_scatter2_hmv_day(df1, df2, label1, label2, doy, comp, unit, folder, ymax, ymin):
    
    # df1
    aux1 = df1[df1['DOY'] == doy]
    x1 = aux1["Datetime_GMT-3"].dt.hour
    y1 = aux1[comp]
    
    # df2
    aux2 = df2[df2['DOY'] == doy]
    x2 = aux2["Datetime_GMT0"].dt.hour
    y2 = aux2[comp]

    date = aux1["Datetime_GMT-3"].dt.date.iat[0]
    figname = f"{date}_{comp}_hmv_{label1}_{label2}.png"
    
    # Plot
    fig, ax = plt.subplots()
    ax.scatter(x1, y1, color = "blue", label = label1)
    ax.scatter(x2, y2, color = "red", label = label2)
    ax.set(xlabel = "Time (hours)", ylabel = unit, 
           title= f"{comp} in {date}")
    ax.set_ylim(min(y1) - ymin, max(y1) + ymax)
    #plt.xticks(rotation=90) 
    ax.legend()
    plt.tight_layout()
    plt.show()
    fig.savefig(folder/figname, dpi=300, bbox_inches="tight")
    
    
# def plot_fit(x, y, degree, comp, var, unit, figname, ymax, ymin, dataspec):
#     """
#     Function to fit a polynomial for a given dataset. It als plots the original
#     data and the fit.

#     Parameters
#     ----------
#     x : TYPE
#         DESCRIPTION.
#     y : TYPE
#         DESCRIPTION.
#     degree : TYPE
#         DESCRIPTION.
#     comp : TYPE
#         DESCRIPTION.
#     var : TYPE
#         DESCRIPTION.
#     unit : TYPE
#         DESCRIPTION.
#     figname : TYPE
#         DESCRIPTION.
#     ytop : TYPE
#         DESCRIPTION.
#     ybot : TYPE
#         DESCRIPTION.

#     Returns
#     -------
#     None.

#     """
    
#     # Fit
#     coefficients = np.polyfit(x, y, degree)
#     fit = np.poly1d(coefficients)

#     # Plot
#     fig, ax = plt.subplots()
#     ax.scatter(x, y, color = "blue", label = var)
#     ax.plot(x, fit(x), color = "red", label = "Fit")
#     #ax.ticklabel_format(axis='x', style='plain')
#     #ax.set_xticks(x)
#     ax.set(xlabel = "Time (decimal years)", ylabel = unit, 
#            title= f"Fit for {comp} {var} {dataspec}: {fit}")
#     ax.set_ylim(min(y) - ymin, max(y) + ymax)
#     ax.set_xlim(min(x) - 0.01, max(x) + 0.01)
#     plt.xticks(rotation=45)
#     plt.ticklabel_format(axis='x', style='plain', useOffset=False)
#     ax.legend()
#     plt.tight_layout()
#     plt.show()
#     fig.savefig(figname, dpi=300, bbox_inches="tight")
