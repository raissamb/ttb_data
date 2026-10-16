import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# 1. Path Resolution
CURRENT_FILE_PATH = Path(__file__).resolve()
CODE_ROOT = CURRENT_FILE_PATH.parent
PROJECT_HOME = CODE_ROOT.parent

# Data folders
IAGA_CSV = PROJECT_HOME / "data" / "formatted_iaga_data"
STAFF_DTA = PROJECT_HOME / "data" / "formatted_dta_data"
STAFF_TXT = PROJECT_HOME / "data" / "formatted_txt_data"

# Output folder
OUTPUT_FOLDER = PROJECT_HOME / "output" / "surface_plots"
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

def plot_hmv_surfaces(df: pd.DataFrame, 
                      field_component: str,
                      dataset_name: str,
                      time_column: str = 'Datetime',
                      year: int = None, 
                      output_folder: Path | str = None,
                      show: bool = False) -> None:
    """
    Generates a 3D surface plot of magnetic component amplitude by day of year and hour.
    """
    # Isolate valid data
    df_plot = df.dropna(subset=[time_column, field_component]).copy()
    
    if df_plot.empty:
        print(f"Warning: No valid data for {field_component} in {dataset_name}.")
        return

    # Dynamically derive visual coordinates
    df_plot[time_column] = pd.to_datetime(df_plot[time_column], utc=True)
    df_plot['DOY'] = df_plot[time_column].dt.dayofyear
    df_plot['Hour'] = df_plot[time_column].dt.hour
    
    if year is None:
        year = df_plot[time_column].dt.year.iloc[0]
        
    days = df_plot['DOY'].to_numpy()
    hours = df_plot['Hour'].to_numpy()
    comp = df_plot[field_component].to_numpy()

    # Figure properties
    unit = "dd" if field_component.upper() == "D" else "nT"
    title = f"TTB {dataset_name} ({year}): {field_component} Component"

    fig = plt.figure(figsize=(10, 8))
    ax = plt.axes(projection='3d')
    
    # Generate the Surface
    surf = ax.plot_trisurf(days, hours, comp, cmap="plasma", edgecolor='none', alpha=0.9)
    
    ax.set_xlabel("Day of Year")
    ax.set_ylabel("Hour of Day (UTC)")
    ax.set_zlabel(f"Amplitude ({unit})")
    ax.set_title(title)
    
    ax.view_init(elev=35, azim=-60)
    plt.tight_layout()
    
    # Save and Render
    if output_folder:
        output_dir = Path(output_folder)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        figname = output_dir / f"surface_{dataset_name}_{field_component}_{year}.png"
        fig.savefig(figname, dpi=300, bbox_inches="tight")
        print(f"Saved: {figname.name}")
    
    if show:
        plt.show()
    else:
        plt.close(fig)

def generate_all_surfaces(year: int, components: list = ["H", "D", "Z"]):
    """
    Loads IAGA, DTA, and TXT formatted files and generates surface plots for each component.
    """
    # Define file paths
    iaga_file = IAGA_CSV / f"ttb{year}_yearly.csv"
    dta_file = STAFF_DTA / f"hmv_HZD_{year}.csv"
    txt_file = STAFF_TXT / f"formatted_HDZ_{year}_data.csv"

    # Process IAGA
    if iaga_file.exists():
        df_iaga = pd.read_csv(iaga_file)
        # Filter out 99999.0 missing values for IAGA
        for comp in components:
            if comp in df_iaga.columns:
                df_clean = df_iaga[df_iaga[comp] < 99999.0]
                plot_hmv_surfaces(df_clean, comp, "IAGA", time_column='datetime', 
                                  year=year, output_folder=OUTPUT_FOLDER / "IAGA")
    else:
        print(f"IAGA file not found: {iaga_file}")

    # Process DTA
    if dta_file.exists():
        df_dta = pd.read_csv(dta_file)
        for comp in components:
            if comp in df_dta.columns:
                plot_hmv_surfaces(df_dta, comp, "DTA", time_column='Datetime_UTC0', 
                                  year=year, output_folder=OUTPUT_FOLDER / "DTA")
    else:
        print(f"DTA file not found: {dta_file}")

    # Process TXT
    if txt_file.exists():
        df_txt = pd.read_csv(txt_file)
        for comp in components:
            if comp in df_txt.columns:
                plot_hmv_surfaces(df_txt, comp, "TXT", time_column='Datetime', 
                                  year=year, output_folder=OUTPUT_FOLDER / "TXT")
    else:
        print(f"TXT file not found: {txt_file}")

if __name__ == "__main__":
    target_year = 1964
    print(f"Generating surface plots for {target_year}...")
    generate_all_surfaces(target_year)
    print("\nAll surface plots generated successfully.")