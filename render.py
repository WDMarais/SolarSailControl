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

genPath = "general.json"
colorsPath = "colors.json"

with open(colorsPath) as colors:
    c = json.load(colors)
colors.close()

with open(genPath) as g:
    generalSettings = json.load(g)
g.close()

scenePath = generalSettings["sceneFileDir"] + "/" + generalSettings["sceneFile"]

with open(scenePath) as s:
    scene = json.load(s)
s.close()

sceneName = scene["name"]
bodiesDict = scene["bodies"]
numSteps = scene["numSteps"]
leaveTrails = scene["leaveTrails"]
trailDuration = scene["trailDuration"]

def flattenRecursiveBodiesDict(bodiesDict):
    flattenedDict = []
    for b in bodiesDict:
        if "children" in b:
            children = b["children"]
            del b["children"]
            flattenedDict = flattenedDict + [b]
            childrenDict = flattenRecursiveBodiesDict(children)
            flattenedDict = flattenedDict + childrenDict
        else:
            flattenedDict = flattenedDict + [b]
    return flattenedDict

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

def clearAllObjects():
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
    with open(genPath) as g:
        gen = json.load(g)
    g.close()

    with open(scenePath) as s:
        scn = json.load(s)
    s.close()

    trailWidth = scn["trailWidth"]
    start = 1
    numSteps = scn["numSteps"]
    location = (0.0, 0.0, 0.0)
    trailName = parentObj.name + "Trail"

    vert = addVertexObj(trailName, location)
    vert.parent = parentObj
    parentColor = parentObj.active_material.diffuse_color
    vertMat = createMaterial(trailName + "Material", parentColor, "HALO")
    vertMat.halo.size = trailWidth
    setMaterial(vert, vertMat)
    addParticles(vert, start, numSteps, trailDuration) #Rendering all frames, so the duration and the end are the same

def addSolarSail(name, size, location = (5, 5, 5)):
    sailDisplacement = 1.5 * size * np.array([0.0, 0.0, 1])
    #sailThickness = tuple(0.2 * size * np.array([0.0, 0.0, 1]))
    O.mesh.primitive_cube_add(radius=2*size)
    A = C.active_object
    A.scale = [1.0, 1.0, 0.05]
    A.location = location + sailDisplacement
    O.mesh.primitive_uv_sphere_add(size=size, location=location)
    B = C.active_object
    O.object.shade_smooth()
    B.name = name

    A.select = True
    B.select = True
    O.object.join()

def addActiveBody(name, size, bodyType, color, location, makeTrail=False):
    if (bodyType == "SPHERE"):
        O.mesh.primitive_uv_sphere_add(size=size, location=location)
        O.object.shade_smooth()
    elif (bodyType == "SOLSAT"):
        addSolarSail(name, size, location)

    body = bpy.context.active_object
    body.name = name
    matName = name + "Material"
    mat = createMaterial(matName, color, "SURFACE")
    setMaterial(body, mat)

    if makeTrail:
        addTrail(body)

def addBodies(bodiesDict, leaveTrails, posArray):
    for b, body in enumerate(bodiesDict):
        name = body["name"]
        dataFile = name + "/Pos.dat"
        position = posArray[b][0]
        print(name)
        print(posArray[b])
        print()
        g = body["graphics"]
        size = g["size"]
        colorName = g["color"]
        bodyType = g["representation"]
        color = tuple(c[colorName])
        addActiveBody(name, size, bodyType, color, position, leaveTrails)

def addCamera(loc, rot, activeLayers):
    bpy.ops.object.camera_add(location = loc, rotation = rot, layers = activeLayers)

def initializeScene(firstFrame, lastFrame):
    clearAllObjects()
    bpy.context.scene.frame_start = firstFrame
    bpy.context.scene.frame_end = lastFrame

def addKeyFrame(objectName, objectLocation):
    o = bpy.data.objects[objectName]
    o.location = objectLocation
    o.keyframe_insert(data_path="location", index=-1)

def setRenderSettings(settingDict):
    bpy.context.scene.render.resolution_x = settingDict["resolution_x"]
    bpy.context.scene.render.resolution_y = settingDict["resolution_y"]
    bpy.context.scene.render.resolution_percentage = settingDict["resolution_percentage"]
    bpy.context.scene.render.ffmpeg.codec = settingDict["file_codec"]
    extension = ".mp4"
    bpy.context.scene.render.filepath = "//movies/" + sceneName + extension
    bpy.context.scene.render.ffmpeg.format = settingDict["file_format"]
    bpy.context.scene.render.fps = settingDict["frames_per_second"]
setRenderSettings(generalSettings)

flatBD = flattenRecursiveBodiesDict(bodiesDict)
posArray = np.zeros((len(flatBD), numSteps, 3))

sceneDataPath = "scenes/" + sceneName
for b, body in enumerate(flatBD):
    name = body["name"]
    posFile = name + "/Pos.dat"
    posArray[b] = np.genfromtxt(sceneDataPath + "/" + posFile)

centerArray = np.genfromtxt(sceneDataPath + "/"+scene["viewCenter"] +"/Pos.dat")
for b, body in enumerate(flatBD):
    posArray[b] -= centerArray

baseUnitScale = scene["baseUnitScale"]
posArray /= (baseUnitScale * au)
#addBodies(flatBD, leaveTrails, posArray)

initializeScene(1, numSteps)
for b, body in enumerate(flatBD):
    name = body["name"]
    position = posArray[b][0]
    print(name)
    g = body["graphics"]
    size = g["size"]
    colorName = g["color"]
    bodyType = g["representation"]
    color = tuple(c[colorName])
    addActiveBody(name, size, bodyType, color, position, leaveTrails)

bpy.context.scene.frame_current = 1
bpy.ops.object.select_all(action='TOGGLE')

def addKeyFrame(objectName, objectLocation):
    o = bpy.data.objects[objectName]
    o.location = objectLocation
    o.keyframe_insert(data_path="location", index=-1)

def keyFrameBodies(frame):
    C.scene.frame_current = frame
    for b, body in enumerate(flatBD):
        name = body["name"]
        pos = posArray[b][frame]
        addKeyFrame(name, pos)

stepsPerKF = numSteps // scene["numKeyFrames"]
consoleUpdateFreq = 100
for s in range(numSteps):
    if ((s % stepsPerKF) == 0):
        keyFrameBodies(s)
    if ((s % consoleUpdateFreq) == 0):
        print("Frames setup: ", s)

keyFrameBodies(numSteps - 1)
bpy.context.scene.frame_current = 1
