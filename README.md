Tatuoca Project: Data Reconstruction Phase

This repository (ttb_data) handles the Data Reconstruction Phase of the Tatuoca Project. It serves as the direct continuation of the data extraction phase (Phase 1, maintained in the Tatuoca repository's linuxdev branch).

The primary goal of this repository is to format the raw extracted data, apply the necessary calibration metadata (baselines and scale values), reconstruct the final physical values, and validate the results against known TTB (Tatuoca Magnetic Observatory) hourly mean values.

📑 Table of Contents

Overview

Prerequisites & Inputs

Task 1: Data Formatting

Task 2: Data Reconstruction and Comparison

Expected Output

🔎 Overview

While Phase 1 focused on safely extracting legacy data, Phase 2 (this repository) is responsible for interpreting that data. Geomagnetic data extraction often yields raw instrument counts or uncalibrated measurements. This pipeline applies observatory metadata to reconstruct accurate scientific measurements and ensures data integrity through rigorous comparison.

📥 Prerequisites & Inputs

Before running the reconstruction pipeline, the following data sources must be available in the workspace:

Phase 1 Extracted Data: The raw data files successfully parsed and extracted from the previous pipeline.

Metadata Files:

Baseline Values: Absolute baseline reference values for the instruments.

Scale Values: Calibration factors required to convert raw variations into physical units (e.g., nanoTeslas).

Reference Data:

TTB Hourly Mean Values: Verified historical hourly means from the Tatuoca Observatory used strictly for validation and comparison.

🛠️ Task 1: Data Formatting

The first stage of the pipeline standardizes all input sources into a cohesive format for processing.

Key Operations:

Ingestion of Extracted Data: Loading the raw files from Phase 1 and handling any lingering structural inconsistencies (e.g., handling missing timestamps or formatting standard data frames).

Metadata Alignment: Parsing the baseline and scale value metadata files. This step ensures that the correct calibration factors are temporally aligned with the corresponding raw data points (handling baseline shifts over time).

Reference Data Preparation: Formatting the TTB hourly mean values so they share the exact same temporal index and unit structure as the target reconstructed data.

📈 Task 2: Data Reconstruction and Comparison

Once the data is formatted and aligned, the core reconstruction algorithm is applied.

1. Data Reconstruction

The script calculates the final scientific values by applying the standard observatory formula to the raw data:

Applies the specific Scale Values to convert the raw variations into their proper units.

Adds the corresponding Baseline Values to establish the absolute measurement.

2. Comparison & Validation

To guarantee the accuracy of the reconstruction, the pipeline validates the high-resolution reconstructed data against the official TTB hourly means.

Resampling: The reconstructed data is mathematically averaged into hourly bins to match the resolution of the reference data.

Residual Calculation: The script calculates the differences (residuals) between the reconstructed hourly means and the official TTB hourly means.

Quality Control: Statistical outputs or visual plots are generated to highlight any discrepancies, ensuring the newly reconstructed dataset is scientifically valid.

🚀 Expected Output

Upon successful execution, this repository will generate:

Reconstructed Datasets: Clean, calibrated time-series data files ready for scientific analysis.

Validation Reports/Plots: Visualizations or logs demonstrating the alignment between the reconstructed data and the historical TTB hourly means.
