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

from datetime import date, timedelta

############################### FILES
def list_files_in_folder(files_list, data_folder):
    """
    Function to read files in a folder and put their names in a list in 
    alphabetical crescent order.

    Parameters
    ----------
    files_list : TYPE
        DESCRIPTION.
    data_folder : TYPE
        DESCRIPTION.

    Returns
    -------
    files_list : TYPE
        DESCRIPTION.

    """

    for entry in data_folder.iterdir():
        # check if it a file
        if entry.is_file():
            entry = entry.name
            files_list.append(entry)

    files_list.sort()
    return files_list


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

def to_decimal_year(dt):
    """
    Converts a datetime object to a decimal year.

    Args:
        dt (datetime): The datetime object to convert.

    Returns:
        float: The decimal year representation.
    """
    # Get the start of the year for the given datetime object
    year_start = datetime(dt.year, 1, 1)

    # Calculate the total number of days in the year
    # This correctly handles leap years
    days_in_year = 366 if calendar.isleap(dt.year) else 365

    # Calculate the total seconds passed since the start of the year
    total_seconds = (dt - year_start).total_seconds()

    # Calculate the total seconds in the year
    seconds_in_year = days_in_year * 24 * 60 * 60

    # Return the decimal year
    return dt.year + (total_seconds / seconds_in_year)


############################### FORMAT DATA
def find_pattern(pattern, input_list, output_list): 
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
    for item in input_list:
        if re.search(pattern, item): 
            output_list.append(item)



def create_dfs_component(input_folder, files_list, nan_list, dfs_list):
    """
    Function to create dfs for each component.

    Parameters
    ----------
    files_list : TYPE
        DESCRIPTION.
    nan_list : TYPE
        DESCRIPTION.
    dfs_list : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
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
            
        
        # replace and remove strings
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


def plot_fit(x, y, degree, comp, var, unit, figname, ymax, ymin):
    """
    Function to fit a polynomial for a given dataset. It als plots the original
    data and the fit.

    Parameters
    ----------
    x : TYPE
        DESCRIPTION.
    y : TYPE
        DESCRIPTION.
    degree : TYPE
        DESCRIPTION.
    comp : TYPE
        DESCRIPTION.
    var : TYPE
        DESCRIPTION.
    unit : TYPE
        DESCRIPTION.
    figname : TYPE
        DESCRIPTION.
    ytop : TYPE
        DESCRIPTION.
    ybot : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    
    # Fit
    coefficients = np.polyfit(x, y, degree)
    fit = np.poly1d(coefficients)

    # Plot
    fig, ax = plt.subplots()
    ax.scatter(x, y, color = "blue", label = var)
    ax.plot(x, fit(x), color = "red", label = "Fit")
    ax.set(xlabel = "Time (decimal years)", ylabel = unit, 
           title= f"Fit for {comp} {var}: {fit}")
    ax.set_ylim(min(y) - ymin, max(y) + ymax)
    ax.legend()
    plt.tight_layout()
    plt.show()
    fig.savefig(figname, dpi=300, bbox_inches="tight")
    
    
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