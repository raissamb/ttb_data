import pandas as pd
from pathlib import Path
import re

# 1. Force resolve the absolute path to this utility script file first
CURRENT_FILE_PATH = Path(__file__).resolve()

# 2. Step back out of the modules/ directory to find your core 'code/' directory level
CODE_ROOT = CURRENT_FILE_PATH.parent

#import module_utils as ut

# 3. Derive the absolute repository workspace root directory location
PROJECT_HOME = CODE_ROOT.parent

# Data folders

DATA = PROJECT_HOME / "data" / "raw_data" / "ttb_data_wdcsite_1957-1999" / "csv_format"
OUT = PROJECT_HOME / "data" / "formatted_iaga_data" 
OUT.mkdir(parents=True, exist_ok=True)

def aggregate_ttb_by_year(input_folder, output_folder):
    """
    Reads monthly TTB magnetogram files and aggregates them into yearly files.
    """
    input_dir = Path(input_folder)
    output_dir = Path(output_folder)
    
    # Create the output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)

    # Dictionary to hold lists of DataFrames for each year
    yearly_data = {}

    # Iterate through all CSV files matching the pattern ttb*
    for file_path in input_dir.glob("ttb*.csv"):
        # Extract the year from the filename (e.g., ttb1964-01.csv -> 1964)
        match = re.search(r'ttb(\d{4})-\d{2}', file_path.name)
        if match:
            year = match.group(1)
            
            # Read the CSV, ignoring the description lines that start with '#'
            df = pd.read_csv(file_path, comment='#')
            
            # Initialize the list for this year if it doesn't exist
            if year not in yearly_data:
                yearly_data[year] = []
                
            yearly_data[year].append(df)
            print(f"Loaded: {file_path.name}")

    # Concatenate and save the data for each year
    for year, dfs in yearly_data.items():
        if dfs:
            # Combine all months for the year
            combined_df = pd.concat(dfs, ignore_index=True)
            
            # Sort by datetime to ensure chronological order across months
            combined_df.sort_values(by='datetime', inplace=True)
            
            # Save to the new folder
            output_file = output_dir / f"iaga_ttb_{year}.csv"
            combined_df.to_csv(output_file, index=False)
            print(f"Saved yearly file: {output_file.name} ({len(combined_df)} rows)")

if __name__ == "__main__":
    # Define your folders here
    INPUT_FOLDER = DATA  # Change to your actual input folder path
    OUTPUT_FOLDER = OUT  # Change to your desired output folder path
    
    aggregate_ttb_by_year(INPUT_FOLDER, OUTPUT_FOLDER)