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


########## Format time marking files
def combine_deviation_files(filename: str, base_path: Path, output_path: str | Path):
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

# --- Configuration ---
OUTPUT_FOLDER = PROJECT_HOME / "data" / "formatted_extracted_data"
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

filename = "hourly_H_deviations_approach3.csv"
input_datapath = PROJECT_HOME / "data" / "raw_data"/ "extracted_data"
output_filepath = f"{OUTPUT_FOLDER}/combined_H_time_markings.csv"

# Run the function
combined_dataframe = combine_deviation_files(filename, input_datapath, output_filepath)




########## Format time all pixels coordinates file
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

filename = "curve0base0.csv"
input_datapath = PROJECT_HOME / "data" / "raw_data"/ "extracted_data"
output_filepath = f"{OUTPUT_FOLDER}/pixels_coords_H.csv"
combined_px_df = combine_pixels_coords_files(filename, input_datapath, output_filepath)
