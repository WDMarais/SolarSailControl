import numpy as np

dimensions = 3
from scipy.constants import G # Newton's gravitational constant

class spaceBody(object):
    def __init__(self, name, mass, position, velocity, diameter, color):
        self.name = name
        self.mass = mass
        self.gravParam = self.mass * G
        self.position = position
        self.velocity = velocity
        self.acceleration = np.zeros(dimensions)
        self.forces = np.zeros(dimensions)
        self.diameter = diameter
        self.color = color
        self.markerSize = 0.02

    def toConsole(self):
        print(self.name)
        print("Mass:", self.mass)
        print("Position:", self.position)
        print("Diameter:", self.diameter)
        print("Color:", self.color)

    def logState(self, frame):
        print(self.name, ': Frame ', frame)
        print("Forces: ", self.forces)
        print("Acceleration: ", self.acceleration)
        print("Velocity: ", self.velocity)
        print("Position: ", self.position)
        print(' ')

    def updatePosition(self, timeStep):
        self.position += timeStep * self.velocity

    def updateVelocity(self, timeStep):
        self.velocity += timeStep * self.acceleration

    def updateAcceleration(self):
        self.acceleration = self.forces / self.mass

    def computeForces(self, others):
        self.forces = np.zeros(dimensions)
        for other in others:
            distanceVector = other.position - self.position
            dSquared = np.dot(distanceVector, distanceVector)
            distanceMagnitude = np.sqrt(dSquared)
            fDir = distanceVector / distanceMagnitude
            self.forces += self.gravParam * (other.mass / dSquared) * fDir

    def updateState(self, others, timeStep):
        self.computeForces(others)
        self.updateAcceleration()
        self.updateVelocity(timeStep)
        self.updatePosition(timeStep)
