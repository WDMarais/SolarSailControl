###############
# All imports #
###############
import bpy, bmesh
import sys
import datetime
import numpy as np
from scipy.constants import au

blenderDir = bpy.path.abspath("//")
sys.path.append(blenderDir)
from IC import basicScene
from IC import keplerian
###################
#Blender Utilities#
###################

def returnLayerTuple(activeLayer):
    layerList = 20 * [False]
    layerList[activeLayer-1] = True
    return tuple(layerList)

def meshSelect(obj):
    bpy.context.scene.objects.active = obj
    bpy.ops.object.mode_set(mode = 'EDIT')


def clearAllObjects():
    #obj = bpy.data.objects['Earth']
    #bpy.contexts.scene.objects.active = obj
    #bpy.ops.object.mode_set(mode = 'OBJECT')
    for o in bpy.data.objects:
        o.select = True
    bpy.ops.object.delete(use_global=False)

    for m in bpy.data.materials:
        bpy.data.materials.remove(m)

def addNamedSphere(sphereName, xyzCoord, diameter, color):
    activeLayers = returnLayerTuple(1)
    bpy.ops.mesh.primitive_uv_sphere_add(size = diameter, location = xyzCoord, layers = activeLayers)
    sphere = bpy.context.active_object
    sphere.name = sphereName
    mat = bpy.data.materials.new(name=sphereName)
    mat.diffuse_color = color
    sphere.data.materials.append(mat)
    bpy.ops.object.shade_smooth()

def addMarker(parentName, xyzCoord, size,  color, frame):
    activeLayers = returnLayerTuple(1)
    bpy.ops.mesh.primitive_plane_add(radius = size, location = xyzCoord, layers = activeLayers)
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

def addCamera(loc, rot, activeLayers):
    bpy.ops.object.camera_add(location = loc, rotation = rot, layers = activeLayers)

def initializeScene(firstFrame, lastFrame):
    clearAllObjects()
    bpy.context.scene.frame_start = firstFrame
    bpy.context.scene.frame_end = lastFrame

def addKeyFrame(objectName, objectLocation, f):
    o = bpy.data.objects[objectName]
    o.location = objectLocation
    o.keyframe_insert(data_path="location", index=-1)

def addViewFrame(obj, visible, f):
    obj.hide = not(visible)
    obj.hide_render = not(visible)
    obj.keyframe_insert(data_path="hide", frame=f)
    obj.keyframe_insert(data_path="hide_render", frame=f)

#def render_and_save(moves):
#    bpy.context.scene.render.filepath = "//renders/"+str(moves)+".png"
#    bpy.ops.render.render(use_viewport = True, write_still=True)
##################
#Scene Parameters#

print("Hello")
loc = (0.0, 0.0, 0.0)
rot = (0.0, 0.0, 0.0)
whichLayers = returnLayerTuple(1)
print(whichLayers)
addCamera(loc, rot, whichLayers)