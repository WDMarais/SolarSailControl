import bpy, bmesh
import json
from scipy.constants import au
import numpy as np
#####################
# Blender Utilities #
#####################

O = bpy.ops
C = bpy.context
D = bpy.data

def returnLayerTuple(activeLayer):
    layerList = 20 * [False]
    layerList[activeLayer] = True
    return tuple(layerList)

def setMaterial(obj, mat):
    obj.active_material = mat

def createMaterial(name, color, whichType):
    mat = D.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)

    mat.diffuse_color = color
    mat.diffuse_intensity = 1
    mat.type = whichType

    return mat

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

def addVertexObj(name, location):
    O.mesh.primitive_plane_add(location = location)
    opObj = O.object
    opObj.mode_set(mode="EDIT")
    O.mesh.select_all(action="DESELECT")
    opObj.mode_set(mode="OBJECT")

    vObj = C.object
    vObj.name = name

    verts = vObj.data.vertices
    for i in range(1, 4):
        verts[i].select = True
    opObj.mode_set(mode="EDIT")
    O.mesh.delete(type="VERT")
    opObj.mode_set(mode="OBJECT")
    opObj.origin_set(type="GEOMETRY_ORIGIN")

    return vObj

def addParticles(obj, start, end, lifetime):
    particleSysName = obj.name + "Particles"
    C.scene.objects.active = obj
    if (particleSysName not in obj):
        O.object.particle_system_add()
        C.object.particle_systems[0].name = particleSysName

    particleSys = obj.particle_systems[particleSysName]
    settings = particleSys.settings
    settings.emit_from = "VERT"
    settings.effector_weights.gravity = 0
    settings.frame_start = start
    settings.frame_end = end
    settings.lifetime = lifetime

def addTrail(parentObj):
    with open('general.json') as g:
        gen = json.load(g)
    g.close()

    with open(gen["sceneFile"]) as s:
        scn = json.load(s)
    s.close()

    trailWidth = scn["trailWidth"]
    start = 1
    end = start + scn["numSteps"]
    location = (0.0, 0.0, 0.0)
    trailName = parentObj.name + "Trail"

    vert = addVertexObj(trailName, location)
    vert.parent = parentObj
    parentColor = parentObj.active_material.diffuse_color
    vertMat = createMaterial(trailName + "Material", parentColor, "HALO")
    vertMat.halo.size = trailWidth
    setMaterial(vert, vertMat)
    duration = end - start + 1
    addParticles(vert, start, end, duration)

def addActiveBody(name, size, bodyType, color, location, makeTrail=False):
    if (bodyType == "SPHERE"):
        O.mesh.primitive_uv_sphere_add(size=size, location=location)
        O.object.shade_smooth()
    else:
        O.mesh.primitive_cube_add(size=size, location=location)

    body = bpy.context.active_object
    body.name = name
    matName = name + "Material"
    mat = createMaterial(matName, color, "SURFACE")
    setMaterial(body, mat)

    if makeTrail:
        addTrail(body)

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

sceneFile = generalData["sceneFile"]

with open(sceneFile) as sF:
    sceneData = json.load(sF)
sF.close()

sceneName = sceneData["sceneName"]

with open("colors.json") as colorFile:
    c = json.load(colorFile)
colorFile.close()

bpy.context.scene.render.resolution_x = generalData["resolution_x"]
bpy.context.scene.render.resolution_y = generalData["resolution_y"]
bpy.context.scene.render.resolution_percentage = generalData["resolution_percentage"]
bpy.context.scene.render.ffmpeg.codec = generalData["file_codec"]
extension = ".mp4"
bpy.context.scene.render.filepath = "//movies/" + sceneName + extension
bpy.context.scene.render.ffmpeg.format = generalData["file_format"]
bpy.context.scene.render.fps = generalData["frames_per_second"]
leaveTrails = sceneData["leaveTrails"]
if (leaveTrails == "True"):
    leaveTrails = True
else:
    leaveTrails = False

firstFrame = 1
numFrames = sceneData["numSteps"]

bodies = sceneData["bodies"]
dataArray = np.zeros((len(bodies), numFrames, 3))
initializeScene(firstFrame, firstFrame + numFrames)

for b, body in enumerate(bodies):
    name = body["name"]
    dataFile = name + "/Pos.dat"
    dataArray[b] = np.genfromtxt(sceneName + "/" + dataFile)
    dataArray[b] /= au
    position = dataArray[b, 0]
    diameter = body["diameter"]
    colorName = body["color"]
    color = tuple(c[colorName])
    addActiveBody(name, diameter, "SPHERE", color, position, leaveTrails)

bpy.context.scene.frame_current = 1
bpy.ops.object.select_all(action='TOGGLE')

trailInterval = 10
ticker = 10
markerSize = 0.02
for f in range(numFrames):
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

activeLayers = returnLayerTuple(0)

loc = (0.0, 0.15, 7.0)
rot = (0.0, 0.0, np.deg2rad(45.0))
addCamera(loc, rot, activeLayers)
bpy.context.scene.camera = bpy.data.objects['Camera']

loc = (0.0, 3.0, 2.0)
rot = (0.0, 0.0, 0.0)
bpy.ops.object.lamp_add(type='POINT', location = loc, rotation = rot, layers = activeLayers)

loc = (0.0, 3.0, -2.0)
rot = (0.0, 0.0, 0.0)
bpy.ops.object.lamp_add(type='POINT', location = loc, rotation = rot, layers = activeLayers)

loc = (0.0, -3.0, 2.0)
rot = (0.0, 0.0, 0.0)
bpy.ops.object.lamp_add(type='POINT', location = loc, rotation = rot, layers = activeLayers)

loc = (0.0, -3.0, -2.0)
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
