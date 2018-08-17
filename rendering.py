import bpy, bmesh
import json
from scipy.constants import au
import numpy as np
#####################
# Blender Utilities #
#####################
def returnLayerTuple(activeLayer):
    layerList = 20 * [False]
    layerList[activeLayer] = True
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
    activeLayers = returnLayerTuple(0)
    bpy.ops.mesh.primitive_uv_sphere_add(size = diameter, location = xyzCoord, layers = activeLayers)
    sphere = bpy.context.active_object
    sphere.name = sphereName
    mat = bpy.data.materials.new(name=sphereName)
    mat.diffuse_color = color
    sphere.data.materials.append(mat)
    bpy.ops.object.shade_smooth()

def addMarker(parentName, xyzCoord, size,  color, frame):
    activeLayers = returnLayerTuple(0)
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

def render_and_save(moves):
    filePath = "//renders/" + str(moves).zfill(4) + ".png"
    bpy.context.scene.render.filepath = filePath
    bpy.ops.render.render(use_viewport = True, write_still=True)


#############
# Main Code #
#############

with open('general.json') as g:
    generalData = json.load(g)
g.close()

sceneName = generalData["sceneName"]
sceneFile = generalData["sceneFile"]
bpy.context.scene.render.resolution_x = generalData["resolution_x"]
bpy.context.scene.render.resolution_y = generalData["resolution_y"]
bpy.context.scene.render.resolution_percentage = generalData["resolution_percentage"]
bpy.context.scene.render.ffmpeg.codec = generalData["file_codec"]
extension = ".mp4"
bpy.context.scene.render.filepath = "//movies/" + sceneName + extension
bpy.context.scene.render.ffmpeg.format = generalData["file_format"]
bpy.context.scene.render.fps = generalData["frames_per_second"]
leaveTrails = generalData["leaveTrails"]
if (leaveTrails == "True"):
    leaveTrails = True
else:
    leaveTrails = False

firstTimeStep = generalData["firstTimeStep"]
lastTimeStep = generalData["lastTimeStep"]

with open(sceneFile) as sF:
    sceneData = json.load(sF)
sF.close()

with open("colors.json") as colorFile:
    c = json.load(colorFile)
colorFile.close()

bodies = sceneData["bodies"]
dataArray = np.zeros((len(bodies), (lastTimeStep + 1 - firstTimeStep), 3))
initializeScene(firstTimeStep, lastTimeStep)
for b, body in enumerate(bodies):
    name = body["name"]
    dataFile = name + "/Pos.dat"
    dataArray[b] = np.genfromtxt(sceneName + "/" + dataFile)
    dataArray[b] /= au
    position = dataArray[b, 0]
    diameter = body["diameter"]
    colorName = body["color"]
    color = tuple(c[colorName])
    addNamedSphere(name, position, diameter, color)

bpy.context.scene.frame_current = 1
bpy.ops.object.select_all(action='TOGGLE')

trailInterval = 10
ticker = 10
markerSize = 0.02
for f in range(lastTimeStep):
    print("Frame: ", f)
    bpy.context.scene.frame_current = f
    for b, body in enumerate(bodies):
        name = body["name"]
        colorName = body["color"]
        color = tuple(c[colorName])
        pos = dataArray[b][f]
        o = bpy.data.objects[name]
        o.location = pos
        if ((f % ticker) == 0):
            addKeyFrame(name, pos, f)
        if ((leaveTrails == True) and ((f % trailInterval) == 0)):
            addMarker(name, pos, markerSize, color, f)
            marker = bpy.context.active_object
            addViewFrame(marker, False, firstTimeStep) #Make invisible from start
            addViewFrame(marker, True, f) #Make visible from current frame

activeLayers = returnLayerTuple(0)

loc = (0.0, 0.15, 7.0)
rot = (0.0, 0.0, np.deg2rad(45.0))
addCamera(loc, rot, activeLayers)
bpy.context.scene.camera = bpy.data.objects['Camera']

loc = (0.0, 3.0, 2.0)
rot = (0.0, 0.0, 0.0)
bpy.ops.object.lamp_add(type='POINT', location = loc, rotation = rot, layers = activeLayers)

loc = (0.0, -3.0, 2.0)
rot = (0.0, 0.0, 0.0)
bpy.ops.object.lamp_add(type='POINT', location = loc, rotation = rot, layers = activeLayers)

bpy.ops.wm.save_mainfile(filepath=sceneName+".blend")
print("Setup complete")
#bpy.ops.render.render(animation=True)
'''
for f in range(firstTimeStep, lastTimeStep):
    bpy.context.scene.frame_set(f)
    render_and_save(f)
'''
