import math
from copy import deepcopy
from tkinter import *

CanvasWidth = 400
CanvasHeight = 400
d = 500

RotationStepSize = 5
TranslationStepSize = 5
ScaleStepSize = 0.1


# ***************************** Initialize Pyramid Object ***************************
# Definition of the five underlying points
apex = [0,50,100]
base1 = [-50,-50,50]
base2 = [50,-50,50]
base3 = [50,-50,150]
base4 = [-50,-50,150]

# Definition of the five polygon faces using the meaningful point names
# Polys are defined in counter clockwise order when viewed from the outside
frontpoly = [apex,base1,base2]
rightpoly = [apex,base2,base3]
backpoly = [apex,base3,base4]
leftpoly = [apex,base4,base1]
bottompoly = [base4,base3,base2,base1]

# Definition of the object
Pyramid = [bottompoly, frontpoly, rightpoly, backpoly, leftpoly]

# Definition of the Pyramid's underlying point cloud.  No structure, just the points.
PyramidPointCloud = [apex, base1, base2, base3, base4]

# A copy of our input data for resetting later
rPyramidPointCloud = deepcopy(PyramidPointCloud)
#************************************************************************************

# This function resets the pyramid to its original size and location in 3D space
# by copying the value of each element from our backup to our shape definition
def resetPyramid():
    for i in range(len(PyramidPointCloud)):                    #for point in our cloud (5 loops)
        for j in range(len(PyramidPointCloud[i])):             #for each dimension value (3 loops)
            PyramidPointCloud[i][j] = rPyramidPointCloud[i][j] #reset each value from our backup

# This function translates an object by some displacement.  The displacement is a 3D
# vector so the amount of displacement in each dimension can vary.
def translate(object, displacement):
    print("translate stub executed.")
    for i in range(len(object)):                        #for every point (5 loops)
        for j in range(len(object[i])):                 #for each dimension value (3 loops)
            object[i][j] = object[i][j]+displacement[j] #add our displacement value to the current location
    
# This function performs a simple uniform scale of an object assuming the object is
# centered at the origin.  The scalefactor is a scalar.
def scale(object,scalefactor):
    print("scale stub executed.")
    for i in range(len(object)):                        #for every point (5 loops)
        for j in range(len(object[i])):                 #for each dimension value (3 loops)
            object[i][j] = object[i][j]*scalefactor     #multiply currrent values by the scale factor

# This function performs a rotation of an object about the Z axis (from +X to +Y)
# by 'degrees', assuming the object is centered at the origin.  The rotation is CCW
# in a LHS when viewed from -Z [the location of the viewer in the standard postion]
def rotateZ(object,degrees):
    radians = math.radians(degrees) #convert degrees to radians
    for i in range(len(object)):
        object[i][0] = object[i][0]*math.cos(radians)-object[i][1]*math.sin(radians)
        object[i][1] = object[i][0]*math.sin(radians)+object[i][1]*math.cos(radians)
    
# This function performs a rotation of an object about the Y axis (from +Z to +X)
# by 'degrees', assuming the object is centered at the origin.  The rotation is CW
# in a LHS when viewed from +Y looking toward the origin.
def rotateY(object,degrees):
    radians = math.radians(degrees) #convert degrees to radians
    for i in range(len(object)):
        object[i][0] = object[i][0]*math.cos(radians)+object[i][2]*math.sin(radians)
        object[i][2] = -object[i][0]*math.sin(radians)+object[i][2]*math.cos(radians)

# This function performs a rotation of an object about the X axis (from +Y to +Z)
# by 'degrees', assuming the object is centered at the origin.  The rotation is CW
# in a LHS when viewed from +X looking toward the origin.
def rotateX(object,degrees):
    radians = math.radians(degrees) #convert degrees to radians
    for i in range(len(object)):
        object[i][1] = object[i][1]*math.cos(radians)-object[i][2]*math.sin(radians)
        object[i][2] = object[i][1]*math.sin(radians)+object[i][2]*math.cos(radians)

# The function will draw an object by repeatedly callying drawPoly on each polygon in the object
def drawObject(object):
    for poly in object:
        drawPoly(poly)

# This function will draw a polygon by repeatedly callying drawLine on each pair of points
# making up the object.  Remember to draw a line between the last point and the first.
def drawPoly(poly):
    for i in range(len(poly)):
        if i==len(poly)-1:
            drawLine(poly[i],poly[0])
        else:
            drawLine(poly[i],poly[i+1])

def testo():
    w.create_line(0,0,100,100)

# Project the 3D endpoints to 2D point using a perspective projection implemented in 'project'
# Convert the projected endpoints to display coordinates via a call to 'convertToDisplayCoordinates'
# draw the actual line using the built-in create_line method
def drawLine(start,end):
    startdisplay = convertToDisplayCoordinates(project(start))
    enddisplay = convertToDisplayCoordinates(project(end))
    w.create_line(startdisplay[0],startdisplay[1],enddisplay[0],enddisplay[1])

# This function converts from 3D to 2D (+ depth) using the perspective projection technique.  Note that it
# will return a NEW list of points.  We will not want to keep around the projected points in our object as
# they are only used in rendering
def project(point):
    ps = []
    ps.append((d*point[0])/(-d+point[2]))
    ps.append((d*point[1])/(-d+point[2]))
    return ps

# This function converts a 2D point to display coordinates in the tk system.  Note that it will return a
# NEW list of points.  We will not want to keep around the display coordinate points in our object as 
# they are only used in rendering.
def convertToDisplayCoordinates(point):
    displayXY = []
    displayXY.append(0.5*CanvasWidth+point[0])
    displayXY.append(0.5*CanvasHeight+point[1])
    return displayXY
    

# **************************************************************************
# Everything below this point implements the interface
def reset():
    w.delete(ALL)
    resetPyramid()
    drawObject(Pyramid)

def larger():
    w.delete(ALL)
    scale(PyramidPointCloud,1+ScaleStepSize)
    drawObject(Pyramid)

def smaller():
    w.delete(ALL)
    scale(PyramidPointCloud,1-ScaleStepSize)
    drawObject(Pyramid)

def forward():
    w.delete(ALL)
    translate(PyramidPointCloud,[0,0,-TranslationStepSize])
    drawObject(Pyramid)

def backward():
    w.delete(ALL)
    translate(PyramidPointCloud,[0,0,TranslationStepSize])
    drawObject(Pyramid)

def left():
    w.delete(ALL)
    translate(PyramidPointCloud,[TranslationStepSize,0,0])
    drawObject(Pyramid)

def right():
    w.delete(ALL)
    translate(PyramidPointCloud,[-TranslationStepSize,0,0])
    drawObject(Pyramid)

def up():
    w.delete(ALL)
    translate(PyramidPointCloud,[0,TranslationStepSize,0])
    drawObject(Pyramid)

def down():
    w.delete(ALL)
    translate(PyramidPointCloud,[0,-TranslationStepSize,0])
    drawObject(Pyramid)

def xPlus():
    w.delete(ALL)
    rotateX(PyramidPointCloud,RotationStepSize)
    drawObject(Pyramid)

def xMinus():
    w.delete(ALL)
    rotateX(PyramidPointCloud,-RotationStepSize)
    drawObject(Pyramid)

def yPlus():
    w.delete(ALL)
    rotateY(PyramidPointCloud,RotationStepSize)
    drawObject(Pyramid)

def yMinus():
    w.delete(ALL)
    rotateY(PyramidPointCloud,-RotationStepSize)
    drawObject(Pyramid)

def zPlus():
    w.delete(ALL)
    rotateZ(PyramidPointCloud,RotationStepSize)
    drawObject(Pyramid)

def zMinus():
    w.delete(ALL)
    rotateZ(PyramidPointCloud,-RotationStepSize)
    drawObject(Pyramid)

root = Tk()
outerframe = Frame(root)
outerframe.pack()

w = Canvas(outerframe, width=CanvasWidth, height=CanvasHeight)
drawObject(Pyramid)
w.pack()

controlpanel = Frame(outerframe, height=400)
controlpanel.pack()

resetcontrols = Frame(controlpanel, height=400, borderwidth=2, relief=RIDGE)
resetcontrols.pack(side=TOP)

resetButton = Button(resetcontrols, text="Reset", fg="green", command=reset)
resetButton.pack(side=LEFT)

scalecontrols = Frame(controlpanel, borderwidth=4, relief=RIDGE)
scalecontrols.pack(side=LEFT)

scalecontrolslabel = Label(scalecontrols, text="Scale")
scalecontrolslabel.pack()

largerButton = Button(scalecontrols, text="Larger", command=larger)
largerButton.pack(side=TOP)

smallerButton = Button(scalecontrols, text="Smaller", command=smaller)
smallerButton.pack(side=BOTTOM)

translatecontrols = Frame(controlpanel, borderwidth=4, relief=RIDGE)
translatecontrols.pack(side=LEFT)

translatecontrolslabel = Label(translatecontrols, text="Translation")
translatecontrolslabel.pack()

translatecontrolsupper = Frame(translatecontrols)
translatecontrolsupper.pack()

translatecontrolslower = Frame(translatecontrols)
translatecontrolslower.pack()

backwardButton = Button(translatecontrolsupper, text="⟱", command=backward)
backwardButton.pack(side=LEFT)

upButton = Button(translatecontrolsupper, text="↑", command=up)
upButton.pack(side=LEFT)

forwardButton = Button(translatecontrolsupper, text="⟰", command=forward)
forwardButton.pack(side=LEFT)

leftButton = Button(translatecontrolslower, text="←", command=left)
leftButton.pack(side=LEFT)

upButton = Button(translatecontrolslower, text="↓", command=down)
upButton.pack(side=LEFT)

rightButton = Button(translatecontrolslower, text="→", command=right)
rightButton.pack(side=LEFT)

rotationcontrols = Frame(controlpanel, borderwidth=4, relief=RIDGE)
rotationcontrols.pack(side=LEFT)

rotationcontrolslabel = Label(rotationcontrols, text="Rotation")
rotationcontrolslabel.pack()

rotationcontrolsx = Frame(rotationcontrols)
rotationcontrolsx.pack(side=LEFT)

rotationcontrolsy = Frame(rotationcontrols)
rotationcontrolsy.pack(side=LEFT)

rotationcontrolsz = Frame(rotationcontrols)
rotationcontrolsz.pack(side=LEFT)

xPlusButton = Button(rotationcontrolsx, text="X+", command=xPlus)
xPlusButton.pack(side=TOP)

xMinusButton = Button(rotationcontrolsx, text="X-", command=xMinus)
xMinusButton.pack(side=BOTTOM)

yPlusButton = Button(rotationcontrolsy, text="Y+", command=yPlus)
yPlusButton.pack(side=TOP)

yMinusButton = Button(rotationcontrolsy, text="Y-", command=yMinus)
yMinusButton.pack(side=BOTTOM)

zPlusButton = Button(rotationcontrolsz, text="Z+", command=zPlus)
zPlusButton.pack(side=TOP)

zMinusButton = Button(rotationcontrolsz, text="Z-", command=zMinus)
zMinusButton.pack(side=BOTTOM)

root.mainloop()