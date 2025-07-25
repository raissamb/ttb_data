#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 12 11:46:51 2025

@author: raissamb
"""


import numpy as np
import pandas as pd
from pathlib import Path
import re
from pathlib import Path

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





