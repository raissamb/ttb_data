#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 25 13:36:11 2025

@author: raissamb
"""

from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Create the scatter plot
def plot_hmv_surfaces(field_component, input_file, input_folder, output_folder):
    # Create main df
    df = pd.read_csv(input_folder/input_file)
    df = df.dropna()
    year = input_file[3:7]

    # Plot variables
    days = df["DOY"].to_numpy()
    hours = df["Hours_in_day"].to_numpy()
    comp = df[field_component].to_numpy()

    # Fig details
    if (field_component == "D"):
        unit = "dd"
    else:
        unit = "nT"

    #figname = f"../output/{field_component}_hmv_surface_{year}.png"
    figname = f"{output_folder}/{field_component}_hmv_surface_{year}.png"
    xlabel = "Days"
    ylabel = "Hours"
    zlabel = f"Amplitude {unit}"
    title = f"{field_component} component in {year} at TTB"

    # Figure
    fig = plt.figure()
    ax = plt.axes(projection='3d')
    ax.plot_trisurf(days, hours, comp, cmap="plasma")
    ax.set(xlabel=xlabel, ylabel=ylabel, zlabel=zlabel, title=title)
    plt.tight_layout()
    fig.savefig(figname, dpi=400, bbox_inches="tight")