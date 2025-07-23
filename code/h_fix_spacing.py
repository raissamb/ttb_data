#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul  9 12:23:25 2025

@author: raissamb
"""

import pandas as pd
from pathlib import Path
import numpy as np
import module_format_data as fd


input_folder = Path("../raw_data/H/")
output = Path("../output/spacing_fix/")
raw_data_list = []
fd.list_files_in_folder(raw_data_list, input_folder)


# ================== Start
# read file, count spaces between strings
# repeticao de espaco em branco deve ser igual a 30 por linha para
# indicar as coluna exatas, menos que isso e pq registro ta com problema

# filenames = []
# for item in raw_data_list:
#     filename = f"formatted_{item}"
#     filenames.append(filename)


# Start process for each file
file = Path(input_folder/raw_data_list[0])
fcontent = fd.read_file(file)
count_spacing = fd.count_blank_spaces_strings(fcontent)
error_spacing_list_index = fd.get_index_wrong_spacing(count_spacing, 30)


# Manual Fix!!
#fixed = fd.fix_lines_ttbh_1964(fcontent, error_spacing_list_index)
#fd.save_formatted_file("ttbh_1964.csv", fixed, output)



# unico processo

def format_file(file, file_listname, file_function, folder): 
    
    fcontent = fd.read_file(file)
    count_spacing = fd.count_blank_spaces_strings(fcontent)
    list_index = fd.get_index_wrong_spacing(count_spacing, 30)
    
    
    
    data = fd.fix_lines_ttbh_1964(fcontent, list_index)
    fd.save_formatted_file(file_listname, data, folder)
    
   
    
    



fixyear = [fd.fix_lines_ttbh_1963, fd.fix_lines_ttbh_1964]
fixname = ["t1.cvs", "t2.csv"]






# # parte 2
# df = pd.DataFrame(fixed, columns=['All'])
# df2 = df.copy()


# header = [ "info", "D", "9",
#                   "Base_value_(unit)",
#                   "H1", "H2", "H3", "H4", "H5", "H6", "H7", "H8",
#                   "H9", "H10", "H11", "H12", "H13", "H14", "H15",
#                   "H16", "H17", "H18", "H19", "H20", "H21",
#                   "H22", "H23", "H24", "Daily_Mean"]

# df2[header] = df2['All'].str.split(' ', expand=True)
# df2 = df2.drop('All', axis=1)
