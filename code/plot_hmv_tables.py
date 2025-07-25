#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 12 16:11:39 2025

@author: raissamb
"""

from pathlib import Path
import pandas as pd
import module_format_data as fd
import module_plot as pt
import matplotlib.pyplot as plt

# Paths and files
data_folder = Path("../output/hmv_tables/")
surface_folder = Path("../output/plot_surface_hmv/")
histogram_folder = Path("../output/plot_histograms_hmv/")

data_list = []
data_list = fd.list_files_in_folder(data_list, data_folder)

data_file = data_list[0]
df = pd.read_csv(data_folder/data_file)

pt.plot_hmv_surfaces("H", data_file, data_folder, surface_folder)
pt.plot_hmv_surfaces("D", data_file, data_folder, surface_folder)
pt.plot_hmv_surfaces("Z", data_file, data_folder, surface_folder)


def plot_histogram(variable, fcomp, year, output_folder, figname):
    fig, ax = plt.subplots()
    ax.hist(variable)
    ax.set(xlabel=f"{fcomp} values", ylabel="Distribution", title=f"Histogram for {fcomp} in {year}")
    ax.grid()
    fig.savefig(output_folder/figname, dpi=400, bbox_inches="tight")
    plt.show()
    plt.close()


plot_histogram(df["H"], "H", 1964, histogram_folder, "H1964.png")
plot_histogram(df["D"], "D", 1964, histogram_folder, "D1964.png")
plot_histogram(df["Z"], "Z", 1964, histogram_folder, "Z1964.png")