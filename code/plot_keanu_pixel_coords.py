from pathlib import Path
import re
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

# 1. Force resolve the absolute path to this utility script file first
CURRENT_FILE_PATH = Path(__file__).resolve()

# 2. Step back out of the modules/ directory to find your core 'code/' directory level
CODE_ROOT = CURRENT_FILE_PATH.parent

import module_utils as ut

# 3. Derive the absolute repository workspace root directory location
PROJECT_HOME = CODE_ROOT.parent

DATA_FOLDER = PROJECT_HOME / "data" / "formatted_extracted_data_keanu"
OUTPUT_FOLDER = PROJECT_HOME / "output" / "extracted_data_keanu"
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

file = "keanu_H_ttb_1964.csv"
df = pd.read_csv(DATA_FOLDER / file)

# Select folder id to slice df
folder = "n640913"
date = "1964-09-13"
df_folder = df[df['folder_id'] == folder]
curve_row = df_folder["curve_height_row_px"].to_numpy()
baseline_row = df_folder["baseline_mean_row_px"].to_numpy()
baseline_curve_col = df_folder["column_position_px"].to_numpy()
height_mm = df_folder["distance_mm"].to_numpy()

## Build the plot

def plot_pixel_coordinates(xvar: np.ndarray,  yvar: np.ndarray, 
                    x_label: str,
                    y_label: str,
                    title: str, 
                    save_path: str | Path, 
                    show: bool = False) -> None:
    
    # 1. Create the figure context
    plt.figure(figsize=(10, 6))
    
    # 2. Plot the data
    # alpha=0.7 makes points semi-transparent (good for overlapping data)
    # edgecolors='k' adds a black border to each dot for better visibility
    plt.scatter(xvar, yvar, c='blue', alpha=0.7, edgecolors='k')

    # --- Invert the Y axis to match image coordinates ---
    plt.gca().invert_yaxis()
    
    # 3. Add Labels and Title
    plt.title(title, fontsize=14)
    plt.xlabel(x_label, fontsize=12)
    plt.ylabel(y_label, fontsize=12)
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



plot_pixel_coordinates(baseline_curve_col, curve_row , 
                    "Column position (px)",
                    "Row position (px)",
                    f"Extracted H data Keanu for {date}", 
                    OUTPUT_FOLDER/f"{date}_keanu_H_comp_px_coords_from_diffs_folder.png",
                    False)