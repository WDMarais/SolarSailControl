import numpy as np
import datetime
J2000 = datetime.datetime(2000, 1, 1, 12, 0, 0)

dimensions = 3
from scipy.constants import G # Newton's gravitational constant
from scipy.constants import au

def solveKepler(M, ecc, tol=1e-6, maxIter=5):
    E = M
    dE = 1
    loops = 0
    while((np.abs(dE) > tol) and (loops < maxIter)):
        loops += 1
        dE = (E - ecc * np.sin(E) - M)/(1 - ecc * np.cos(E))
        E -= dE

    return E

E = solveKepler(np.deg2rad(27.0), 0.5)

def perifocalToCartesian(a, ecc, EA, AOP, I, LAN, LDot): #inputs in /cty, rad and rad/cty, output in AU and AU per century
    ecc2 = ecc**2
    P = a * (np.cos(EA) - ecc)
    Q = a * np.sin(EA) * np.sqrt(1 - ecc2)

    vP = -a * np.sin(EA) * LDot / (1 - ecc * np.cos(EA))
    vQ = a * np.cos(EA) * np.sqrt(1 - ecc2) * LDot / (1 - ecc * np.cos(EA))

    x = np.cos(AOP) * P - np.sin(AOP) * Q
    vX = np.cos(AOP) * vP - np.sin(AOP) * vQ

    y = np.sin(AOP) * P + np.cos(AOP) * Q
    vY = np.sin(AOP) * vP + np.cos(AOP) * vQ

    z = np.sin(I) * x
    vZ = np.sin(I) * vX

    x = np.cos(I) * x
    vX = np.cos(I) * vX

    xT = x
    vXT = vX

    x = np.cos(LAN) * xT - np.sin(LAN) * y
    vX = np.cos(LAN) * vXT - np.sin(LAN) * vY

    y = np.sin(LAN) * xT + np.cos(LAN) * y
    vY = np.sin(LAN) * vXT + np.cos(LAN) * vY

    position = np.array([x, y, z])
    print("Type returned:")
    print(type(position))
    velocity = np.array([vX, vY, vZ])

    return position, velocity

class spaceBody(object):
    def __init__(self, name, diameter=None, color=None, mass=None, pos=None, vel=None):
        self.name = name
        self.mass = mass
        self.gravParam = self.mass * G

        if (pos is None):
            self.pos = np.zeros(dimensions)
        else:
            self.pos = pos

        if (vel is None):
            self.vel = np.zeros(dimensions)
        else:
            self.vel = vel

        self.acc = np.zeros(dimensions)
        self.forces = np.zeros(dimensions)
        self.diameter = diameter
        self.color = color
        self.markerSize = 0.02

    def toConsole(self):
        print(self.name)
        print("Mass: ", self.mass)
        print("Diameter: ", self.diameter)
        print("Color: ", self.color)
        print("Velocity: ", self.vel)
        print("Position: ", self.pos)
        print()

    def isMobile(self):
        return True

    def isNBody(self):
        return True

    def logState(self, frame):
        print(self.name, ': Frame ', frame)
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

    def initFromOE(self, orbitDict, ephemerisTime):
        deltaSeconds = (ephemerisTime - J2000).total_seconds()
        deltaCenturies = deltaSeconds / (60*60*24*365.25*100)
        a = orbitDict["a0"] + deltaCenturies * orbitDict["aDot"] # au
        ecc = orbitDict["e0"] + deltaCenturies * orbitDict["eDot"] # no units, just ecc
        I = orbitDict["I0"] + deltaCenturies * orbitDict["IDot"] # deg
        L = orbitDict["L0"] + deltaCenturies * orbitDict["LDot"] # deg
        LDot = orbitDict["LDot"]
        LOP = orbitDict["LOP0"] + deltaCenturies * orbitDict["LOPDot"] # deg
        LAN = orbitDict["LAN0"] + deltaCenturies * orbitDict["LANDot"] # deg
        AOP = LOP - LAN

        AOPRad = np.deg2rad(LOP - LAN)

        M = (L - LOP) % 360
        if (M > 180):
            M = M - 360

        MRad = np.deg2rad(M)
        IRad = np.deg2rad(I)
        LANRad = np.deg2rad(LAN)
        LDotRad = np.deg2rad(LDot)

        E = solveKepler(MRad, ecc)

        self.pos, self.vel = perifocalToCartesian(a, ecc, E, AOPRad, IRad, LANRad, LDotRad)
        self.vel = self.vel * au / (100 * 365.25 * 24 * 60 * 60)

    def updateState(self, others, dT):
        self.computeForces(others)
        self.updateAcc()
        self.updateVel(dT)
        self.updatePos(dT)

class thrustSatellite(spaceBody):
    def setThrustVector(self, thrustVector=np.zeros(3)):
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
