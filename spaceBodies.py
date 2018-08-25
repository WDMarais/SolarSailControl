import numpy as np

from scipy.constants import G # Newton's gravitational constant
from scipy.constants import au
import orbitUtils

dimensions = 3

class spaceBody(object):
    def __init__(self, name, mass):
        self.name = name
        self.mass = mass
        self.gravParam = self.mass * G
        self.pos = np.zeros(dimensions)
        self.vel = np.zeros(dimensions)
        self.acc = np.zeros(dimensions)
        self.forces = np.zeros(dimensions)
        self.hasInitSV = False

    def setSV(self, stateVectorDict, parent):
        self.pos = np.array(stateVectorDict["pos"])
        self.vel = np.array(stateVectorDict["vel"])
        if not (parent == None):
            self.pos += parent.pos
            self.vel += parent.vel
        self.hasInitSV = True

    def setSVFromOE(self, oEDict, initTime, parent):
        self.pos, self.vel = orbitUtils.getSVFromOE(oEDict, initTime, parent)
        self.hasInitSV = True

    '''
    def scaleSVFromTo(fromUnit, toUnit):
        if (fromUnit == "JPLOE"): #au, au/cty
            self.pos *= au
    '''

    def getNewtonInfluence(self, other):    # Used to determine which bodies will have greatest influence on
        r = self.pos - other.pos            # object. Determines r, r^2 and G*m(self)/r^2 - uses G*m(self)/r^2
        rSquared = r.dot(r)                 # to determine greatest influence, returns r, rSquared to save comp
        newtonInfluence = other.gravParam * rSquared
        return newtonInfluence, r, rSquared

    def logState(self):
        print(self.name)
        print("Forces: ", self.forces)
        print("Acceleration: ", self.acc)
        print("Velocity: ", self.vel)
        print("Position: ", self.pos)
        print(' ')

    def updatePos(self, dT):
        self.pos += dT * self.vel

    def updateVel(self, dT):
        self.vel += dT * self.acc

    def updateAcc(self):
        self.acc = self.forces / self.mass

    def computeForces(self, others):
        self.forces = np.zeros(dimensions)
        for other in others:
            distanceVector = other.pos - self.pos
            dSquared = np.dot(distanceVector, distanceVector)
            distanceMagnitude = np.sqrt(dSquared)
            fDir = distanceVector / distanceMagnitude
            self.forces += self.gravParam * (other.mass / dSquared) * fDir

    def updateState(self, dT):
        self.updateAcc() #update acceleration using forces
        self.updateVel(dT)
        self.updatePos(dT)

class solarSailSatellite(spaceBody):
    def __init__(self, name, mass, sailArea, sailDirection = None):
        super(solarSailSatellite, self).__init__(name, mass)
        self.sailArea = sailArea[0]
        self.rho_s = 1 # assume perfect reflectivity
        if (sailDirection == None):
            self.sailDirection = np.array([0.0, 0.0, -1.0])
        else:
            self.sailDirection = np.array(sailDirection)
        self.sailDirection = self.sailDirection.flatten()

    def updateSolarForce(self, sunBody):
        r = self.pos - sunBody.pos
        rayDirection = r / np.sqrt(r.dot(r))
        tRatio = rayDirection.dot(self.sailDirection)
        exposedArea = np.abs(tRatio) * self.sailArea
        self.sailDirection = np.linalg.norm(self.sailDirection)
        self.solarForce = (tRatio * exposedArea * self.Psolar) * (1 + self.rho_s) * self.sailDirection

    def setSailDirection(self, sailDirection):
        self.sailDirection = sailDirection

    '''
    def setPsolar(self, Psolar):
        self.Psolar =
    '''

    def setIdealPsolar(self):
        self.Psolar = 4.563e-6

    def computeForces(self, others):
        super(solarSailSatellite, self).computeForces(others)
        self.forces += self.solarForce

class thrustSatellite(spaceBody):
    def __init__(self, name, mass, thrustVector = None):
        super(thrustSatellite, self).__init__(name, mass)
        if (thrustVector == None):
            self.thrustVector = np.zeros(dimensions)
        else:
            self.thrustVector = thrustVector

    def setThrustVector(self, thrustVector=np.zeros(dimensions)):
        self.thrustVector = thrustVector

    def computeForces(self, others):
        super(thrustSatellite, self).computeForces(others)
        self.forces += self.thrustVector

    def setThrustToPos(self, pos, magnitude):
        r = self.pos - pos
        rMag = np.sqrt(r.dot(r))
        uR = r/rMag
        thrust = uR * magnitude
        self.setThrustVector(thrust)

    def setThrustAwayFromPos(self, pos, magnitude):
        r = self.pos - pos
        rMag = np.sqrt(r.dot(r))
        uR = r/rMag
        thrust = -uR * magnitude
        self.setThrustVector(thrust)

    def thrustWidenOrbit(self, magnitude):
        v = self.vel
        vMag = np.sqrt(v.dot(v))
        uV = v/vMag
        thrust = uV * magnitude
        self.setThrustVector(thrust)

    def thrustNarrowOrbit(self, magnitude):
        v = self.vel
        vMag = np.sqrt(v.dot(v))
        uV = v/vMag
        thrust = -uV * magnitude
        self.setThrustVector(thrust)
