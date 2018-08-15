###############
# All imports #
###############
import sys
import os
import datetime
import numpy as np
from scipy.constants import au

filePath = '/home/wdmarais/Desktop/Skripsie/SolarSailControl/IC.py'
fileDir = os.path.dirname(filePath)
sys.path.append(fileDir)
print(sys.path)
from IC import basicScene
from IC import keplerian

##################
#Scene Parameters#
##################
numDimensions = 3
firstTime = 1
numSteps = 1000
dT = 24*60*60

#bodies, distanceFactor = basicScene()

theDate = datetime.datetime.now()
bodies, distanceFactor = keplerian(theDate)

bodyPositions = np.zeros((len(bodies), numSteps, numDimensions))
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
dataPath = 'bodies/'

def createDir(newDirectory):
    if not os.path.exists(os.path.dirname(newDirectory)):
    	try:
            os.makedirs(os.path.dirname(newDirectory), exist_ok=True)
    	except OSError as exc:
    		raise

for b in bodies:
    createDir(dataPath + b.name + '/')

for f in range(numSteps):
    print("Frame: ", f)
    ticker += 1

    for b, body in enumerate(bodies):
        others = np.delete(bodies, b)
        if body.isNBody():
            body.updateState(others, dT)
        else:
            body.updateState(dT)

        bodyPositions[b][f] = body.position

for b, body in enumerate(bodies):
    fileName = dataPath + body.name + '/' + 'Pos.dat'
    f = open(fileName, 'w')
    np.savetxt(f, bodyPositions[b])
