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
X_RES = 2000
Y_RES = 2000
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

# ------------------------------------------------ Start of code to download and sort data sets
# check for dataset and download if needed
def checkDataset():
    # start a loop counting ds up through 79 values, which is 0-78. Source filenames are numbered 0-78
    for ds in range(79):
        # numbers less than 10 will need to be padded with a 0 so that ds will always be the same length
        if ds < 10:
            # adds a 0 the front and makes it a string
            num = '0' + str(ds)
        # numbers >= 10 already have two digits and can just be converted to a string
        else:
            num = str(ds)
        # makes a new string using the first 36 characters from the filename, inserting a 2 character string
        # of the current number in the loop and adding the end of the filename back so it has the extension
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
    # after it checks through all filenames to make sure they have been downloaded and decompressed, it
    # launches the fixData function
    fixData()

# makes a dictionary of start times to reorganize the dataset
def fixData():
    # creates an empty dictionary
    dataFiles = {}
    # start a loop counting ds up through 79 values, which is 0-78. Source filenames are numbered 0-78
    for ds in range(79):
        # numbers less than 10 will need to be padded with a 0 so that ds will always be the same length
        if ds < 10:
            # adds a 0 the front and makes it a string
            num = '0' + str(ds)
        # numbers >= 10 already have two digits and can just be converted to a string
        else:
            num = str(ds)
        # makes a new string using the first 36 characters from the filename, inserting a 2 character string
        # of the current number in the loop and adding the end of the filename back so it has the extension
        dsFile = D_FILE[:36] + num + D_FILE[38:]
        # checks to make sure file exists before processing
        if os.path.exists(dsFile):
            # sends the filename to the sortFile function to get first time entry in seconds
            tSeconds, filename = sortFile(dsFile)
            # creates a dictionary entry with the key of time in seconds and value of filename
            dataFiles[tSeconds] = filename
    # set count variable to starting point of 100
    count = 100
    # makes a loop going through dataFile sorted by keys
    for startTime in sorted(dataFiles):
        # make terminal command to move the file to the new filename in order. This is how you rename a
        # file in a Linux terminal, move to the same location but with different name
        proc = 'mv ' + dataFiles[startTime] + ' ' + D_SORTED + str(count) + D_EXT
        # starts the terminal in a subprocess so the rest of the code can continue
        subprocess.Popen(proc, shell=True)
        # increment count variable for next pass
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
                # take the first 19 characters of time value, which cuts off milliseconds and UTC label
                # Milliseconds are cut off because the string length will change frequently, for example a time could
                # show up as 04:20:22, 04:20:22.2, 04:20:22.22, or 04:20:22.222. This could be accounted for, but since
                # each dataset is a large chunk of time there is no way two datasets would start within the same second
                utc = utc[:19]
                # this uses the datetime package to make an object that datetime recognizes as a full data and time.
                # The entry would show up like 2022-04-01 13:04:46, so we're saying here's a string formatted as
                # year-month-day hours:minutes:seconds.
                utc = datetime.strptime(utc, "%Y-%m-%d %H:%M:%S")
                # This converts the time object into a tuple, with is how the time package wants the data so that it
                # can convert it into seconds since the epoch. Then subtract time since the epoch starting around the
                # first time entry in the dataset. This last subtraction step isn't necessary since it would still be i
                # n order either way, but it just makes the numbers smaller and easier to deal with if we ever print
                # them out during testing.
                utc = time.mktime(utc.timetuple()) - 1648773840
                # returns tuple containing the time in seconds for the first entry in the file and the filename
                return utc, file
            except ValueError:  # skips lines from the csv that do not contain pixel data
                print('No values')
# ------------------------------------------------ End of code to download and sort data sets

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
                if xPos
                # initialize variable pixel as class type PlacePixel
                pixel = PlacePixel()
                # assign information parsed from the line to the class
                pixel.set(date, hTime, mTime, sTime, rgb, xPos, yPos)
                # add an entry to the list with the class data
                dataSet.append(pixel)
                # check to see if the checkTime variable has been set
                if not checkTime:
                    # if not, set it to the seconds value of current entry
                    checkTime = sTime
                # if current entry is not from the same second as the previous ones
                if checkTime != sTime:
                    # send dataset to the readData function, get array of pixel info returned
                    pixelArray = readData(dataSet)
                    # send array of pixel info to the pyGame function
                    pyGame(pixelArray)
                    # update checktime to the seconds value of current entry
                    checkTime = sTime
                    # clear dataset so it doesn't get too big
                    dataSet.clear()
                    # re-add current entry as starting point of new dataset
                    dataSet.append(pixel)
            except ValueError:  # skips lines from the csv that do not contain pixel data
                print('No values')

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
        # if it doesn't find the sorted version of the final dataset, check all files
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
        # loop through ds values of 100-178 (always stops before end value). Since we made our filenames start at 100,
        # we don't need to do any additional padding for numbers below 10 and can just convert all values to strings
        for ds in range(100, 179):
            # make string of our new filename plus current number plus extension
            dsFile = D_SORTED + str(ds) + D_EXT
            # checks to see if data file exists before running function
            if os.path.exists(dsFile):
                # sends the filename to the readFile function for processing and display
                readFile(dsFile, dataSet)

# python way of checking if this is the main program, i.e. this code isn't being called from 'import xxx'
if __name__ == '__main__':
    # calls the main loop, this is the line that actually starts the program moving
    main()