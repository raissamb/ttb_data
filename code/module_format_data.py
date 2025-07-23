#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 12 11:46:51 2025

@author: raissamb
"""


import numpy as np
import pandas as pd
from pathlib import Path

header = [
    """Info D 9 Base_value_(unit) H1 H2 H3 H4 H5 H6 H7 H8 H9 H10 H11 H12 H13 H14 H15 H16 H17 H18 H19 H20 H21 H22 H23 H24 Daily_Mean"""]


def save_formatted_file(filename, data, folder):
    pathsave = Path(folder/filename)
    np.savetxt(pathsave,
            data,
            delimiter =",",
            fmt ='% s')






def list_files_in_folder(files_list, data_folder):
    """
    Function to read files in a folder and put their names in a list in 
    alphabetical crescent order.

    Parameters
    ----------
    files_list : TYPE
        DESCRIPTION.
    data_folder : TYPE
        DESCRIPTION.

    Returns
    -------
    files_list : TYPE
        DESCRIPTION.

    """
    for entry in data_folder.iterdir():
        # check if it a file
        if entry.is_file():
            entry = entry.name
            files_list.append(entry)

    files_list.sort()
    return files_list


def read_file(file):
    fread = open(file, 'r')
    lines = fread.readlines()
    return lines


def count_blank_spaces_strings(file):
    spaces_per_row = []
    for item in file:
        count = item.count(" ")
        spaces_per_row.append(count)

    return spaces_per_row


def get_index_wrong_spacing(list_spacing, standard_spacing):
    lines_error_index = []

    for i, item in enumerate(list_spacing):
        if (item < standard_spacing):
            lines_error_index.append(i)

    return lines_error_index


def fix_lines_ttbh_1964(data, index_list):    

    # replace lines with correct format
    data[index_list[0]] = "ttb6403H19  D  9 280 9999 9999 9999 9999 9999 9999 9999 9999 9999 9999 9999 9999 9999 9999 9999 461 450 444 441 444 443 442 438 440 9999"
    data[index_list[1]] = "ttb6404H11  D  9 280 430 430 429 430 431 429 424 430 435 9999 9999 9999 9999 9999 9999 9999 9999 9999 9999 9999 9999 9999 9999 9999 9999"
    data[index_list[2]] = "ttb6404H12  D  9 280 9999 9999 9999 9999 9999 9999 9999 9999 9999 457 466 470 470 461 450 444 439 439 439 433 424 424 422 422 9999"

    content = []
    for item in data:
        row = " ".join(item.split())
        content.append(row)

    final = header + content
    #final = content

    return final




def fix_lines_ttbh_1963(data, index_list):

    # replace lines with correct format
    data[index_list[0]] = """
    ttb6303h11  D  9 280 455 458 455 454 459 457 457 462 474 9999 9999 9999 9999 9999 9999 9999 9999 9999 9999 9999 9999 9999 9999 9999 9999
    """
    
    data[index_list[1]] = """
    ttb6303h12  D  9 280 9999 9999 9999 9999 9999 9999 9999 9999 9999 484 492 493 485 485 487 480 469 464 463 463 462 462 462 463 9999
    """

    data[index_list[2]] = """
    ttb6303h21  D  9 280 9999 9999 9999 9999 9999 9999 9999 480 494 508 519 522 518 508 494 485 482 479 478 477 476 475 475 474 9999
    """
    
    data[index_list[3]] = """
    ttb6303h22  D  9 280 474 475 476 477 479 479 479 483 492 501 515 523 9999 9999 9999 9999 9999 9999 487 485 485 484 479 475 9999
    """
    
    data[index_list[4]] = """
    ttb6303h23  D  9 280 477 482 486 491 485 491 498 500 514 9999 9999 9999 9999 9999 9999 9999 9999 9999 9999 467 467 466 466 466 9999
    """
    
    data[index_list[5]] = """
    ttb6304h20  D  9 280 9999 9999 9999 9999 9999 9999 9999 475 475 488 490 493 485 481 476 472 468 466 466 465 464 464 464 465 9999    
    """
    
    data[index_list[6]] = """
    ttb6306h21  D  9 280 448 458 458 455 456 456 462 469 478 9999 9999 9999 9999 9999 9999 9999 9999 9999 9999 9999 9999 9999 460 457 9999
    """
    
    data[index_list[7]] = """ """
    
    data[index_list[8]] = """ """
    
    data[index_list[9]] = """ """
    
    data[index_list[10]] = """ """
    
    data[index_list[11]] = """ """
    
    data[index_list[12]] = """ """
    
    data[index_list[13]] = """ """
    
    data[index_list[14]] = """ """
    
    data[index_list[15]] = """ """
    
    data[index_list[16]] = """ """
    
    data[index_list[17]] = """ """
    
    data[index_list[18]] = """ """
    
    data[index_list[19]] = """ """
    
    data[index_list[20]] = """ """
    
    content = []
    for item in data:
        row = " ".join(item.split())
        content.append(row)

    # final = header + content
    final = content

    return final