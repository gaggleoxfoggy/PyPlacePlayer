'''
PyPlacePlayer

P-Trip is a program to read from the reddit.com/r/place dataset and display
the information to the screen as a timelapse.
'''
# imports additional python packages to handle complex functions
import numpy as np # used to turn dataset into array of pixel values
import pygame as pg # reads pixel array and displays images to screen
import subprocess # executes tasks in a subprocess
import os # used for file operations
from datetime import datetime
import time

# static constants
#X & Y constants, will be used to define resolution of player window
X_RES = 1000
Y_RES = 1000
# base url that stores datasets from r/place
D_URL = 'https://placedata.reddit.com/data/canvas-history/'
# first filename of dataset
D_FILE = '2022_place_canvas_history-000000000000.csv'
# base filename of sorted data
D_SORTED = 'Sorted_Data_'
# extension of datasets
D_EXT = '.csv'

# initialize pygame
pg.init()
# set display resolution to X & Y constants
screen = pg.display.set_mode((X_RES, Y_RES))
# initialize pygame clock, will be used to lock framerate
clock = pg.time.Clock()

# create array for pixels and set default to white
pixelArray = np.full((X_RES, Y_RES, 3), 255)

# class to organize information from each pixel in the dataset
class PlacePixel:

    # method to set values for pixel
    def set(self, date, hTime, mTime, sTime, rgb, xPos, yPos):
        self.date = date
        self.hTime = int(hTime)
        self.mTime = int(mTime)
        self.sTime = int(sTime)
        self.rgb = rgb
        self.xPos = xPos
        self.yPos = yPos






# check for dataset and download if needed
def checkDataset():
    for ds in range(79):
        if ds < 10:
            num = '0' + str(ds)
        else:
            num = str(ds)
        dsFile = D_FILE[:36] + num + D_FILE[38:]
        # check to see if the file already exists
        if not os.path.exists(dsFile):
            # this builds a terminal command that will use the tool 'curl' to download the file and then
            # use 'gzip' to decompress the file. The use of && makes them run in series, so the file will
            # finish downloading before it tries to decompress it.
            proc = 'curl -o ' + dsFile + '.gzip ' + D_URL + dsFile + \
                   '.gzip && gzip -f -d -S .gzip ' + dsFile + '.gzip'
            # starts the terminal in a subprocess
            p = subprocess.Popen(proc, shell=True)
            # links thread to the subprocess so it will not continue until completed
            p.communicate()
    fixData()

def fixData():
    dataFiles = {}
    for ds in range(79):
        if ds < 10:
            num = '0' + str(ds)
        else:
            num = str(ds)
        dsFile = D_FILE[:36] + num + D_FILE[38:]
        if os.path.exists(dsFile):
            # sends the filename to the sortFile function to get first time entry in seconds
            utc, filename = sortFile(dsFile)
            dataFiles[utc] = filename
    count = 100

    for startTime in sorted(dataFiles):
        proc = 'mv', dataFiles[startTime], D_SORTED + str(count) + D_EXT
        # starts the terminal in a subprocess so the rest of the code can continue
        subprocess.Popen(proc, shell=True)
        count += 1

# sorts the dataset into chronological order
def sortFile(file):
    # opens a file and also handles closing the file when done
    with open(file) as f:
        # iterate through each line of text
        for line in f:
            # try adds exception handling so program will not crash on errors
            try:
                # split line at every comma and assign each comma separated value to a variable
                utc, null, hexValue, xPos, yPos = (line.split(','))
                utc = utc[:19]
                utc = datetime.strptime(utc, "%Y-%m-%d %H:%M:%S")
                utc = time.mktime(utc.timetuple()) - 1648773840
                return utc, file
            except ValueError:  # skips lines from the csv that do not contain pixel data
                print('No values')







# Reads data file into a list and sends it to pygame for display
def readFile(file, dataSet):
    # initial value for 'checkTime' which will be used to see when the dataset has moved to the next second
    checkTime = False
    # opens a file and also handles closing the file when done
    with open(file) as f:
        # iterate through each line of text
        for line in f:
            # try adds exception handling so program will not crash on errors
            try:
                # split line at every comma and assign each comma separated value to a variable
                utc, null, hexValue, xPos, yPos = (line.split(','))
                # break full date/time variable into smaller date and time variables
                date, time, null = utc.split()
                # only take the first 8 characters from time to remove milliseconds
                time = time[:8]
                # split time variable into hours, minutes, seconds variables
                hTime, mTime, sTime = time.split(':')
                # break each section of the hex value into r,g,b parts
                r = hexValue[1] + hexValue[2]
                g = hexValue[3] + hexValue[4]
                b = hexValue[5] + hexValue[6]
                # convert RGB 16 bit hex values into integers
                rgb = [int(r, 16), int(g, 16), int(b, 16)]
                # remove extra data from x & y position values and convert to integer
                xPos = int(xPos.strip('"'))
                yPos = int(yPos.rstrip('"\n'))
                # initialize variable pixel as class type PlacePixel
                pixel = PlacePixel()
                # assign information parsed from the line to the class
                pixel.set(date, hTime, mTime, sTime, rgb, xPos, yPos)
                # add an entry to the list with the class data
                dataSet.append(pixel)
                # check to see if the checkTime variable has been set
                if not checkTime:
                    # if not, set it to time of current entry
                    checkTime = sTime
                # if current entry is not from the same second as the previous ones
                if checkTime != sTime:
                    # send dataset to the readData function, get array of pixel info returned
                    pixelArray = readData(dataSet)
                    # send array of pixel info to the pyGame function
                    pyGame(pixelArray)
                    # update checktime to the current entry
                    checkTime = sTime
                    # clear dataset so it doesn't get too big
                    dataSet.clear()
                    # re-add current entry as starting point of new dataset
                    dataSet.append(pixel)
            except ValueError:  # skips lines from the csv that do not contain pixel data
                print('No values')
    return dataSet


# reads pixels from the dataset and returns an array of RGB values
def readData(dataSet):
    # read through the dataset from the first pixel requested until the end of the dataset
    for x in range(len(dataSet)):
        # check if the current pixel being read falls within the window resolution
        if 0 <= dataSet[x].xPos < X_RES and 0 <= dataSet[x].yPos < Y_RES:
            # assign the RGB values to an X,Y position in the array
            pixelArray[dataSet[x].xPos, dataSet[x].yPos] = dataSet[x].rgb
    # return array of pixel data
    return pixelArray

# loop of the game engine that displays the data to screen
def pyGame(pixelarray):
    # turn array of pixel values into an image buffer
    surface = pg.surfarray.make_surface(pixelArray)
    # add the new image to the screen canvas starting at top left corner (0,0)
    screen.blit(surface, (0, 0))
    # update screen ouptut
    pg.display.flip()
    # check clock to keep maximum framerate at 60 FPS
    clock.tick(60)

# main code loop
def main():
    # make sure end of dataset is downloaded and sorted before continuing
    if not os.path.exists(D_SORTED + '178' + D_EXT):
        checkDataset()
    # create empty list to store info from the dataset
    dataSet = []
    # pygame variable to exit loop
    running = True
    # start of pygame loop
    while running:
        # check for pygame events
        for event in pg.event.get():
            # if exit code is given, end the loop
            if event.type == pg.QUIT:
                running = False

        for ds in range(100, 179):
            #dsFile = D_FILE[:36] + num + D_FILE[38:]
            dsFile = D_SORTED + str(ds) + D_EXT
            # checks to see if data file exists before running function
            if os.path.exists(dsFile):
                # sends the filename to the readFile function for processing and display
                dataSet = readFile(dsFile, dataSet)

# python way of checking if this is the main program, i.e. this code isn't being called from 'import xxx'
if __name__ == '__main__':
    # calls the main loop, this is the line that actually starts the program moving
    main()
