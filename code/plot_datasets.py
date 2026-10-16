import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

# 1. Force resolve the absolute path to this utility script file first
CURRENT_FILE_PATH = Path(__file__).resolve()

# 2. Step back out of the modules/ directory to find your core 'code/' directory level
CODE_ROOT = CURRENT_FILE_PATH.parent

# 3. Derive the absolute repository workspace root directory location
PROJECT_HOME = CODE_ROOT.parent

# Data folders
IAGA_CSV = PROJECT_HOME / "data" / "formatted_iaga_data"
STAFF_DTA = PROJECT_HOME / "data" / "formatted_dta_data"
STAFF_TXT = PROJECT_HOME / "data" / "formatted_txt_data"

# Output
output_folder = PROJECT_HOME / "output" / "plot_datasets"
output_folder.mkdir(parents=True, exist_ok=True)

def load_aligned_data(year, component="H"):
    """
    Loads IAGA, DTA, and TXT data for a given year, extracts the component,
    and returns a single unified DataFrame indexed by UTC datetime.
    """
    component = component.upper()
    
    iaga_file = IAGA_CSV / f"ttb{year}_yearly.csv"
    dta_file = STAFF_DTA / f"hmv_HZD_{year}.csv"
    txt_file = STAFF_TXT / f"formatted_H_{year}_data.csv"

    dataframes = []

    # Load IAGA
    if iaga_file.exists():
        df_iaga = pd.read_csv(iaga_file)
        if component in df_iaga.columns and 'datetime' in df_iaga.columns:
            df_iaga = df_iaga[df_iaga[component] < 99999.0] # Filter missing
            df_iaga['datetime'] = pd.to_datetime(df_iaga['datetime'], utc=True)
            df_iaga = df_iaga.set_index('datetime')[[component]].rename(columns={component: 'IAGA'})
            # Remove duplicate timestamps
            df_iaga = df_iaga[~df_iaga.index.duplicated(keep='first')]
            dataframes.append(df_iaga)

    # Load STAFF DTA
    if dta_file.exists():
        df_dta = pd.read_csv(dta_file)
        if component in df_dta.columns and 'Datetime_UTC0' in df_dta.columns:
            df_dta['Datetime_UTC0'] = pd.to_datetime(df_dta['Datetime_UTC0'], utc=True)
            df_dta = df_dta.set_index('Datetime_UTC0')[[component]].rename(columns={component: 'DTA'})
            # Remove duplicate timestamps
            df_dta = df_dta[~df_dta.index.duplicated(keep='first')]
            dataframes.append(df_dta)

    # Load STAFF TXT
    if txt_file.exists():
        df_txt = pd.read_csv(txt_file)
        if component in df_txt.columns and 'Datetime' in df_txt.columns:
            df_txt['Datetime'] = pd.to_datetime(df_txt['Datetime'], utc=True)
            df_txt = df_txt.set_index('Datetime')[[component]].rename(columns={component: 'TXT'})
            # Remove duplicate timestamps
            df_txt = df_txt[~df_txt.index.duplicated(keep='first')]
            dataframes.append(df_txt)

    # Merge all available dataframes on their time index
    if not dataframes:
        return pd.DataFrame()
    
    # Explicitly set sort=True to chronologically order the merged DatetimeIndex
    combined_df = pd.concat(dataframes, axis=1, sort=True)
    return combined_df

def plot_magnetic_component_yearly(year, component="H"):
    """Plots a specific magnetic component for the entire year."""
    df = load_aligned_data(year, component)
    if df.empty:
        print(f"No data found for {year}.")
        return

    plt.figure(figsize=(12, 6))
    for col in df.columns:
        plt.plot(df.index, df[col], label=f"{col} ({component})", alpha=0.7)

    plt.title(f"Yearly Comparison - {component} Component - {year}")
    plt.xlabel("Datetime (UTC)")
    plt.ylabel(f"Amplitude ({component})")
    plt.legend()
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.tight_layout()
    plt.savefig(output_folder / f"yearly_{component}_{year}.png", dpi=300)
    plt.show()

def plot_magnetic_component_daily(year, date_str, component="H"):
    """Plots all datasets for a specific date (YYYY-MM-DD)."""
    df = load_aligned_data(year, component)
    if df.empty:
        print(f"No data found for {year}.")
        return

    # Filter by the specific date
    try:
        df_day = df.loc[date_str]
    except KeyError:
        print(f"No data available for the date {date_str}.")
        return

    plt.figure(figsize=(10, 5))
    for col in df_day.columns:
        plt.plot(df_day.index, df_day[col], label=f"{col} ({component})", marker='o', markersize=3, alpha=0.8)

    plt.title(f"Daily Comparison - {component} Component - {date_str}")
    plt.xlabel("Time (UTC)")
    plt.ylabel(f"Amplitude ({component})")
    plt.legend()
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.tight_layout()
    plt.savefig(output_folder / f"daily_{component}_{date_str}.png", dpi=300)
    plt.show()

def plot_dataset_difference(year, ds1="IAGA", ds2="DTA", component="H", date_str=None):
    """
    Plots the difference between two selected datasets (ds1 - ds2).
    If date_str is provided, plots for that day; otherwise, plots the whole year.
    Valid dataset names: 'IAGA', 'DTA', 'TXT'.
    """
    df = load_aligned_data(year, component)
    
    if ds1 not in df.columns or ds2 not in df.columns:
        print(f"Error: Both '{ds1}' and '{ds2}' must be available to plot their difference.")
        print(f"Available datasets for {year}: {list(df.columns)}")
        return

    # Calculate difference
    diff_series = df[ds1] - df[ds2]

    # Filter by date if provided
    if date_str:
        try:
            diff_series = diff_series.loc[date_str]
            title_suffix = date_str
            save_suffix = f"{date_str}"
        except KeyError:
            print(f"No data available for the date {date_str}.")
            return
    else:
        title_suffix = str(year)
        save_suffix = f"yearly_{year}"

    plt.figure(figsize=(12, 5))
    plt.plot(diff_series.index, diff_series, color='red', alpha=0.8, label=f"{ds1} - {ds2}")
    
    # Add a zero-line for reference
    plt.axhline(0, color='black', linewidth=1, linestyle='--')

    plt.title(f"Difference ({ds1} minus {ds2}) - {component} Component - {title_suffix}")
    plt.xlabel("Datetime (UTC)")
    plt.ylabel(f"Difference in Amplitude ({component})")
    plt.legend()
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.tight_layout()
    plt.savefig(output_folder / f"difference_{ds1}_vs_{ds2}_{component}_{save_suffix}.png", dpi=300)
    plt.show()

if __name__ == "__main__":
    target_year = 1964
    target_component = "H" 
    target_date = "1964-09-13"

    print("Generating Yearly Plot...")
    plot_magnetic_component_yearly(target_year, target_component)

    print(f"\nGenerating Daily Plot for {target_date}...")
    plot_magnetic_component_daily(target_year, target_date, target_component)

    print("\nGenerating Yearly Difference Plot (IAGA vs DTA)...")
    plot_dataset_difference(target_year, ds1="IAGA", ds2="DTA", component=target_component)

    print(f"\nGenerating Daily Difference Plot (IAGA vs DTA) for {target_date}...")
    plot_dataset_difference(target_year, ds1="IAGA", ds2="DTA", component=target_component, date_str=target_date)
    
    print(f"\nGenerating Daily Difference Plot (IAGA vs TXT) for {target_date}...")
    plot_dataset_difference(target_year, ds1="IAGA", ds2="TXT", component=target_component, date_str=target_date)
    
    print(f"\nGenerating Daily Difference Plot (TXT vs DTA) for {target_date}...")
    plot_dataset_difference(target_year, ds1="TXT", ds2="DTA", component=target_component, date_str=target_date)