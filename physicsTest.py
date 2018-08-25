import numpy as np
import os
import errno

dataDir = 'bodies/'

bodies = [	'Sun', 'Mercury', 'Venus', 'Earth',
		'Mars', 'Jupiter', 'Saturn', 'Uranus',
		'Neptune', 'Pluto'
	]

'''
test = np.array([[1.123, 2.456, 5.6667]])
fileName = 'coords/test.dat'

if not os.path.exists(os.path.dirname(fileName)):
	try:
		os.makedirs(os.path.dirname(fileName))
	except OSError as exc:
		raise

f = open(fileName, 'ab')
np.savetxt(f, test)
f.close()
'''
numTimeStep = 1000
numCenterRevs = 10

dimensions = (numTimeStep, 3)
threeCoords = np.zeros(dimensions)
numBodies = len(bodies)
numVectors = 5
bodyCoords = np.array([threeCoords] * numVectors)
allCoords = np.array([bodyCoords] * numBodies)

logName = 'general.log'

if not os.path.exists(os.path.dirname(dataDir + logName)):
	try:
		os.makedirs(os.path.dirname(dataDir + logName))
	except OSError as exc:
		raise

angleStep = 2 * np.pi * numCenterRevs / numTimeStep
z = 0.0000005

for i, b in enumerate(bodies):
	for j in range(numVectors):
		for k in range(numTimeStep):
			radius = i
			angle = (k * angleStep)/(radius + 1)
			x = radius * np.cos(angle)
			y = radius * np.sin(angle)
			allCoords[i, j, k] = [x, y, z]

vectors = ['Pos', 'Vel', 'Acc', 'F', 'Angle']

print(allCoords.shape)

for j, b in enumerate(bodies):
	for k in range(numVectors):
		fileName = dataDir + b + '/' + vectors[k] + '.dat'

		if not os.path.exists(os.path.dirname(fileName)):
			try:
				os.makedirs(os.path.dirname(fileName))
			except OSError as exc:
				raise

		f = open(fileName, 'w')
		np.savetxt(f, allCoords[j][k])
		f.close()
'''
for i in range(numTimeStep):
	for j, b in enumerate(bodies):
		for k in range()
		x = j * np.cos(i*angleStep/(j+1))
		y = j * np.sin(i*angleStep/(j+1))
		bodyCoords[j][i] = [x, y, z]

for j, b in enumerate(bodies):
	fileName = dataDir + b + '.dat'
	f = open(fileName, 'w')
	np.savetxt(f, bodyCoords[j])
'''
