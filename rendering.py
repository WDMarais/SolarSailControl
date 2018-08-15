import bpy, bmesh
from IC import keplerian
#######################
# Rendering Constants #
#######################
xRes, yRes = 1920, 1080
resPercent = 50.0
leaveMotionTrails = True

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

initializeScene(firstTimeStep, lastTimeStep)

for body in bodies:
    name = body.name
    position = body.position / distanceFactor
    diameter = body.diameter
    color = body.color
    addNamedSphere(name, position, diameter, color)

bpy.context.scene.frame_current = 1
bpy.ops.object.select_all(action='TOGGLE')

activeLayers = returnLayerTuple(0)

loc = (-0.2, -0.05, 5.0)
rot = (0.0, 0.0, 45.0)
addCamera(loc, rot, activeLayers)
bpy.context.scene.camera = bpy.data.objects['Camera']

loc = (0.0, 3.0, 2.0)
rot = (0.0, 0.0, 0.0)
bpy.ops.object.lamp_add(type='POINT', location = loc, rotation = rot, layers = activeLayers)

loc = (0.0, -3.0, 2.0)
rot = (0.0, 0.0, 0.0)
bpy.ops.object.lamp_add(type='POINT', location = loc, rotation = rot, layers = activeLayers)

for f in range(firstTimeStep, lastTimeStep):
    bpy.context.scene.frame_set(f)
    render_and_save(f)
