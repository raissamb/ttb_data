# Imports & Path Hardening
import sys
from pathlib import Path
import pandas as pd
import io

# 1. Force resolve the absolute path to this utility script file first
CURRENT_FILE_PATH = Path(__file__).resolve()

# 2. Step back out of the modules/ directory to find your core 'code/' directory level
CODE_ROOT = CURRENT_FILE_PATH.parent

import module_utils as ut

# 3. Derive the absolute repository workspace root directory location
PROJECT_HOME = CODE_ROOT.parent
DATA_FOLDER = PROJECT_HOME / "data" / "raw_data" / "ttb_staff_data" / "Dados64"

# 4. Define output folders
OUT_FOLDER = PROJECT_HOME / "data" / "formatted_txt_data"
OUT_FOLDER.mkdir(parents=True, exist_ok=True)

# Get all files in directory
files = ut.list_files_in_folder(Path(DATA_FOLDER))
f = files[1]

df = ut.format_table_txt_data(DATA_FOLDER, f)
df2 = ut.create_hmv_from_txt_file(df, "H", OUT_FOLDER)
