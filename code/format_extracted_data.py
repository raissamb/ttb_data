from pathlib import Path


# 1. Force resolve the absolute path to this utility script file first
CURRENT_FILE_PATH = Path(__file__).resolve()

# 2. Step back out of the modules/ directory to find your core 'code/' directory level
CODE_ROOT = CURRENT_FILE_PATH.parent

import module_utils as ut

# 3. Derive the absolute repository workspace root directory location
PROJECT_HOME = CODE_ROOT.parent

# --- Configuration ---
OUTPUT_FOLDER = PROJECT_HOME / "data" / "formatted_extracted_data"
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)
input_datapath = PROJECT_HOME / "data" / "raw_data"/ "extracted_data"

# Get full Path objects
folders = [x for x in input_datapath.iterdir() if x.is_dir()]

########## Format time marking files
filename = "hourly_H_deviations_approach3.csv"

for item in folders:
    pathfolder = Path(OUTPUT_FOLDER/ item.name)
    pathfolder.mkdir(parents=True, exist_ok=True)
    output_filepath = f"{pathfolder}/combined_H_time_markings.csv"
    combined_dataframe = ut.combine_baseline_time_marking_files(filename, item, output_filepath)

    

########## Format time all pixels coordinates file

filename = "curve0base0.csv"
for item in folders:
    pathfolder = Path(OUTPUT_FOLDER/ item.name)
    pathfolder.mkdir(parents=True, exist_ok=True)
    output_filepath = f"{pathfolder}/pixels_coords_H.csv"
    combined_dataframe = ut.combine_pixels_coords_files(filename, item, output_filepath)

