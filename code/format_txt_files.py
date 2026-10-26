# Imports & Path Hardening
import sys
from pathlib import Path
import pandas as pd

# 1. Force resolve the absolute path to this utility script file first
CURRENT_FILE_PATH = Path(__file__).resolve()

# 2. Step back out of the modules/ directory to find your core 'code/' directory level
CODE_ROOT = CURRENT_FILE_PATH.parent

import module_utils as ut

# 3. Derive the absolute repository workspace root directory location
PROJECT_HOME = CODE_ROOT.parent
#DATA_FOLDER = PROJECT_HOME / "data" / "raw_data" / "ttb_staff_data" / "Dados64"
DATA_FOLDER = PROJECT_HOME / "data" / "raw_data" / "ttb_staff_data" / "Dados91"


# 4. Define output folders
OUT_FOLDER = PROJECT_HOME / "data" / "formatted_txt_data"
OUT_FOLDER.mkdir(parents=True, exist_ok=True)

# Define the target year for this batch processing
#target_year = 1964
target_year = 1991
year_str = str(target_year)[-2:]  # E.g., "64"

# Get all files in directory
files = ut.list_files_in_folder(Path(DATA_FOLDER))

dataframes = []

# Process each component for the specified year
for comp in ["H", "D", "Z"]:
    # Using flexible matching in case filenames vary slightly like "TTB64H.TXT" vs "TTB64H_2.TXT"
    comp_file = [f for f in files if f.startswith(f"TTB{year_str}{comp}") and f.endswith(".TXT")]
    
    if not comp_file:
        print(f"Warning: No file found for component {comp} in {target_year}.")
        continue
        
    f_name = comp_file[0]
    print(f"Processing {f_name}...")
    
    # Parse the text file
    df_raw = ut.format_table_txt_data(DATA_FOLDER, f_name)
    
    # Create the HMV dataframe and calculate formulas
    df_hmv = ut.create_hmv_from_txt_file(df_raw, comp, OUT_FOLDER)
    
    # Set the time columns as indexes so we can cleanly concat them together laterally
    #df_hmv = df_hmv.set_index(['Datetime', 'Decimal_Year_GMT', 'Datetime_Local', 'Decimal_Year_Local'])
    df_hmv = df_hmv.set_index(['Datetime', 'Datetime_Local'])
    
    # --- FIX: Remove duplicate timestamps before merging ---
    df_hmv = df_hmv[~df_hmv.index.duplicated(keep='first')]
    
    dataframes.append(df_hmv)

# Merge all available components into a single DataFrame based on exact timestamps
if dataframes:
    final_df = pd.concat(dataframes, axis=1, sort=True).reset_index()
    
    # Reorder cleanly: Time columns first, then H, D, Z
    #col_order = ['Datetime', 'Decimal_Year_GMT', 'Datetime_Local', 'Decimal_Year_Local']
    col_order = ['Datetime', 'Datetime_Local']
    available_comps = [c for c in ["H", "D", "Z"] if c in final_df.columns]
    
    final_df = final_df[col_order + available_comps]
    final_df["Data_Source"] = "TXT_files"
    
    # Save unified file
    save_path = OUT_FOLDER / f"txt_ttb_{target_year}.csv"
    final_df.to_csv(save_path, index=False, na_rep='NaN')
    print(f"\nSuccess! Unified dataset saved to: {save_path.name}")
else:
    print("Error: No dataframes were built.")