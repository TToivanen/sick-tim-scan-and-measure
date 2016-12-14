# TiMmy: a tool to plot and measure object width using Sick TiM
# series 2D scanners
# Copyright (C) 2016 Toni Toivanen

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import math
import tkinter
import time
import sys

maxDist = 600
minDist = 50

scale = 0.6

def readFile(src): #palauttaa tiedot listana

    try:
        file = open(src, "r") #Avataan tied. lukua varten
        try:
            data = [] #Lista
            while True:
                line = file.readline()
                line = line.replace("\n", "")
                line = line.replace("\"", "")
                line = line.strip() #Siivotaan \n-merkit
                #print(line)
                if len(line) == 0:
                    break
                data.append(line) #LisÃ¤tÃ¤Ã¤n listan alkioksi
                
        except IOError:
            print("Tiedoston lukeminen ei onnistunut!")
        finally:
            file.close() #Sulje tiedosto
    except IOError:
        print("Tiedoston avaaminen ei onnistunut!")

    return data

def clean(data):

    listFoo = []
    
    for line in data:
        for i in line.split(" "):
            listFoo.append(str(i.strip()))

    #print(listFoo)

    return listFoo

def parse(data):

    list0 = []
    # print(data)
    startPos = len(data) - 690
    endPos = len(data) - 120
    for i in range(startPos+1, endPos):
        try:
            line = int(data[i], 16) # base conversion
        except IOError:
            line = 0
        line = str(line)
        list0.append(line)
    
    return list0 # nyt lista etÃ¤isyyksistÃ¤ millimetreinÃ¤
    
def main():
	data = readFile("data.log")
	data = clean(data)
	data = parse(data)
	makeGui(data)
	# draw(data)

def measure(x, v):

    n = 200

    particleFilterTreshold = 3

    x2 = []
    sorted(x)
    
    for i in range(0,len(x)-1):
        if abs(x[i] - x[i+1]) < particleFilterTreshold:
            x2.append(x[i])
        
    minX = min(x2)
    maxX = max(x2)
    a = (maxX - minX)/scale
    v.append(a)
##    print('x',str(len(x)))
##    print('x2',str(len(x2)))
    # print(len(v))

    if len(v) < n:
        res = -1
    else:
        sSum = 0
        for i in range(len(v)-n,len(v)):
            sSum = sSum + v[i]
        res = sSum/n
        print('Kappaleen leveys: ', res)
        sys.exit('program end')

    return res
	
def makeGui(data):

    h = 800
    w = 800
    v = []
    
    xUpdate = True

    updateRate = 10 # päivityksen väli ms

    def update():

        canvas.delete("all")

        coord = (w/2 - maxDist*scale,
            h/2 - maxDist*scale,
            w/2 + maxDist*scale,
            h/2 + maxDist*scale)
        rangeArc = canvas.create_arc(coord,
                                     start=0,
                                     extent=180,
                                     fill= 'darkgrey')

        
        scanner = canvas.create_oval((w/2) - 8,
                             (h/2) + 8,
                             (w/2) + 8,
                             (h/2) - 8,
                             fill = 'blue')

        data = readFile("data.log")
        data = clean(data)
        data = parse(data)

        angle = 0

        x = []
        y = []

        #pixel = 0.254

        lenV = []
        
        for i in range(2,len(data)):

            scanAreaWidth = 1100
            scanAreaHeight = 300
            distanceFromScanner = 150

            x1 = w/2 - (scanAreaWidth/2)*scale
            y1 = h/2 - (scanAreaHeight + distanceFromScanner)*scale
            x2 = w/2 + (scanAreaWidth/2)*scale
            y2 = h/2 - distanceFromScanner*scale

            if int(data[i]) < maxDist and int(data[i]) > minDist:
                xPos = h/2 + int(data[i])*math.cos(math.radians(angle))*scale
                yPos = w/2 + int(data[i])*math.sin(math.radians(angle))*scale

                scanArea = canvas.create_rectangle(x1,
                                                y1,
                                                x2,
                                                y2)
                
                # y.append(yPos)

                if xPos > x1 and xPos < x2 and yPos > y1 and yPos < y2:
                    x.append(xPos)
                    mDot = canvas.create_oval(xPos-3,
                                              yPos-3,
                                              xPos+3,
                                              yPos+3,
                                              fill = 'red')
                else:
                    mDot = canvas.create_oval(xPos-3,
                                              yPos-3,
                                              xPos+3,
                                              yPos+3,
                                              fill = 'grey')
                    
                

            angle = angle - 0.33333

        widthVar.set('Measured object width: ' + str(measure(x, v)))
        
        if xUpdate:
            top.after(updateRate, update)
    
    top = tkinter.Tk()

    rangeVar = tkinter.StringVar()
    tMaxRange = tkinter.Label(top,
                              textvariable = rangeVar,
                              anchor = tkinter.W)
    
    rangeVar.set('Maximum range setting: ' + str(maxDist))
    tMaxRange.pack()

    widthVar = tkinter.StringVar()
    tMaxRange = tkinter.Label(top,
                              textvariable = widthVar,
                              anchor = tkinter.W)
    
    tMaxRange.pack()
    
    
    canvas = tkinter.Canvas(top, # tausta
                            bg = 'grey',
                            height = h,
                            width = h)
    canvas.pack(ipady=3)

    top.after(updateRate, update)
    top.mainloop()
    
main()
