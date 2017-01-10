########################################################################################################################
#
#   Ryan Walters
#   101-60-902
#   1/9/16
#
#   Assignment 2:
#   This program draws three dimensional objects and manipulates them,
#   projecting results into a 2d plane so that it is viewable on a screen.
#
#   Currently can scale, rotate, and translate objects. All of which
#   can be done at different magnitudes.
#
#   It can have multiple objects on screen, with multiple objects being able to be selected at once.
#   It can perform manipulations both in place and from origin by toggling the use of world-space coordinates.
#   User can create, delete, manipulate and select any number of objects.
#   There are currently pyramids and cubes implemented.
#
########################################################################################################################

"""
UI Guide:

*** FEEL FREE TO MAXIMIZE THE WINDOW. THIS PROGRAM FULLY SUPPORTS WINDOW SCALING.

In the center of the screen is the viewport. Meshes created are displayed here. Selected meshes are highlighted in red.
All actions you perform on an mesh are performed on all selected meshes.

The white box on the left lists all of the meshes in the world using a friendly name. you can click on the names of
meshes to select them and can drag+click, control+click, or shift+click to select multiple meshes at once. Above this
box are buttons to create and delete meshes.

At the bottom of the screen is the manipulation toolbar:
    *** ALL OF THESE BUTTONS CAN BE HELD DOWN TO GO FASTER

    * The "Reset" button resets meshes to original scale, position, and rotation
    * The "Use World-Space Coordinates" checkbox disables local rotations for the meshes

    * Use the "Scale" button to scale meshes by the multiplier shown to the left of it.
    * You can increase and decrease this multiplier using the arrow buttons.
    ** Clicking on the current multiplier text between the arrow buttons will reset the multiplier to default

    * Use the "Translation" buttons to translate meshes in the button's direction by the number of units to the left.
    * You can increase and decrease the number of units translated each click by using the arrow buttons.
    ** Clicking on the current unit size text between the arrow buttons will reset the number of units to default

    * Use the "Rotation" buttons to rotate meshes in the button's axis rotation vector by the degrees to the left.
    * You can increase and decrease the number of degrees rotated each click by using the arrow buttons.
    ** Clicking on the current number of degrees between the arrow buttons will reset the degrees to default.
"""

import math
from copy import deepcopy
from tkinter import *

CanvasWidth = 400
CanvasHeight = 400
d = 500

# these are added so that we can transform by varying amounts
RotationStepSize = 5
TranslationStepSize = 5
ScaleStepSize = 1.00

# keep track of our meshes
selectedMeshes = []
allMeshes = []
meshNames = []
numMeshesCreated = 0

# stands for Not In-Place. If true, we use world-coordinate system for transformations rather than local
NIP = False


# **************************************************************************
# Our mesh object class. All meshes that we create are defined by this class. This class contains the variables and
# functions that define translations and drawings of the meshes in the engine
class Mesh:

    # These are the basic matrices  that are used for transformations. Only the indexes with a '2' need to be altered.
    translationMatrix = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [2, 2, 2, 1]]
    scalingMatrix = [[2, 0, 0, 0], [0, 2, 0, 0], [0, 0, 2, 0], [0, 0, 0, 1]]

    xRotMatrix = [[1, 0, 0, 0], [0, 2, 2, 0], [0, 2, 2, 0], [0, 0, 0, 1]]
    yRotMatrix = [[2, 0, 2, 0], [0, 1, 0, 0], [2, 0, 2, 0], [0, 0, 0, 1]]
    zRotMatrix = [[2, 2, 0, 0], [2, 2, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]

    # Need an initializer for variables. If variables are defined above this line (like our matrices), altering them in
    # one instantiated object alters them for every instantiated object. Not what we want
    def __init__(self):
        self.polyList = []  # List of polygon faces defined in counter clockwise order when viewed from the outside
        self.pointList = []  # Definition of the underlying points
        self.pointCloud = []  # Definition of the Pyramid's underlying point cloud.  No structure, just the points.
        self.rPointCloud = []  # A copy of our input data for resetting later
        self.meshDef = []  # Definition of the object

        self.midpoint = [0, 0, 0, 1]  # location of the mesh's pivot
        # use these for determining the bounds of the object. Useful for finding midpoint
        self.smallest = [0, 0, 0, 1]  # stores the most negative of all the points' values
        self.largest = [0, 0, 0, 1]  # stores the most negative of all the points' values

    # make a backup of the locations of the points so we can easily reset the mesh's position
    def initPointCloud(self):
        self.rPointCloud = deepcopy(self.pointCloud)

    # called upon object creation. Determine starting midpoint.
    def findMidpoint(self):
        for i in self.pointCloud:  # for every point,
            for j in range(len(self.pointCloud[0])):  # for every dimension in the point vector
                if i[j] < self.smallest[j]:  # keep track of the smallest number in each dimension
                    self.smallest[j] = i[j]
                if i[j] > self.largest[j]:  # keep track of the largest number in each dimension
                    self.largest[j] = i[j]

        # using the smallest and largest numbers in each dimension, calculate the midpoint by taking the averages
        for i in range(len(self.midpoint)):
            self.midpoint[i] = ((self.largest[i] + self.smallest[i]) / 2)

    # Resets the pyramid to its original size and location in 3D space
    # by copying the value of each element from our backup to our point cloud
    def resetMesh(self):
        for i in range(len(self.pointCloud)):  # for point in our cloud
            for j in range(len(self.pointCloud[i])):  # for each dimension value
                self.pointCloud[i][j] = self.rPointCloud[i][j]  # reset each value from our backup
        self.midpoint = [0, 0, 0, 1]  # place our pivot at the origin

    # This function translates an object by some displacement.  The displacement is a 3D
    # vector so the amount of displacement in each dimension can vary.
    def translate(self, displacement):
        # grab a copy of the matrices needed for translation
        matrix = deepcopy(self.translationMatrix)
        answer = deepcopy(self.pointCloud)

        # make the bottom 3 values in our matrix equal to the displacement we want
        for i in range(0, 3):
            matrix[3][i] = displacement[i]

        # do our matrix multiplication for every point in our mesh. We store it in answer then transfer it to pointcloud
        # element by element because it doesn't work otherwise.
        for i in range(len(self.pointCloud)):
            answer[i] = vectorMatrixMult(self.pointCloud[i], matrix)
            for j in range(len(answer[i])-1):
                self.pointCloud[i][j] = answer[i][j]

        # displace the midpoint as well
        for j in range(0,3):
            self.midpoint[j] += displacement[j]

    # This function performs a simple uniform scale of an object using the origin as the pivot. Scalefactor is scalar
    # TODO: if we ever want stretching we need scalefactor to be a vector
    def scaleNIP(self, scalefactor):
        # grab a copy of the matrices needed for scaling
        matrix = deepcopy(self.scalingMatrix)
        answer = deepcopy(self.pointCloud)

        # Make the matrix's diagonal equal to the scalefactor
        for i in range(0, 3):
            matrix[i][i] = scalefactor

        # since the scaling pivot is not the midpoint of the mesh, the midpoint maya move. Therefore, calculate how much
        # one point is displaced so we can apply the same displacement to the midpoint of the mesh
        answer[0] = vectorMatrixMult(self.pointCloud[0], matrix)
        for i in range(len(self.midpoint)):
            self.midpoint[i] = self.midpoint[i] - (self.pointCloud[0][i] - answer[0][i])

        # do our matrix multiplication for every point in our mesh. We store it in answer then transfer it to pointcloud
        # element by element because it doesn't work otherwise.
        for i in range(len(self.pointCloud)):
            answer[i] = vectorMatrixMult(self.pointCloud[i], matrix)
            for j in range(len(answer[i])):
                self.pointCloud[i][j] = answer[i][j]

    # scale mesh using the mesh's pivot as the scaling pivot. Scalefactor is a scalar
    def scale(self, scalefactor):
        global NIP
        # if we are using world-space coordinates, use the other scaling function
        if NIP:
            self.scaleNIP(scalefactor)
        else:
            # grab a copy of the matrices needed for scaling
            answer = deepcopy(self.pointCloud)
            matrix = deepcopy(self.scalingMatrix)

            # The composite matrix can be easily defined without multiplying matrices by replacing the translation
            # parts of the matrix with [pivot*(1-scalefactor)]
            for i in range(0, 3):
                matrix[3][i] = self.midpoint[i]*(1-scalefactor)
                matrix[i][i] = scalefactor

            # do our matrix multiplication for every point in our mesh. We store it in answer then transfer it to
            # pointcloud element by element because it doesn't work otherwise.
            for i in range(len(self.pointCloud)):
                answer[i] = vectorMatrixMult(self.pointCloud[i], matrix)
                for j in range(len(answer[i])):
                    self.pointCloud[i][j] = answer[i][j]

    # this function rotates a mesh, either by transferring inputs to separate functions if using world-space coords, or
    # by performing the seven steps to calculate a composite matrix and multiplying the input vector by that. It takes
    # a scalar, degrees, and a string, axis, which tells the function which way to rotate the mesh.
    def rotateMesh(self, degrees, axis):
        global NIP
        # if using world-space coordinates, send input to other functions, one for each axis of rotation
        if NIP:
            if axis == 'x':
                self.rotateXNIP(degrees)
            elif axis == 'y':
                self.rotateYNIP(degrees)
            elif axis == 'z':
                self.rotateZNIP(degrees)
        else:
            radians = math.radians(-degrees)  # convert degrees to radians
            # grab a copy of the matrices needed for rotation
            transmatrix = deepcopy(self.translationMatrix)
            answer = deepcopy(self.pointCloud)

            # get our pivot then add the largest bounds to it to create the rotation vector. The largest bounds
            # insures that the vector's origin will be outside of the mesh
            p1 = deepcopy(self.midpoint)
            p1[2] += self.largest[2]

            # steps 1 and 7 are translations, so we will have a copy of the base translation matrix for each
            step1 = deepcopy(transmatrix)
            step7 = deepcopy(transmatrix)
            # step 1 needs to be negative displacement, as we need to translate it to the origin
            for i in range(0, 3):
                step1[3][i] = -self.midpoint[i]
                step7[3][i] = self.midpoint[i]

            # calculate our variables for math
            a = self.midpoint[0] - p1[0]  # a = x2 - x1
            b = self.midpoint[1] - p1[1]  # b = y2 - y1
            c = self.midpoint[2] - p1[2]  # c = z2 - z1
            p = math.sqrt(b ** 2 + c ** 2)  # p = sqrt(b^2 + c^2)
            l = math.sqrt(a ** 2 + b ** 2 + c ** 2)  # l = sqrt(a^2 + b^2 + c^2)

            # matrices used for steps 2 and 3
            step2 = [[1,    0,   0, 0],
                     [0,  c/p, b/p, 0],
                     [0, -b/p, c/p, 0],
                     [0,    0,   0, 1]]

            step3 = [[p/l, 0, -a/l, 0],
                     [0,   1,    0, 0],
                     [a/l, 0,  p/l, 0],
                     [0,   0,    0, 1]]

            # step 4 is the actual rotation we are calculating, so we use a different matrix depending on the axis of
            # rotation. The matrices only differ in position and sign of the cosines and sines. So we grab a copy of
            # the base rotation matrices for each rotation axis and set them up.
            if axis == 'z':
                radians = -radians
                step4 = deepcopy(self.zRotMatrix)
                step4[0][0] = math.cos(radians)
                step4[0][1] = math.sin(radians)
                step4[1][0] = -math.sin(radians)
                step4[1][1] = math.cos(radians)
            elif axis == 'y':
                step4 = deepcopy(self.yRotMatrix)
                step4[0][0] = math.cos(radians)
                step4[0][2] = -math.sin(radians)
                step4[2][0] = math.sin(radians)
                step4[2][2] = math.cos(radians)
            else:
                step4 = deepcopy(self.xRotMatrix)
                step4[1][1] = math.cos(radians)
                step4[1][2] = math.sin(radians)
                step4[2][1] = -math.sin(radians)
                step4[2][2] = math.cos(radians)

            # steps 5 and six are the reversal of 2 and 3
            step5 = [[p/l,  0, a/l, 0],
                     [0,    1,   0, 0],
                     [-a/l, 0, p/l, 0],
                     [0,    0,   0, 1]]

            step6 = [[1,   0,    0, 0],
                     [0, c/p, -b/p, 0],
                     [0, b/p,  c/p, 0],
                     [0,   0,    0, 1]]

            # compute the composite matrix by multiplying each matrix in the order that we want to perform the steps.
            matrix = matrixMult4x4(step1, step2)
            matrix = matrixMult4x4(matrix, step3)
            matrix = matrixMult4x4(matrix, step4)
            matrix = matrixMult4x4(matrix, step5)
            matrix = matrixMult4x4(matrix, step6)
            matrix = matrixMult4x4(matrix, step7)

            # do our matrix multiplication for every point in our mesh. We store it in answer then transfer it to
            # pointcloud element by element because it doesn't work otherwise.
            for i in range(len(self.pointCloud)):
                answer[i] = vectorMatrixMult(self.pointCloud[i], matrix)
                for j in range(len(answer[i])):
                    self.pointCloud[i][j] = answer[i][j]

            # calculate the displacement of the pivot of our mesh
            self.midpoint = vectorMatrixMult(self.midpoint, matrix)

    # This function performs a rotation of an object about the Z axis (from +X to +Y)
    # by 'degrees', using the origin as the pivot.  The rotation is CCW
    # in a LHS when viewed from -Z [the location of the viewer in the standard postion]
    def rotateZNIP(self, degrees):
        radians = math.radians(-degrees)  # convert degrees to radians
        # grab a copy of the matrices needed for z rotation
        matrix = deepcopy(self.zRotMatrix)
        answer = deepcopy(self.pointCloud)

        # calculate the sines and cosines for insertion in the matrix
        matrix[0][0] = math.cos(radians)
        matrix[0][1] = math.sin(radians)
        matrix[1][0] = -math.sin(radians)
        matrix[1][1] = math.cos(radians)

        # do our matrix multiplication for every point in our mesh. We store it in answer then transfer it to
        # pointcloud element by element because it doesn't work otherwise.
        for i in range(len(self.pointCloud)):
            answer[i] = vectorMatrixMult(self.pointCloud[i], matrix)
            for j in range(len(answer[i])):
                self.pointCloud[i][j] = answer[i][j]

        # calculate the displacement of the pivot of our mesh
        self.midpoint = vectorMatrixMult(self.midpoint, matrix)

    # This function performs a rotation of an object about the Y axis (from +Z to +X)
    # by 'degrees', using the origin as the pivot.  The rotation is CW
    # in a LHS when viewed from +Y looking toward the origin.
    def rotateYNIP(self, degrees):
        radians = math.radians(degrees)  # convert degrees to radians
        # grab a copy of the matrices needed for z rotation
        matrix = deepcopy(self.yRotMatrix)
        answer = deepcopy(self.pointCloud)

        # calculate the sines and cosines for insertion in the matrix
        matrix[0][0] = math.cos(radians)
        matrix[0][2] = -math.sin(radians)
        matrix[2][0] = math.sin(radians)
        matrix[2][2] = math.cos(radians)

        # do our matrix multiplication for every point in our mesh. We store it in answer then transfer it to
        # pointcloud element by element because it doesn't work otherwise.
        for i in range(len(self.pointCloud)):
            answer[i] = vectorMatrixMult(self.pointCloud[i], matrix)
            for j in range(len(answer[i])):
                self.pointCloud[i][j] = answer[i][j]

        # calculate the displacement of the pivot of our mesh
        self.midpoint = vectorMatrixMult(self.midpoint, matrix)

    # This function performs a rotation of an object about the X axis (from +Y to +Z)
    # by 'degrees', using the origin as the pivot.  The rotation is CW
    # in a LHS when viewed from +X looking toward the origin.
    def rotateXNIP(self, degrees):
        radians = math.radians(-degrees)  # convert degrees to radians
        # grab a copy of the matrices needed for z rotation
        matrix = deepcopy(self.xRotMatrix)
        answer = deepcopy(self.pointCloud)

        # calculate the sines and cosines for insertion in the matrix
        matrix[1][1] = math.cos(radians)
        matrix[1][2] = math.sin(radians)
        matrix[2][1] = -math.sin(radians)
        matrix[2][2] = math.cos(radians)

        # do our matrix multiplication for every point in our mesh. We store it in answer then transfer it to
        # pointcloud element by element because it doesn't work otherwise.
        for i in range(len(self.pointCloud)):
            answer[i] = vectorMatrixMult(self.pointCloud[i], matrix)
            for j in range(len(answer[i])):
                self.pointCloud[i][j] = answer[i][j]

        # calculate the displacement of the pivot of our mesh
        self.midpoint = vectorMatrixMult(self.midpoint, matrix)

    # The function will draw an object by repeatedly calling drawPoly on each polygon in the object
    def drawObject(self, selected):
        for poly in self.meshDef:  # for each polygon,
            self.drawPoly(poly, selected)  # send it to drawPoly()

    # This function will draw a polygon by repeatedly calling drawLine on each pair of points
    # making up the object.  Remember to draw a line between the last point and the first.
    def drawPoly(self, poly, selected):
        for i in range(len(poly)):  # for each point in the polygon (most likely only 3 but arbitrary for compatibility)
            if i == len(poly) - 1:  # if last point in polygon,
                self.drawLine(poly[i], poly[0], selected)  # draw line from last point to first
            else:  # if not last point,
                self.drawLine(poly[i], poly[i + 1], selected)  # draw line from current point to the next point

    # Project the 3D endpoints to 2D point using a perspective projection implemented in 'project'
    # Convert the projected endpoints to display coordinates via a call to 'convertToDisplayCoordinates'
    # draw the actual line using the built-in create_line method. 'selected' is a boolean for determining object color
    def drawLine(self, start, end, selected):
        # send the starting and ending point coords to the project method, then convert them to display
        # #coords to store to local var
        startdisplay = self.convertToDisplayCoordinates(self.project(start))
        enddisplay = self.convertToDisplayCoordinates(self.project(end))
        # use TKinter's create line method using our two points. If object is selected, make line red.
        if selected:
            w.create_line(startdisplay[0], startdisplay[1], enddisplay[0], enddisplay[1], fill="red")
        else:
            w.create_line(startdisplay[0], startdisplay[1], enddisplay[0], enddisplay[1])

    # This function converts from 3D to 2D (+ depth) using the perspective projection technique.  Note that it
    # will return a NEW list of points.  We will not want to keep around the projected points in our object as
    # they are only used in rendering
    def project(self, point):
        # create new list to return projected points without altering our shape definition
        ps = [(d * point[0]) / (-d + point[2]), (d * point[1]) / (-d + point[2]), (point[2]) / (-d + point[2])]
        return ps

    # This function converts a 2D point to display coordinates in the tk system.  Note that it will return a
    # NEW list of points.  We will not want to keep around the display coordinate points in our object as
    # they are only used in rendering.
    def convertToDisplayCoordinates(self, point):
        # create new list to return converted points without altering our shape definition
        displayXY = [0.5 * CanvasWidth + point[0], 0.5 * CanvasHeight + point[1]]
        return displayXY


# *******************************
# Object Manipulation Functions #
# *******************************

# Each of these functions just serves to call the internal manipulation functions on an object, but they loop through
# all selected objects and perform the manipulations on all of them

def drawScreen():
    global allMeshes
    global selectedMeshes

    w.delete(ALL)
    for i in allMeshes:
        i.drawObject(False)

    for i in selectedMeshes:
        i.drawObject(True)

# ***************************


def reset():
    global selectedMeshes
    for i in selectedMeshes:
        i.resetMesh()
    drawScreen()


def scaler():
    global selectedMeshes
    for i in selectedMeshes:
        i.scale(ScaleStepSize)
    drawScreen()


def larger():
    global selectedMeshes
    for i in selectedMeshes:
        i.scale(1 + ScaleStepSize)
    drawScreen()


def smaller():
    global selectedMeshes
    for i in selectedMeshes:
        i.scale(1 - ScaleStepSize)
    drawScreen()


def forward():
    global selectedMeshes
    for i in selectedMeshes:
        i.translate([0, 0, -TranslationStepSize, 1])
    drawScreen()


def backward():
    global selectedMeshes
    for i in selectedMeshes:
        i.translate([0, 0, TranslationStepSize, 1])
    drawScreen()


def left():
    global selectedMeshes
    for i in selectedMeshes:
        i.translate([TranslationStepSize, 0, 0, 1])
    drawScreen()


def right():
    global selectedMeshes
    for i in selectedMeshes:
        i.translate([-TranslationStepSize, 0, 0, 1])
    drawScreen()


def up():
    global selectedMeshes
    for i in selectedMeshes:
        i.translate([0, TranslationStepSize, 0, 1])
    drawScreen()


def down():
    global selectedMeshes
    for i in selectedMeshes:
        i.translate([0, -TranslationStepSize, 0, 1])
    drawScreen()


def xPlus():
    global selectedMeshes
    for i in selectedMeshes:
        i.rotateMesh(RotationStepSize, 'x')
    drawScreen()


def xMinus():
    global selectedMeshes
    for i in selectedMeshes:
        i.rotateMesh(-RotationStepSize, 'x')
    drawScreen()


def yPlus():
    global selectedMeshes
    for i in selectedMeshes:
        i.rotateMesh(RotationStepSize, 'y')
    drawScreen()


def yMinus():
    global selectedMeshes
    for i in selectedMeshes:
        i.rotateMesh(-RotationStepSize, 'y')
    drawScreen()


def zPlus():
    global selectedMeshes
    for i in selectedMeshes:
        i.rotateMesh(RotationStepSize, 'z')
    drawScreen()


def zMinus():
    global selectedMeshes
    for i in selectedMeshes:
        i.rotateMesh(-RotationStepSize, 'z')
    drawScreen()


# *******************************************************
# ******************* Other Functions *******************

# create a mesh and define it as a pyramid
def makePyramid():

    pyramidMesh = Mesh()
    global selectedMeshes
    global allMeshes
    global numMeshesCreated

    # Definition of the underlying points
    pyramidMesh.pointList.append([0, 50, 0, 1])
    pyramidMesh.pointList.append([-50, -50, -50, 1])
    pyramidMesh.pointList.append([50, -50, -50, 1])
    pyramidMesh.pointList.append([50, -50, 50, 1])
    pyramidMesh.pointList.append([-50, -50, 50, 1])

    # Definition of the polygons
    # Polys are defined in counter clockwise order when viewed from the outside
    pyramidMesh.polyList.append([pyramidMesh.pointList[0], pyramidMesh.pointList[1], pyramidMesh.pointList[2]])
    pyramidMesh.polyList.append([pyramidMesh.pointList[0], pyramidMesh.pointList[2], pyramidMesh.pointList[3]])
    pyramidMesh.polyList.append([pyramidMesh.pointList[0], pyramidMesh.pointList[3], pyramidMesh.pointList[4]])
    pyramidMesh.polyList.append([pyramidMesh.pointList[0], pyramidMesh.pointList[4], pyramidMesh.pointList[1]])
    pyramidMesh.polyList.append([pyramidMesh.pointList[4], pyramidMesh.pointList[3], pyramidMesh.pointList[2],
                                pyramidMesh.pointList[1]])

    # Definition of the object
    pyramidMesh.meshDef = [pyramidMesh.polyList[0], pyramidMesh.polyList[1], pyramidMesh.polyList[2],
                           pyramidMesh.polyList[3], pyramidMesh.polyList[4]]

    # Definition of the Pyramid's underlying point cloud.  No structure, just the points.
    for i in pyramidMesh.pointList:
        pyramidMesh.pointCloud.append(i)

    # initialize point cloud copy for resetting
    pyramidMesh.initPointCloud()

    # add new mesh to our selected meshes and our list of all meshes
    selectedMeshes = [pyramidMesh]
    allMeshes.append(pyramidMesh)

    meshNames.append(["pyramid" + str(numMeshesCreated)])  # add a user-friendly name to be associated with the mesh
    numMeshesCreated += 1  # increment the counter for meshes
    updateMeshList()  # update our UI's mesh list
    pyramidMesh.findMidpoint()  # find the midpoint of our new object
    drawScreen()  # draw the screen
    updateTitleBar()
    return pyramidMesh


# create a mesh and define it as a cube
def makeCube():
    cubeMesh = Mesh()
    global selectedMeshes
    global allMeshes
    global numMeshesCreated

    # for num in range(0,5):
    # Definition of the underlying points
    cubeMesh.pointList.append([-50, 50, -50, 1])
    cubeMesh.pointList.append([-50, -50, -50, 1])
    cubeMesh.pointList.append([50, -50, -50, 1])
    cubeMesh.pointList.append([50, 50, -50, 1])
    cubeMesh.pointList.append([50, 50, 50, 1])
    cubeMesh.pointList.append([50, -50, 50, 1])
    cubeMesh.pointList.append([-50, -50, 50, 1])
    cubeMesh.pointList.append([-50, 50, 50, 1])

    # Definition of the polygons
    # Polys are defined in counter clockwise order when viewed from the outside
    cubeMesh.polyList.append([cubeMesh.pointList[0], cubeMesh.pointList[1], cubeMesh.pointList[2], cubeMesh.pointList[3]])
    cubeMesh.polyList.append([cubeMesh.pointList[3], cubeMesh.pointList[2], cubeMesh.pointList[5], cubeMesh.pointList[4]])
    cubeMesh.polyList.append([cubeMesh.pointList[4], cubeMesh.pointList[5], cubeMesh.pointList[6], cubeMesh.pointList[7]])
    cubeMesh.polyList.append([cubeMesh.pointList[7], cubeMesh.pointList[6], cubeMesh.pointList[1], cubeMesh.pointList[0]])
    cubeMesh.polyList.append([cubeMesh.pointList[1], cubeMesh.pointList[6], cubeMesh.pointList[5], cubeMesh.pointList[2]])
    cubeMesh.polyList.append([cubeMesh.pointList[7], cubeMesh.pointList[0], cubeMesh.pointList[3], cubeMesh.pointList[4]])

    # Definition of the object
    cubeMesh.meshDef = [cubeMesh.polyList[0], cubeMesh.polyList[1], cubeMesh.polyList[2],
                        cubeMesh.polyList[3], cubeMesh.polyList[4], cubeMesh.polyList[5]]

    # Definition of the Pyramid's underlying point cloud.  No structure, just the points.
    for i in cubeMesh.pointList:
        cubeMesh.pointCloud.append(i)

    # initialize point cloud copy for resetting
        cubeMesh.initPointCloud()

    # add new mesh to our selected meshes and our list of all meshes
    selectedMeshes = [cubeMesh]
    allMeshes.append(cubeMesh)

    meshNames.append(["cube" + str(numMeshesCreated)])  # add a user-friendly name to be associated with the mesh
    numMeshesCreated += 1  # increment the counter for meshes
    updateMeshList()  # update our UI's mesh list
    cubeMesh.findMidpoint()  # find the midpoint of our new object
    drawScreen()  # draw the screen
    updateTitleBar()
    return cubeMesh


# deletes all selected meshes
def deleteMesh():
    global selectedMeshes
    global allMeshes

    for i in selectedMeshes:  # for each selected mesh
        if i in allMeshes:  # sanity check
            del meshNames[allMeshes.index(i)]  # delete the user-friendly mesh name
            allMeshes.remove(i)  # and delete the associated mesh

    selectedMeshes = []  # empty the list of selected meshes
    updateMeshList()  # update our UI's mesh list
    updateTitleBar()
    drawScreen()  # draw the screen


# updates our UI's list of meshes
def updateMeshList():
    global selectedMeshes
    global allMeshes

    meshList.delete(0, END)  # empty the mesh list

    for i in range(len(allMeshes)):  # for each mesh
        meshList.insert(i, meshNames[i])  # add it to the mesh list


# function called when user changes selection of meshes in the mesh list box
def onSelectionChanged(input):
    global selectedMeshes
    global allMeshes

    selectedMeshes.clear()  # deselect all meshes

    for i in list(meshList.curselection()):  # for each mesh selected in the UI
        selectedMeshes.append(allMeshes[i])  # add it to our selected meshes list

    updateTitleBar()
    drawScreen()  # draw the screen


# multiplies a vector by a 4x4 matrix
def vectorMatrixMult(vector, matrix):
    answerVector = [0,0,0,0]

    # for each column and row we multiply the two values from the two matrices and sum them all up, storing the value in
    # the related index in our new vector
    for col in range(len(matrix)):
        answerVector[col] = 0
        for row in range(len(matrix)):
            answerVector[col] += vector[row] * matrix[row][col]

    return answerVector


# multiplies 2 4x4 matrices
def matrixMult4x4(matrix1, matrix2):
    answerMatrix = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]

    # for each column and row and column we multiply the two values from the two matrices and sum them all up, storing
    # the value in the related index in our new matrix
    for i in range(len(matrix1)):
        for j in range(len(matrix2[0])):
            for k in range(len(matrix1[0])):
                answerMatrix[i][j] += matrix1[i][k] * matrix2[k][j]

    return answerMatrix

# **************************************************
# ******* Functions for Changing UI Behavior *******


# lower the step size of the "scale" transformation control
def changeScaleStepSizeDown():
    global ScaleStepSize  # access global variable that controls the step size for the transformation controls
    ScaleStepSize -= 0.01  # alter it
    if ScaleStepSize < 0.01:  # confine it
        ScaleStepSize = 0.01
    scalecontrolsstepslabel.config(
        text=str('{:.2f}'.format(round(ScaleStepSize, 2))) + 'x')  # change the text of the label for step size
    if ScaleStepSize < 1:
        scalecontrolslabel2.config(text='(Smaller)')  # if we will be decreasing the size, text changes to indicate this
    if ScaleStepSize == 1:
        scalecontrolslabel2.config(text='(Static)')  # if there will be no change in size, text changes to indicate this


# raise the step size of the "scale" transformation control
def changeScaleStepSizeUp():
    global ScaleStepSize
    ScaleStepSize += 0.01
    if ScaleStepSize > 10:
        ScaleStepSize = 10
    scalecontrolsstepslabel.config(text=str('{:.2f}'.format(round(ScaleStepSize, 2))) + 'x')
    if ScaleStepSize > 1:
        scalecontrolslabel2.config(text='(Larger)')  # if we will be increasing the size, text changes to indicate this
    if ScaleStepSize == 1:
        scalecontrolslabel2.config(text='(Static)')  # if there will be no change in size, text changes to indicate this


# resets the scaling step size to default
def resetScaleStepSize(event):
    global ScaleStepSize
    ScaleStepSize = 1.00
    scalecontrolsstepslabel.config(text=str('{:.2f}'.format(round(ScaleStepSize, 2))) + 'x')
    scalecontrolslabel2.config(text='(Static)')


# lower the step size of the "translation" transformation control
def changeTranslationStepSizeDown():
    global TranslationStepSize
    TranslationStepSize -= 1
    if TranslationStepSize < 1:
        TranslationStepSize = 1
    translationcontrolsstepslabel.config(text=TranslationStepSize)


# raise the step size of the "translation" transformation control
def changeTranslationStepSizeUp():
    global TranslationStepSize
    TranslationStepSize += 1
    if TranslationStepSize > 100:
        TranslationStepSize = 100
    translationcontrolsstepslabel.config(text=TranslationStepSize)


# resets the translation step size to default
def resetTranslationStepSize(event):
    global TranslationStepSize
    TranslationStepSize = 5
    translationcontrolsstepslabel.config(text=str(TranslationStepSize))


# lower the step size of the "rotation" transformation control
def changeRotationStepSizeDown():
    global RotationStepSize
    RotationStepSize -= 1
    if RotationStepSize < 1:
        RotationStepSize = 1
    rotationcontrolsstepslabel.config(text=str(RotationStepSize) + '°')


# raise the step size of the "rotation" transformation control
def changeRotationStepSizeUp():
    global RotationStepSize
    RotationStepSize += 1
    if RotationStepSize > 180:
        RotationStepSize = 180
    rotationcontrolsstepslabel.config(text=str(RotationStepSize) + '°')


# resets the rotation step size to default
def resetRotationStepSize(event):
    global RotationStepSize
    RotationStepSize = 5
    rotationcontrolsstepslabel.config(text=str(RotationStepSize) + '°')


# toggles the usage of world-coordinates vs local-coordinates
def toggleNIP():
    global NIP
    if not NIP:
        NIP = True
    else:
        NIP = False


# Handles screen and viewport resizing and recalculating. Whenever the window size is change by the user, set the new
# width and height of our canvas to the new midpoint, so that the origin stays at the center of the canvas.
def updateCanvasCoords(event):
    global CanvasHeight
    global CanvasWidth

    CanvasWidth = event.width
    CanvasHeight = event.height

    drawScreen()


# update what is written on the title bar with the number of meshes and selected meshes
def updateTitleBar():
    if len(allMeshes) == 1:
        meshesString = 'Mesh'
    else:
        meshesString = 'Meshes'
    root.wm_title("Sweet Engine v0.2 -- " + str(len(allMeshes)) + " "
                  + meshesString + " (" + str(len(selectedMeshes)) + " Selected)")


# *****************************************************
# ***************** TKinter layout ********************

root = Tk()
root.minsize(444, 519)
root.wm_title("Sweet Engine v0.2")

outerframe = Frame(root)
outerframe.pack(fill="both", expand=True)

selectionpanel = Frame(outerframe, height=400, width=400)
selectionpanel.pack(side=LEFT, fill=Y, expand=0, anchor=W)

createpyramidbutton = Button(selectionpanel, text="New Pyramid", fg="green", command=makePyramid)
createpyramidbutton.pack(fill=X, expand=0)

createcubebutton = Button(selectionpanel, text="New Cube", fg="green", command=makeCube)
createcubebutton.pack(fill=X, expand=0)

deletemeshbutton = Button(selectionpanel, text="Delete Mesh", fg="red", command=deleteMesh)
deletemeshbutton.pack(fill=X, expand=0)

rightframe = Frame(outerframe)
rightframe.pack(side=RIGHT, fill="both", expand=True)

w = Canvas(rightframe, width=CanvasWidth, height=CanvasHeight, bg="white", relief=RIDGE, borderwidth=4)
w.pack(side=TOP, fill="both", expand=True)
w.bind('<Configure>', updateCanvasCoords)


controlpanel = Frame(rightframe, height=400)
controlpanel.pack(side=BOTTOM)

scrollbar = Scrollbar(selectionpanel, orient="vertical")
meshList = Listbox(selectionpanel, selectmode=EXTENDED, height=30, yscrollcommand=scrollbar.set)
scrollbar.config(command=meshList.yview)
scrollbar.pack(side="right", fill="y")
meshList.bind('<<ListboxSelect>>', onSelectionChanged)
meshList.pack(fill="both", expand=True)

resetcontrols = Frame(controlpanel, height=400, borderwidth=2, relief=RIDGE)
resetcontrols.pack(side=TOP)

coordcheckbox = Checkbutton(resetcontrols, text="Use World-Space Coordinates", command=toggleNIP)
coordcheckbox.pack(side=RIGHT)

resetButton = Button(resetcontrols, text="Reset", fg="red", command=reset)
resetButton.pack(side=LEFT)

# scale step controls

scalecontrolssteps = Frame(controlpanel, borderwidth=4, relief=RIDGE)
scalecontrolssteps.pack(side=LEFT)

scaleUpButton = Button(scalecontrolssteps, text="▲", command=changeScaleStepSizeUp, repeatdelay=500, repeatinterval=25)
scaleUpButton.pack(side=TOP)

scalecontrolsstepslabel = Label(scalecontrolssteps, text="1.00x")
scalecontrolsstepslabel.bind('<Button-1>', resetScaleStepSize)
scalecontrolsstepslabel.pack()

scaleDownButton = Button(scalecontrolssteps, text="▼", command=changeScaleStepSizeDown, repeatdelay=500,
                         repeatinterval=25)
scaleDownButton.pack(side=BOTTOM)

########

scalecontrols = Frame(controlpanel, borderwidth=4, relief=RIDGE)
scalecontrols.pack(side=LEFT)

scalecontrolslabel = Label(scalecontrols, text="Scale", fg="green")
scalecontrolslabel.pack(side=TOP)

scalecontrolslabel2 = Label(scalecontrols, text="(Static)", fg="green")
scalecontrolslabel2.pack()

scaleButton = Button(scalecontrols, text="Scale", command=scaler, repeatdelay=500, repeatinterval=100)
scaleButton.pack(side=BOTTOM)

# translation step controls

translationcontrolssteps = Frame(controlpanel, borderwidth=4, relief=RIDGE)
translationcontrolssteps.pack(side=LEFT)

translationUpButton = Button(translationcontrolssteps, text="▲", command=changeTranslationStepSizeUp, repeatdelay=500,
                             repeatinterval=50)
translationUpButton.pack(side=TOP)

translationcontrolsstepslabel = Label(translationcontrolssteps, text="5")
translationcontrolsstepslabel.bind('<Button-1>', resetTranslationStepSize)
translationcontrolsstepslabel.pack()

translationDownButton = Button(translationcontrolssteps, text="▼", command=changeTranslationStepSizeDown,
                               repeatdelay=500, repeatinterval=50)
translationDownButton.pack(side=BOTTOM)

########

translatecontrols = Frame(controlpanel, borderwidth=4, relief=RIDGE)
translatecontrols.pack(side=LEFT)

translatecontrolslabel = Label(translatecontrols, text="Translation", fg="green")
translatecontrolslabel.pack()

translatecontrolsupper = Frame(translatecontrols)
translatecontrolsupper.pack()

translatecontrolslower = Frame(translatecontrols)
translatecontrolslower.pack()

#########

backwardButton = Button(translatecontrolsupper, text="⟱", command=backward, repeatdelay=500, repeatinterval=50)
backwardButton.pack(side=LEFT)

upButton = Button(translatecontrolsupper, text="↑", command=up, repeatdelay=500, repeatinterval=50)
upButton.pack(side=LEFT)

forwardButton = Button(translatecontrolsupper, text="⟰", command=forward, repeatdelay=500, repeatinterval=50)
forwardButton.pack(side=LEFT)

leftButton = Button(translatecontrolslower, text="←", command=left, repeatdelay=500, repeatinterval=50)
leftButton.pack(side=LEFT)

upButton = Button(translatecontrolslower, text="↓", command=down, repeatdelay=500, repeatinterval=50)
upButton.pack(side=LEFT)

rightButton = Button(translatecontrolslower, text="→", command=right, repeatdelay=500, repeatinterval=50)
rightButton.pack(side=LEFT)

# rotation step controls

rotationcontrolssteps = Frame(controlpanel, borderwidth=4, relief=RIDGE)
rotationcontrolssteps.pack(side=LEFT)

rotationUpButton = Button(rotationcontrolssteps, text="▲", command=changeRotationStepSizeUp, repeatdelay=500,
                          repeatinterval=50)
rotationUpButton.pack(side=TOP)

rotationcontrolsstepslabel = Label(rotationcontrolssteps, text="5°")
rotationcontrolsstepslabel.bind('<Button-1>', resetRotationStepSize)
rotationcontrolsstepslabel.pack()

rotationDownButton = Button(rotationcontrolssteps, text="▼", command=changeRotationStepSizeDown, repeatdelay=500,
                            repeatinterval=50)
rotationDownButton.pack(side=BOTTOM)

##########

rotationcontrols = Frame(controlpanel, borderwidth=4, relief=RIDGE)
rotationcontrols.pack(side=LEFT)

rotationcontrolslabel = Label(rotationcontrols, text="Rotation", fg="green")
rotationcontrolslabel.pack()

rotationcontrolsx = Frame(rotationcontrols)
rotationcontrolsx.pack(side=LEFT)

rotationcontrolsy = Frame(rotationcontrols)
rotationcontrolsy.pack(side=LEFT)

rotationcontrolsz = Frame(rotationcontrols)
rotationcontrolsz.pack(side=LEFT)

xPlusButton = Button(rotationcontrolsx, text="X+", command=xPlus, repeatdelay=500, repeatinterval=50)
xPlusButton.pack(side=TOP)

xMinusButton = Button(rotationcontrolsx, text="X-", command=xMinus, repeatdelay=500, repeatinterval=50)
xMinusButton.pack(side=BOTTOM)

yPlusButton = Button(rotationcontrolsy, text="Y+", command=yPlus, repeatdelay=500, repeatinterval=50)
yPlusButton.pack(side=TOP)

yMinusButton = Button(rotationcontrolsy, text="Y-", command=yMinus, repeatdelay=500, repeatinterval=50)
yMinusButton.pack(side=BOTTOM)

zPlusButton = Button(rotationcontrolsz, text="Z+", command=zPlus, repeatdelay=500, repeatinterval=50)
zPlusButton.pack(side=TOP)

zMinusButton = Button(rotationcontrolsz, text="Z-", command=zMinus, repeatdelay=500, repeatinterval=50)
zMinusButton.pack(side=BOTTOM)


# **************************************************************************
# ****************** Place Initialization Conditions Here ******************


# MUST GO AT END OF PROGRAM!!! PLACE NOTHING BELOW THIS!!!!!!!!!!!!
root.mainloop()
