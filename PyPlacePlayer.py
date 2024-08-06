#!/usr/bin/python
'''
PyPlacePlayer

P-Trip (PyPlacePlayer) is a program to read from the reddit.com/r/place dataset and display
the information to the screen as a timelapse.

2022 Dataset canvas growth times
First X = 2022-04-02 16:24:56.239 UTC
Sorted_Data_113.csv
First Y = 2022-04-03 19:03:53.356 UTC
Sorted_Data_134.csv

2023 canvas size dataset changes
X = 1000-1999, Y = 500-1499
109
X = 1000-2499, Y = 500-1499
115
X = 500-2499, Y = 500-1499
121
X = 500-2499, Y = 0-1499
128
X = 500-2499, Y = 0-1999
132
X = 0-2499, Y = 0-1999
138
X = 0-2999, Y = 0-1999
'''
# imports additional python packages to handle complex functions
import random
import numpy as np # used to turn dataset into array of pixel values
import pygame as pg # reads pixel array and displays images to screen
import subprocess # executes tasks in a subprocess
import os # used for file operations
from datetime import datetime
import time
os.environ['SDL_AUDIODRIVER'] = 'dsp' # Don't need audio and ALSA kept crashing

#  set to list of file numbers of the first data set after each canvas resize to capture starting images.
#  Currently only set up for 2023 dataset
getResize = False

# static constants
#X & Y constants, will be used to define resolution of player window
NATIVE_X_RES = 800
NATIVE_Y_RES = 600
MAX_SCALE = 6 #   res scale will get randomized each loop with this as max
RAND_TOLERANCE = 40

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
GRID_SIZE23_X = 3000
GRID_SIZE23_Y = 2000
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
# initialize pygame
pg.init()
# set display resolution to X & Y constants
screen = pg.display.set_mode((NATIVE_X_RES, NATIVE_Y_RES))# pg.display.set_mode((GRID_SIZE23_X, GRID_SIZE23_Y))#
# initialize pygame clock, will be used to lock framerate
clock = pg.time.Clock()
pg.mouse.set_visible(False)

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
def checkDataset(year,total):
    if year == 22:
        TMP_FILE = D_FILE
        TMP_URL = D_URL
    if year == 23:
        TMP_FILE = D_FILE23
        TMP_URL = D_URL23
        # start a loop counting ds up through 79 values, which is 0-78. Source filenames are numbered 0-78
    for ds in range(total):
        # numbers less than 10 will need to be padded with a 0 so that ds will always be the same length
        if ds < 10:
            # adds a 0 the front and makes it a string
            num = '0' + str(ds)
        # numbers >= 10 already have two digits and can just be converted to a string
        else:
            num = str(ds)
        # makes a new string using the first 36 characters from the filename, inserting a 2 character string
        # of the current number in the loop and adding the end of the filename back so it has the extension

        dsFile = TMP_FILE[:36] + num + TMP_FILE[38:]
        # check to see if the file already exists
        if not os.path.exists(dsFile):
            # this builds a terminal command that will use the tool 'curl' to download the file and then
            # use 'gzip' to decompress the file. The use of && makes them run in series, so the file will
            # finish downloading before it tries to decompress it.
            proc = 'curl -o ' + dsFile + '.gzip ' + TMP_URL + dsFile + \
                   '.gzip && gzip -f -d -S .gzip ' + dsFile + '.gzip'
            # starts the terminal in a subprocess
            p = subprocess.Popen(proc, shell=True)
            # links thread to the subprocess so it will not continue until completed
            p.communicate()
    # after it checks through all filenames to make sure they have been downloaded and decompressed, it
    # launches the fixData function. ONLY NEEDED ON 2022 DATA
    if year == 22:
        fixData(year,total)

#  normalize data for 2023 dataset to all be positive integers
def normalizeData(infile, outfile, year):
    with open(outfile, 'w') as output:
        with open(infile) as f:
            for line in f:
                if year == 23:
                    try:
                        utc, null, xPos, yPos, hexValue = line.split(',')
                        # Convert xPos and yPos to integers and adjust values
                        xPos = int(xPos.strip('"')) + 1500
                        yPos = int(yPos.strip('"')) + 1000
                        output.write(f'{utc},"{xPos},{yPos}",{hexValue}')
                    except:
                        print(f'Normalize error: {line}')


# makes a dictionary of start times to reorganize the dataset
def fixData(year,total):
    # creates an empty dictionary
    dataFiles = {}
    if year == 22:
        TMP_FILE = D_FILE
        TMP_SORTED = D_SORTED
        # start a loop counting ds up through 79 values, which is 0-78. Source filenames are numbered 0-78
    for ds in range(total):
        # numbers less than 10 will need to be padded with a 0 so that ds will always be the same length
        if ds < 10:
            # adds a 0 the front and makes it a string
            num = '0' + str(ds)
        # numbers >= 10 already have two digits and can just be converted to a string
        else:
            num = str(ds)
        # makes a new string using the first 36 characters from the filename, inserting a 2 character string
        # of the current number in the loop and adding the end of the filename back so it has the extension
        dsFile = TMP_FILE[:36] + num + TMP_FILE[38:]
        # checks to make sure file exists before processing
        if os.path.exists(dsFile):
            # sends the filename to the sortFile function to get first time entry in seconds
            tSeconds, filename = sortFile(year,dsFile)
            # creates a dictionary entry with the key of time in seconds and value of filename
            dataFiles[tSeconds] = filename
    # set count variable to starting point of 100
    count = 100
    # makes a loop going through dataFile sorted by keys
    for startTime in sorted(dataFiles):
        # make terminal command to move the file to the new filename in order. This is how you rename a
        # file in a Linux terminal, move to the same location but with different name
        proc = 'mv ' + dataFiles[startTime] + ' ' + TMP_SORTED + str(count) + D_EXT
        # starts the terminal in a subprocess so the rest of the code can continue
        subprocess.Popen(proc, shell=True)
        # increment count variable for next pass
        count += 1

# sorts the datasets into chronological order
def sortFile(year,file):
    with open(file) as f:
        for line in f:
            try:
                if year == 22:
                    utc, null, hexValue, xPos, yPos = (line.split(','))
                if year == 23:
                    utc, null, xPos, yPos, hexValue = (line.split(','))
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
                # first time entry in the dataset. This last subtraction step isn't necessary since it would still be
                # in order either way, but it just makes the numbers smaller and easier to deal with if we ever print
                # them out during testing.
                utc = time.mktime(utc.timetuple()) - 1648773840
                # returns tuple containing the time in seconds for the first entry in the file and the filename
                return utc, file
            except ValueError:  # skips lines from the csv that do not contain pixel data
                print('No values')

#order the contents of each dataset chronologically
def orderDataset(year,total):
    # start a loop counting ds up through 79 values, which is 0-78. Source filenames are numbered 0-78
    for ds in range(100,(total+100)):
        if year == 22:
            dsFile = D_SORTED + str(ds) + D_EXT
            outFile = D_ORDERED + str(ds) + D_EXT
        if year == 23:
            dsFile = D_SORTED23 + str(ds) + D_EXT
            outFile = D_ORDERED23 + str(ds) + D_EXT
        # checks to make sure file exists before processing
        if os.path.exists(dsFile):
            # creates an empty dictionary
            dataFiles = {}
            # opens a file and also handles closing the file when done
            with open(dsFile) as f:
                # iterate through each line of text
                for line in f:
                    # try adds exception handling so program will not crash on errors
                    try:
                        # split line at every comma and assign each comma separated value to a variable
                        if year == 22:
                            try:
                                utc, null, hexValue, xPos, yPos = (line.split(','))
                            except:
                                print('Moderation stuff')
                                #utc, null, hexValue, xPos, yPos, xPos2, yPos2 = (line.split(','))
                        if year == 23:
                            try:
                                utc, null, xPos, yPos, hexValue = (line.split(','))
                            except:
                                print('Moderation stuff')
                        utc = utc[:23]
                        if not utc[22:].isdigit():
                            utc = utc[:22]
                            if not utc[21:].isdigit():
                                utc = utc[:21]
                                if not utc[20:].isdigit():
                                    utc = utc[:19] + '.0'
                        utc = datetime.strptime(utc, "%Y-%m-%d %H:%M:%S.%f")
                        dataFiles[line] = utc
                    except:
                        print('No pixel data')
            sortData = {k: v for k, v in sorted(dataFiles.items(), key=lambda x: x[1])}
            sortData = sortData.keys()
            with open(outFile, 'w') as f:
                for k in sortData:
                    f.write(k)
            os.remove(dsFile)

#  Check Dataset for spots that canvas size changes
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
# ------------------------------------------------ End of code to download and sort data sets

# Reads data file into a list and sends it to pygame for display
def readFile(file, dataSet, xOffset, yOffset,year,filenumber):
    # initial value for 'checkTime' which will be used to see when the dataset has moved to the next second
    checkTime = False
    loopTime = time.time()
    minLoop = 1000
    maxLoop = 0
    aveLoop = 0
    timeLoop = 0
    totalPixels = 0
    goodPixels = 0
    badPixels = 0
    # opens a file and also handles closing the file when done
    with open(file) as f:
        # iterate through each line of text
        for line in f:
            # try adds exception handling so program will not crash on errors
            try:
                totalPixels += 1
                xPos2 = False
                yPos2 = False
                # split line at every comma and assign each comma separated value to a variable
                if year == 22:
                    utc, null, hexValue, xPos, yPos = (line.split(','))
                    #try:
                    #    utc, null, hexValue, xPos, yPos = (line.split(','))
                    #except:
                    #    utc, null, hexValue, xPos, yPos, xPos2, yPos2 = (line.split(','))
                    #    totalPixels += 1
                if year == 23:
                    utc, xPos, yPos, hexValue = (line.split(','))
                    #try:
                    #    utc, null, xPos, yPos, hexValue = (line.split(','))
                    #    hexValue = hexValue.rstrip('"\n')
                    #except:
                        #utc = '2023-07-20 23:31:34.377 UTC'
                    #    null = 'shitcock'
                        #xPos, yPos, hexValue = (line.split(','))
                        #hexValue = hexValue.rstrip('"\n')

                #print(f'year={year}')
                #print(f'utc={utc}')
                #print(f'xPos={xPos}')
                #print(f'yPos={yPos}')
                #print(f'hexValue={hexValue}')
                #quit()
                # remove extra data from x & y position values and convert to integer
                xPos = int(xPos.strip('"'))
                if not yPos2:
                    if year == 22:
                        yPos = int(yPos.rstrip('"\n'))
                    if year == 23:
                        yPos = int(yPos.rstrip('"'))
                else:
                    xPos2 = int(xPos2)
                    yPos = int(yPos)
                    yPos2 = int(yPos2.rstrip('"\n'))
                # check if the current pixel being read falls within the window resolution
                if xOffset <= xPos < (X_RES + xOffset) and yOffset <= yPos < (Y_RES + yOffset):
                    goodPixels += 1
                    xPos -= xOffset
                    yPos -= yOffset
                    if xPos2:
                        if xOffset <= xPos2 < (X_RES + xOffset) and yOffset <= yPos2 < (Y_RES + yOffset):
                            goodPixels += 1
                            xPos2 -= xOffset
                            yPos2 -= yOffset
                    # break full date/time variable into smaller date and time variables
                    date, dataTime, null = utc.split()
                    # only take the first 8 characters from time to remove milliseconds
                    dataTime = dataTime[:8]
                    # split time variable into hours, minutes, seconds variables
                    hTime, mTime, sTime = dataTime.split(':')
                    # break each section of the hex value into r,g,b parts
                    r = hexValue[1] + hexValue[2]
                    g = hexValue[3] + hexValue[4]
                    b = hexValue[5] + hexValue[6]
                    # convert RGB 16 bit hex values into integers
                    rgb = [int(r, 16), int(g, 16), int(b, 16)]
                    # initialize variable pixel as class type PlacePixel
                    pixel = PlacePixel()
                    # assign information parsed from the line to the class
                    pixel.set(date, hTime, mTime, sTime, rgb, xPos, yPos)
                    # add an entry to the list with the class data
                    dataSet.append(pixel)
                    if xPos2:
                        # assign information parsed from the line to the class
                        pixel.set(date, hTime, mTime, sTime, rgb, xPos2, yPos2)
                        # add an entry to the list with the class data
                        dataSet.append(pixel)
                        print('Double entry added')
                    # check to see if the checkTime variable has been set
                    if not checkTime:
                        # if not, set it to the seconds value of current entry
                        checkTime = sTime
                    # if current entry is not from the same second as the previous ones
                    if checkTime != sTime:
                        # update checktime to the seconds value of current entry
                        checkTime = sTime
                        # send dataset to the readData function, get array of pixel info returned
                        pixelArray = readData(dataSet)
                        # send array of pixel info to the pyGame function
                        pyGame(pixelArray, getResize, filenumber)
                        # clear dataset so it doesn't get too big
                        dataSet.clear()
                        # re-add current entry as starting point of new dataset
                        dataSet.append(pixel)
                else:
                    badPixels += 1
            except ValueError:  # skips lines from the csv that do not contain pixel data
                print('\n\n'+ file)
                print(line)
            loopTime = time.time() - loopTime
            timeLoop += loopTime
            if loopTime > maxLoop:
                maxLoop = loopTime * 1000
            elif loopTime < minLoop:
                minLoop = loopTime * 1000
            loopTime = time.time()
    aveLoop = (aveLoop / totalPixels) * 1000
    print(file)
    print('%.2f ms Max loop time' % maxLoop)
    print('%.2f ms Minimum loop time' % minLoop)
    print('%.2f ms Average loop time' % aveLoop)
    print('%s Total pixels in set' % totalPixels)
    print('%s Used pixels in set' % goodPixels)
    print('%s Unused pixels in set' % badPixels)
    return dataSet

# reads pixels from the dataset and returns an array of RGB values
def readData(dataSet):
    # read through the dataset from the first pixel requested until the end of the dataset
    for x in range(len(dataSet)):
        # assign the RGB values to an X,Y position in the array
        try:
            pixelArray[dataSet[x].xPos, dataSet[x].yPos] = dataSet[x].rgb
        except:
            print(f'Error reading line {x}')
    # return array of pixel data
    return pixelArray

# loop of the game engine that displays the data to screen
def pyGame(pixelArray, savepoints, filenumber):
    # turn array of pixel values into an image buffer
    surface = pg.surfarray.make_surface(pixelArray)
    surface = pg.transform.scale(surface, (X_RES * RES_SCALE, Y_RES * RES_SCALE))
    # add the new image to the screen canvas starting at top left corner (0,0)
    screen.blit(surface, (0, 0))
    # update screen ouptut
    pg.display.flip()
    # check clock to keep maximum framerate at 60 FPS
    clock.tick(60)
    if savepoints:
        global getResize
        try:
            if filenumber in getResize:
                pg.image.save(surface, f'2023_{filenumber}.png')
                getResize.remove(filenumber)
        except:
            print(f'Error saving image for {filenumber}')

def pickSpot(year):
    global pixelArray
    firstSet = 100
    if year == 22:
        xGrid = GRID_SIZE
        yGrid = GRID_SIZE
    if year == 23:
        xGrid = GRID_SIZE23_X
        yGrid = GRID_SIZE23_Y
    xRand = random.randrange(xGrid)
    yRand = random.randrange(yGrid)
    if xRand < RAND_TOLERANCE:
        xRand = 0
    elif xRand > (xGrid - (RAND_TOLERANCE + X_RES)):
        xRand = xGrid - X_RES
    if yRand < RAND_TOLERANCE:
        yRand = 0
    elif yRand > (yGrid - (RAND_TOLERANCE + Y_RES)):
        yRand = yGrid - Y_RES
    if year == 22:
        if xRand >= ( (xGrid / 2) - (X_RES / 2) ) and yRand < ( (yGrid / 2) - (Y_RES / 2) ):
            firstSet = 113
            bg = pg.image.load('xBase.png')
            bg.convert()
            rect = (xRand, yRand, X_RES, Y_RES)
            bg = bg.subsurface(rect)
            pixelArray = pg.surfarray.array3d(bg)
            bg = pg.transform.scale(bg, (X_RES * RES_SCALE, Y_RES * RES_SCALE))
            screen.blit(bg, (0, 0))
        if yRand >= ( (GRID_SIZE / 2) - (Y_RES / 2) ):
            firstSet = 134
            bg = pg.image.load('yBase.png')
            bg.convert()
            rect = (xRand, yRand, X_RES, Y_RES)
            bg = bg.subsurface(rect)
            pixelArray = pg.surfarray.array3d(bg)
            bg = pg.transform.scale(bg, (X_RES * RES_SCALE, Y_RES * RES_SCALE))
            screen.blit(bg, (0, 0))
    if year == 23:
        if xRand > (2500 - (X_RES / 2)):
            firstSet = 138
        elif (2000 + (X_RES / 2)) > xRand > (2000 - (X_RES / 2)):
            if (500 - (Y_RES / 2)) <= yRand < (1500 - (Y_RES / 2)):
                firstSet = 109
            elif 0 < yRand < (500 - (Y_RES / 2)):
                firstSet = 121
            elif (1500 - (Y_RES / 2)) < yRand:
                firstSet = 128
        elif (1000 - (X_RES / 2)) > xRand > (500 - (X_RES / 2)):
            if (500 - (Y_RES / 2)) < yRand < (1500 - (Y_RES / 2)):
                firstSet = 115
            elif yRand < (500 - (Y_RES / 2)):
                firstSet = 121
            elif (1500 - (Y_RES / 2)) < yRand:
                firstSet = 128
        elif (500 - (X_RES / 2)) > xRand:
            if (500 - (Y_RES / 2)) < yRand < (1500 - (Y_RES / 2)):
                firstSet = 132
        if yRand < (500 - (Y_RES / 2)):
            if (500 - (X_RES / 2)) <= xRand < (2500 + (X_RES / 2)):
                firstSet = 121
            elif xRand < (500 - (X_RES / 2)):
                firstSet = 132
            else:
                firstSet = 138
        elif yRand > (1500 + (Y_RES / 2)):
            if (500 - (X_RES / 2)) <= xRand < (2500 + (X_RES / 2)):
                firstSet = 128
            elif xRand < (500 - (X_RES / 2)):
                firstSet = 132
            else:
                firstSet = 138
        if firstSet != 100:
            bg = pg.image.load(f'2023_{firstSet}.png')
            bg.convert()
            rect = (xRand, yRand, X_RES, Y_RES)
            bg = bg.subsurface(rect)
            pixelArray = pg.surfarray.array3d(bg)
            bg = pg.transform.scale(bg, (X_RES * RES_SCALE, Y_RES * RES_SCALE))
            screen.blit(bg, (0, 0))

    return xRand, yRand, firstSet

# main code loop
def main():
    # make sure end of dataset is downloaded and sorted before continuing
    if not (os.path.exists(D_SORTED + '178' + D_EXT) or os.path.exists(D_ORDERED + '178' + D_EXT)):
        # if it doesn't find the sorted version of the final dataset, check all files
        checkDataset(22,COUNT22)
    # make sure end of dataset is chronologically ordered before continuing
    if not os.path.exists(D_ORDERED + '178' + D_EXT):
        # if it doesn't find the sorted version of the final dataset, check all files
        orderDataset(22,COUNT22)
    if not os.path.exists(D_ORDERED23 + '152' + D_EXT):
        for i in range(COUNT23):
            num = str(i)
            if i < 10:
                num = '0' + str(i)
            outfile = f"{D_ORDERED23}1{num}{D_EXT}"
            if not os.path.exists(outfile):
                # Format the file number with leading zeros
                file_number = f"{i:012}"
                # Create input and output filenames
                infile = f"2023_place_canvas_history-{file_number}.csv"
                normalizeData(infile, outfile, 23)
    # create empty list to store info from the dataset
    dataSet = []
    # pygame variable to exit loop
    running = True
    # start of pygame loop
    while running:
        global RES_SCALE
        global X_RES
        global Y_RES
        global pixelArray
        pickyear=random.randrange(22,24)
        if pickyear == 22:
            rangeyear = 179
        if pickyear == 23:
            rangeyear = 153
        RES_SCALE = random.randrange(0,MAX_SCALE)
        if RES_SCALE == 0:
            RES_SCALE = random.randrange(0,MAX_SCALE)
            if RES_SCALE == 0:
                RES_SCALE = 0.5
        X_RES = round(NATIVE_X_RES / RES_SCALE)
        Y_RES = round(NATIVE_Y_RES / RES_SCALE)
        # create array for pixels and set default to white
        pixelArray = np.full((X_RES, Y_RES, 3), 255)
        xOffset, yOffset, firstSet = pickSpot(pickyear)
        if getResize:
            xOffset=0
            yOffset=0
            RES_SCALE = 1
            X_RES = GRID_SIZE23_X
            Y_RES = GRID_SIZE23_Y
            pixelArray = np.full((X_RES, Y_RES, 3), 255)
            firstSet = 100
            rangeyear = 153
            pickyear = 23
        # loop through ds values of 100-178 (always stops before end value). Since we made our filenames start at 100,
        # we don't need to do any additional padding for numbers below 10 and can just convert all values to strings
        for ds in range(firstSet, rangeyear):
            # make string of our new filename plus current number plus extension
            if pickyear == 22:
                dsFile = D_ORDERED + str(ds) + D_EXT
            if pickyear == 23:
                dsFile = D_ORDERED23 + str(ds) + D_EXT
            # checks to see if data file exists before running function
            if os.path.exists(dsFile):
                setTime = time.time()
                print(pickyear)
                # sends the filename to the readFile function for processing and display
                dataSet = readFile(dsFile, dataSet, xOffset, yOffset, pickyear, ds)
                setTime = time.time() - setTime
                print('Dataset processed in %s seconds' % setTime)

# python way of checking if this is the main program, i.e. this code isn't being called from 'import xxx'
if __name__ == '__main__':
    # calls the main loop, this is the line that actually starts the program moving
    main()
