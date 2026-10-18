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

# Data folders
EXTRACTED_DATA_DIFF = PROJECT_HOME / "data" / "formatted_extracted_data_keanu"
#EXTRACTED_DATA_DIFF_RMB = PROJECT_HOME / "data" / "raw_data" / "extracted_data_raissa"


#EXTRACTED_DATA = PROJECT_HOME / "data" / "extracted_data" / "n640913" / "30min"


BASELINE_FOLDER = PROJECT_HOME / "data" / "formatted_baselines"
BASELINE_COEFFS_FOLDER = PROJECT_HOME / "output" / "plot_fit_baselines"

SCALEV_FOLDER = PROJECT_HOME / "data" / "formatted_scale_values"
SCALEV_COEFFS_FOLDER = PROJECT_HOME / "output" / "plot_fit_scale_values"

ttb_folder = PROJECT_HOME / "data" / "formatted_dta_data"

# Output
output_folder = PROJECT_HOME / "output" / "early_result_data_extraction"
output_folder.mkdir(parents=True, exist_ok=True)



#%% Process Extracted data 
"""
descricao das linhas
base0: linha de base H
curve0: H
curve1: D
curve2: ta pegando Z e a outra linha de base para 1964-09-13

descricao do arquivo curve0base0.txt em diffs
- altura da curva de medicao (em pixels)
- média da posicao linha do pixel da baseline, 
- posicao coluna da curva de medicao (pixels), que é a msm posicao coluna para linha de base
- distancia em mm entre a curva e a media da linha da linha de basel
"""

### --- DISTANCES FROM MEASUREMENT TO BASELINE IN MM


### Source: diffs folder

diffs_kn = pd.read_csv(EXTRACTED_DATA_DIFF/"keanu_H_ttb_1964.csv")
folder1 = "n640912"
folder2 = "n640913"


df_kn = diffs_kn[(diffs_kn["folder_id"] == folder1) | (diffs_kn["folder_id"] == folder2)]






# # Setup variables
# curve_row = df_ext_diffs["Curve_row_px"].to_numpy()
# baseline_row = df_ext_diffs["Mean_baseline_row_px"].to_numpy()
# baseline_curve_col = df_ext_diffs["Mean_baseline_Curve_col_px"].to_numpy()
# height_mm = df_ext_diffs["Dist_Curve_Mean_baseline_mm"].to_numpy()

# ## Build the plot
# ut.plot_pixel_coordinates(df_ext_diffs, 
#                     "Mean_baseline_Curve_col_px", 
#                "Curve_row_px", 
#                "Px", 
#                output_folder/"fig_H_comp_px_diffs_folder.png")