import simUtils
import timeUtils
import fileUtils
from spaceBodies import spaceBody
from spaceBodies import thrustSatellite
from spaceBodies import solarSailSatellite
import numpy as np
import json
from scipy.constants import au

genPath = "general.json"
with open(genPath) as g:
    generalSettings = json.load(g)
g.close()

scenePath = generalSettings["sceneFileDir"] + "/" + generalSettings["sceneFile"]

with open(scenePath) as s:
    scene = json.load(s)
s.close()

sceneName = scene["name"]
bodiesDict = scene["bodies"]
initTime = timeUtils.dictToDateTime(scene["initTime"])
timeStep = scene["timeStep"]
numSteps = scene["numSteps"]
numDimensions = 3
bodies = simUtils.initBodiesRecursive(bodiesDict, initTime)

dataPath = "scenes/" + sceneName + "/"
fileUtils.createDirs(bodies, dataPath)
numBodies = len(bodies)
posArray = np.zeros((numBodies, numSteps, numDimensions))
velArray = np.zeros((numBodies, numSteps, numDimensions))

consoleUpdateFreq = 100
c = consoleUpdateFreq

def runStep(bodies, frame):
    for b, body in enumerate(bodies):
        others = np.delete(bodies, b)
        if (type(body) is thrustSatellite):
            forceMagnitude = 2
            body.thrustWidenOrbit(forceMagnitude)
        elif (type(body) is solarSailSatellite):
            sun = bodies[0]
            lineToSun = body.pos - sun.pos
            idealSailDir = lineToSun / np.linalg.norm(lineToSun)
            body.setSailDirection(idealSailDir)
            body.updateSolarForce(bodies[0]) # assume sun is first in array
        body.computeForces(others)
        body.updateState(timeStep)
        posArray[b][frame] = body.pos
        velArray[b][frame] = body.vel

def saveArrays(posArray, velArray):
    for b, body in enumerate(bodies):
        fileName = dataPath + body.name + '/' + 'Pos.dat'
        f = open(fileName, 'w')
        np.savetxt(f, posArray[b])
        f.close()

        fileName = dataPath + body.name + '/' + 'Vel.dat'
        f = open(fileName, 'w')
        np.savetxt(f, velArray[b])
        f.close()

for f in range(numSteps):
    runStep(bodies, f)
    if (c >= (consoleUpdateFreq)):
        print("Steps Executed: ", f, "/", numSteps)
        c = 1
    else:
        c += 1

saveArrays(posArray, velArray)

print("Simulation Finished")
