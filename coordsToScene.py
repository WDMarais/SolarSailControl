import bpy
import numpy as np

bodies = [	
        'Sun', 'Mercury', 'Venus', 'Earth',
		'Mars', 'Jupiter', 'Saturn', 'Uranus',
		'Neptune', 'Pluto'
	]

vectors = ['Pos', 'Vel', 'Acc', 'F', 'Angle']

dataDir = 'bodies/'

def addSphere(sphereName, pos):
    layers = 20 * [False]
    layers[0] = True
    bpy.ops.mesh.primitive_uv_sphere_add(size = 0.3, location=pos, layers=layers)
    bpy.context.active_object.name = sphereName

def addKeyFrame(objectName, objectLocation):
    o = bpy.data.objects[objectName]
    o.location = objectLocation
    o.keyframe_insert(data_path="location", index=-1)
    
vecIndex = 0
for b in bodies:
    fileName = dataDir + b + '/' + vectors[0] + '.dat'
    positions = np.array(np.loadtxt(fileName, ndmin=2))
    positions = positions.reshape(1000, 3)
    addSphere(b, positions[0])
    for f in range(1000):
        bpy.context.scene.frame_set(f)
        addKeyFrame(b, tuple(positions[f]))