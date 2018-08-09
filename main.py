###############
# All imports #
###############
import bpy
import sys
import numpy as np
from os.path import dirname
filePath = '/home/wdmarais/Desktop/BlenderSpace/structured/IC.py'
fileDir = dirname(filePath)
sys.path.append(fileDir)
from spaceBodies import spaceBody
from IC import basicScene
from scipy.constants import au
###################
#Blender Utilities#
###################
def clearAllObjects():
    for o in bpy.data.objects:
        o.select = True
    bpy.ops.object.delete(use_global=False)

    for m in bpy.data.materials:
        bpy.data.materials.remove(m)

def addNamedSphere(sphereName, xyzCoord, diameter, color):
    layerList = [False] * 20
    layerList[0] = True
    activeLayers = tuple(layerList)
    bpy.ops.mesh.primitive_ico_sphere_add(size = diameter, location = xyzCoord, layers = activeLayers)
    sphere = bpy.context.active_object
    sphere.name = sphereName
    mat = bpy.data.materials.new(name=sphereName)
    mat.diffuse_color = color
    sphere.data.materials.append(mat)
    #bpy.ops.object.shade_smooth()

def addMarker(parentName, xyzCoord, size,  color, frame):
    layerList = [False] * 20
    layerList[0] = True
    activeLayers = tuple(layerList)
    bpy.ops.mesh.primitive_cube_add(radius = size, location = xyzCoord, layers = activeLayers)
    marker = bpy.context.active_object
    marker.name = parentName + "Frame" + str(frame).zfill(5)
    mat = bpy.data.materials[parentName]
    marker.data.materials.append(mat)

def addNamedCylinder(cylName, xyzCoord, rad, height, color):
    layerList = [False] * 20
    layerList[0] = True
    activeLayers = tuple(layerList)
    bpy.ops.mesh.primitive_cylinder_add(radius = diameter, depth = height, location = xyzCoord, layers = activeLayers)
    bpy.context.active_object.name = cylName
    #bpy.ops.object.shade_smooth()

def initializeScene(firstFrame, lastFrame):
    clearAllObjects()
    bpy.context.scene.frame_start = firstFrame
    bpy.context.scene.frame_end = lastFrame

def addKeyFrame(objectName, objectLocation, frame):
    o = bpy.data.objects[objectName]
    o.location = objectLocation
    o.keyframe_insert(data_path="location", index=-1)

##################
#Scene Parameters#
##################
firstTimeStep = 1
lastTimeStep = 500
dT = 24*60*60
leavePathMarkers = True
###########
#Main code#
###########
bodies = basicScene()

initializeScene(firstTimeStep, lastTimeStep)
distanceFactor = 1*au

for body in bodies:
    name = body.name
    position = body.position / distanceFactor
    diameter = body.diameter
    color = body.color
    print(color)
    print(position)
    addNamedSphere(name, position, diameter, color)

markerTicker = 0
markerFrameGap = 10
for f in range(firstTimeStep, lastTimeStep):
    print(f)
    markerTicker += 1
    bpy.context.scene.frame_set(f)

    for index, body in enumerate(bodies):
        others = np.delete(bodies, index)
        body.updateState(others, dT)
        body.logState(f)
        addKeyFrame(body.name, body.position / distanceFactor, f)

    if (leavePathMarkers == True) and (markerTicker >= markerFrameGap):
        markerTicker = 0
        for body in bodies:
                addMarker(body.name, body.position / distanceFactor, body.markerSize, body.color, f)

bpy.context.scene.frame_current = 1
bpy.ops.object.select_all(action='TOGGLE')
