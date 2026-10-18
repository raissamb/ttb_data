from pathlib import Path
import re
import pandas as pd
from datetime import datetime

# 1. Force resolve the absolute path to this utility script file first
CURRENT_FILE_PATH = Path(__file__).resolve()

# 2. Step back out of the modules/ directory to find your core 'code/' directory level
CODE_ROOT = CURRENT_FILE_PATH.parent

import module_utils as ut

# 3. Derive the absolute repository workspace root directory location
PROJECT_HOME = CODE_ROOT.parent

# 1. Define paths based on your directory structure using Path objects
path1 = "../data/raw_data/extracted_data_keanu"
base_input_dir = Path(path1)
path2 = "../data/formatted_extracted_data_keanu"
output_dir = Path(path2)

# Ensure the output directory exists (parents=True acts like exist_ok=True with nested dirs)
output_dir.mkdir(parents=True, exist_ok=True)

# 2. Define the regex pattern to parse the string: e.g., "(416, 1083), 380 - 66.7"
regex_pattern = re.compile(r'\((\d+),\s*(\d+)\),\s*(\d+)\s*-\s*([0-9.-]+)')

# List to hold all parsed rows
parsed_data = []

# 3. Find all curve0base0.txt files using pathlib's glob method
# Matches paths like: project/data/raw_data/extracted_data_keanu/n640901/diffs/curve0base0.txt
target_files = base_input_dir.glob("n*/diffs/curve0base0.txt")

# 4. Iterate through files and extract data
for file_path in target_files:
    # Extract the specific folder name (e.g., 'n640901') 
    # file_path.parents[0] is 'diffs', file_path.parents[1] is 'n640901'
    folder_name = file_path.parents[1].name
    
    # Pathlib objects have a convenient .open() method built-in
    with file_path.open('r') as file:
        for line in file:
            match = regex_pattern.search(line)
            if match:
                parsed_data.append({
                    "folder_id": folder_name,
                    "curve_height_px": int(match.group(1)),
                    "baseline_mean_row_px": int(match.group(2)),
                    "column_position_px": int(match.group(3)),
                    "distance_mm": float(match.group(4))
                })

# 5. Convert to a Pandas DataFrame
df = pd.DataFrame(parsed_data)
df = df.sort_values(by=["folder_id"])

# 6. Save to CSV with the requested filename format using Path concatenation (/)
year = datetime.now().year 
output_filename = f"keanu_H_ttb_{year}.csv"
output_path = output_dir / output_filename

df.to_csv(output_path, index=False)