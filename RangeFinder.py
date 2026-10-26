#!/usr/bin/python
'''

'''
# imports additional python packages to handle complex functions
import subprocess # executes tasks in a subprocess
import os # used for file operations
from datetime import datetime
import time

# 2022 Data set
GRID_SIZE = 2000
COUNT22 = 79
# base url that stores datasets from r/place
D_URL = 'https://placedata.reddit.com/data/canvas-history/'
# first filename of dataset
D_FILE = '2022_place_canvas_history-000000000000.csv'
# base filename of sorted data
D_SORTED = 'Sorted_Data_'
# base filename of chronologically re-ordered data
D_ORDERED = 'Ordered_Data_'

#  2023 Data set
GRID_SIZE23_X = 1500 #  2023 dataset, files use positive and negative 1500 range
GRID_SIZE23_Y = 1000 #  2023 dataset, files use positive and negative 1000 range
COUNT23 = 53
# base url that stores datasets from r/place
D_URL23 = 'https://placedata.reddit.com/data/canvas-history/2023/'
# first filename of dataset
D_FILE23 = '2023_place_canvas_history-000000000000.csv'
# base filename of sorted data
D_SORTED23 = 'Sorted_Data_23_'
# base filename of chronologically re-ordered data
D_ORDERED23 = 'Ordered_Data_23_'

# extension of datasets
D_EXT = '.csv'











#  normalize data for 2023 dataset to all be positive integers
def rangeCheck(infile,year):
    xMin = 69420
    yMin = 69420
    xMax = 69420
    yMax = 69420
    with open(infile) as f:
        for line in f:
            check = 1
            if year == 23:
                try:
                    utc, xPos, yPos, hexValue = line.split(',')
                    xPos = int(xPos.strip('"'))
                    yPos = int(yPos.strip('"'))
                    if xMax == 69420:
                        xMax = xPos
                    if xMin == 69420:
                        xMin = xPos
                    if yMax == 69420:
                        yMax = yPos
                    if yMin == 69420:
                        yMin = yPos
                    if xMax < xPos:
                        xMax = xPos
                    if xMin > xPos:
                        xMin = xPos
                    if yMax < yPos:
                        yMax = yPos
                    if yMin > yPos:
                        yMin = yPos
                except:
                    print(f'FAIL:{line}')
    print(f'{infile}: xMin = {xMin}: xMax = {xMax}: yMin = {yMin}: yMax = {yMax}')



# python way of checking if this is the main program, i.e. this code isn't being called from 'import xxx'
if __name__ == '__main__':
    # calls the main loop, this is the line that actually starts the program moving
    for x in range(100, (100 + COUNT23)):
        dsFile = D_ORDERED23 + str(x) + D_EXT
        rangeCheck(dsFile,23)