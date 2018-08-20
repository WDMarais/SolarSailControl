###############
# All imports #
###############
import sys
import os
import datetime
import numpy as np
import json
from scipy.constants import au

#filePath = '/home/wdmarais/Desktop/Skripsie/SolarSailControl/IC.py'
#fileDir = os.path.dirname(filePath)
#sys.path.append(fileDir)
#print(sys.path)
from IC import basicScene
from IC import keplerian
from IC import keplerian2
from spaceBodies import thrustSatellite
##################
#Scene Parameters#
##################

with open("general.json") as g:
    gen = json.load(g)
g.close()

with open(gen["sceneFile"]) as s:
    scene = json.load(s)
s.close()

numDimensions = 3
firstTime = 1
numSteps = scene["numSteps"]
dT = scene["timeStep"]

#bodies, distanceFactor = basicScene()
#bodies, distanceFactor = keplerian(theDate)

theDate = datetime.datetime.now()
bodies, dScaleFactor, tScaleFactor = keplerian2(theDate)
numBodies = len(bodies)
dataArray = np.zeros((numBodies, numSteps, numDimensions))

###########
#Main code#
###########
#print("Hello")
#location = (0, 0, 0)
#rotation = (0, 0, 0)
#whichLayers = returnLayerTuple(1)
#addCamera(location, rotation, whichLayers)

ticker = 0
frameGap = 10
dataPath = scene["sceneName"] + "/"

def createDir(newDirectory):
    if not os.path.exists(os.path.dirname(newDirectory)):
    	try:
            os.makedirs(os.path.dirname(newDirectory), exist_ok=True)
    	except OSError as exc:
    		raise

for b in bodies:
    b.pos *= dScaleFactor
    createDir(dataPath + b.name + '/')

for f in range(numSteps):
    print("TimeStep: ", f)
    ticker += 1

    for b, body in enumerate(bodies):
        others = np.delete(bodies, b)
        if (type(body) is thrustSatellite):
            forceMagnitude = 2
            position = bodies[0].pos
            body.thrustWidenOrbit(forceMagnitude)
        body.updateState(others, dT)

        dataArray[b][f] = body.pos

for b, body in enumerate(bodies):
    fileName = dataPath + body.name + '/' + 'Pos.dat'
    f = open(fileName, 'w')
    print("Shape: ", dataArray[b].shape)
    np.savetxt(f, dataArray[b])
    f.close()
