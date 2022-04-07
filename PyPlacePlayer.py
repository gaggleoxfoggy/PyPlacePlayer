'''
PyPlacePlayer

P-Trip is a program to read from the reddit.com/r/place dataset and display
the information to the screen as a timelapse.
'''
#imports additiona python packages to handle complex functions
import numpy as np
import pygame as pg

#static constants
X_RES = 800
Y_RES = 600

#initial config for pygame
pg.init()
screen = pg.display.set_mode((X_RES, Y_RES))
clock = pg.time.Clock()

#create array for pixels and set default to white
pixelArray = np.full( (X_RES, Y_RES, 3), 255)

#class to organize information from each pixel in the dataset
class PlacePixel:

    #method to set values for pixel
    def set(self, date, hTime, mTime, sTime, rgb, xPos, yPos):
        self.date = date
        self.hTime = int(hTime)
        self.mTime = int(mTime)
        self.sTime = int(sTime)
        self.rgb = rgb
        self.xPos = xPos
        self.yPos = yPos

# Reads data file into a list
def readFile(file):
    dataSet = []
    with open(file, 'r') as f:
        for line in f.readlines():
            try:
                #assign each comma seperated value to a variable
                utc, null, hexValue, xPos, yPos = (line.split(','))
                #break full date/time variable into smaller date and time variables
                date, time, null = utc.split()
                #only take the first 8 characters from time to remove milliseconds
                time = time[:8]
                #split time variable into hours, minutes, seconds variables
                hTime, mTime, sTime = time.split(':')
                #break each section of the hex value into r,g,b parts
                r = hexValue[1] + hexValue[2]
                g = hexValue[3] + hexValue[4]
                b = hexValue[5] + hexValue[6]
                #convert RGB 16 bit hex values into 8 bit integer
                rgb = [int(r, 16), int(g, 16), int(b, 16)]
                #remove extra data from x & y position values and convert to integer
                xPos = int(xPos.strip('"'))
                yPos = int(yPos.rstrip('"\n'))
                #initialize variable pixel as class type PlacePixel
                pixel = PlacePixel()
                #assign information parsed from the line to the class
                pixel.set(date, hTime, mTime, sTime, rgb, xPos, yPos)
                #add an entry to the list with the class data
                dataSet.append(pixel)
            except ValueError: #skips lines from the csv that do not contain pixel data
                print('No values')
    #return list with dataSet
    return dataSet

#reads pixels from the dataset and returns an array of RGB values
def readData(dataSet, start):
    #read the time value in seconds of the first pixel to be read
    timeCheck = dataSet[start].sTime
    #read through the dataset from the first pixel requested until the end of the dataset
    for x in range(start, len(dataSet)):
        #check to see if this pixel was placed during the same second as the initial pixel requested
        if dataSet[x].sTime != timeCheck:
            #if data is from a different second, pass the current pixel back to be the next starting point
            start = x
            break #ends the for loop
        #check if the current pixel being read falls within the window resolution
        if 0 <= dataSet[x].xPos < X_RES and 0 <= dataSet[x].yPos < Y_RES:
            #assign the RGB values to an X,Y position in the array
            pixelArray[dataSet[x].xPos, dataSet[x].yPos] = dataSet[x].rgb
    #return array of pixel data and starting index of next pixel
    return pixelArray, start

#main loop of the game engine that displays the data to screen
def pyGame(dataSet):
    #initialize variable to start at first pixel of the dataset
    start = 0
    #code to start the pygame loop and help it exit smoothly
    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
        #passes the dataset and starting index to the readData function
        #and returns the output of the pixelArray and new starting index
        pixelArray, start = readData(dataSet, start)
        #pygame code to turn the pixelArray into an image to display
        surface = pg.surfarray.make_surface(pixelArray)
        #puts the image onto the screen starting at the origin (0,0 is the top left of the screen)
        screen.blit(surface, (0, 0))
        #draws the output to screen
        pg.display.flip()
        #pygame code to lock framerate to max of 60 FPS
        clock.tick(60)

#main code loop
def main():
    #sends the filename to the readFile function and returns output to variable dataSet
    dataSet = readFile('2022_place_canvas_history-000000000000.csv')
    #passes dataSet to pyGame loop for processing
    pyGame(dataSet)

#python way of checking if this is the main program, i.e. this code isn't being called from 'import xxx'
if __name__ == '__main__':
    #calls the main loop, this is the line that actually starts the program moving
    main()
