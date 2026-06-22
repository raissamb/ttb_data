# -*- coding: utf-8 -*-
"""
Created on Sat Aug 30 11:55:37 2025

@author: raiss
"""

import pandas as pd
from pathlib import Path
import numpy as np
import module_utils as ut
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

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

output_folder = Path("../output/early_result_data_extraction/")

###########################  DISTANCES FROM MEASUREMENT TO BASELINE IN MM
# using the 30min marks
# Get all files in directory
#dist_folder = Path("../data/n640913/diffs/")
dist_folder = Path("../data/n640913/30min/")
files = []
files = ut.list_files_in_folder(files, dist_folder)
f = files[1]
df = pd.read_csv(dist_folder/f)
df.columns=['Dist_mm', 'Column_Pixel_Position']
df_1h = df.iloc[::2]
#df_1h = df.iloc[1::2]
h = df_1h["Dist_mm"]


########################### BASELINE 
# Baseline values y = ax +b 
#blh = 2.06267 * t + 24170.3, where t is time for Sep-Oct data
#blh = -30.473 * t + 88095.5, where t is time for all year data

# create list of hours for 1964-09-13
hourly_dates = []
start_date = datetime(1964, 9, 13, 0, 0, 0)
end_date = datetime(1964, 9, 14, 0, 0, 0)
current_date = start_date
while current_date < end_date:
    hourly_dates.append(current_date)
    current_date += timedelta(hours=1)

# convert the datetime for 1964-09-13 to decimal years
date_dec_years = []
for i in hourly_dates:
    date_dec_years.append(ut.to_decimal_year(i))
    
    
bhl = []
for t in date_dec_years:
    val = (2.06267 * t) + 24170.3
    #val = (-30.47 * t) + 88100
    bhl.append(val)
    
    
    
    
# ########################### SCALE VALUE
# # Scale value for H following TTB 1964 magnetogram metadata and formula for
# # September
# # H = Baseline + Scale_value * distance_mm
# # scale value sh = s0 + DeltaD * S0 + a * n
# sh = []
# for i in h:
#     var = 3.138 + (-0.0173) + 0.00122 * i
#     sh.append(var)

# #sh = 3.138 + (-0.0173) + 0.00122



########################### SCALE VALUE following y = ax +b 
#sh = 0.177097 * t - 344.807, #where t is time for Sep-Oct data
#sh = 0.0132377 * t - 22.8773, #where t is time for all year data

sh = 0.177097 * t - 344.807
#sh = 0.0132377 * t - 22.8773
sh = []
for t in date_dec_years:
    val = ((0.177097 * t) - 344.807)
    sh.append(val)
  
    

    
########################### hmv
# hmv = bhl + sh * h
hmv = []

for i,j,k in zip(bhl, sh, h):
    res = i + j * k
    hmv.append(res)



date = current_date.date

# Plot
fig, ax = plt.subplots()
ax.scatter(hourly_dates, hmv, color = "blue", label = "HMV")
ax.set(xlabel = "Time", ylabel = "nT", 
       title= "H in 1964-09-13 (Oct-Sep data)")
#ax.set_ylim(min(y) - ymin, max(y) + ymax)
plt.xticks(rotation=90) 
ax.legend()
plt.tight_layout()
plt.show()
fig.savefig("../output/early_result_data_extraction/sep_oct_prelim_result_HMV_13_09_1964.png", 
            dpi=300, bbox_inches="tight")
    
    
    
data = list(zip(hourly_dates, date_dec_years, bhl, sh, h, hmv))
resultados = pd.DataFrame(data, columns=["Datetime", "Decimal_years", 
                                         "Candidate_baseline_H", 
                                         "Candidate_scale_value_h",
                                         "Distances_mm",
                                         "Calculated_HMV_nT"])

ut.save_formatted_file("early_results_table.csv", resultados, output_folder)