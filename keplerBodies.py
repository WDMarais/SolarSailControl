#Kepler to cartesian and vice-versa

import numpy as np
import datetime

dimensions = 3
G = 6.67408 * 10 ** -11# Newton's gravitational constant

J2000 = datetime.datetime(2000, 1, 1, 12, 0, 0)
now = datetime.datetime.now()
now = now + datetime.timedelta(seconds=3600)

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

    position = [x, y, z]
    velocity = [vX, vY, vZ]

    return position, velocity

class generalBody(object):
    def __init__(self, name, color, pos = 0, mass="NaN"):
        self.name = name
        self.color = color
        self.mass = mass

        if (pos == 0):
            self.pos = np.zeros(dimensions)
        else:
            self.pos = pos
        self.vel = np.zeros(dimensions)
        self.acc = np.zeros(dimensions)
        self.extForces = np.zeros(dimensions)

    def setCartesianState(self, pos, vel, acc):
        self.pos = pos
        self.vel = vel
        self.acc = acc

    def setPos(self, pos):
        self.pos = pos

    def cartesianToConsole(self):
        print(self.name)
        print("Position: ", self.pos)
        print("Velocity: ", self.vel)
        print()

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

class immobileBody(object):
    def __init__(self, name, position, diameter, color):
        self.name = name
        self.diameter = diameter
        self.color = color
        self.markerSize = 0.001
        self.doCorrect = False
        self.position = position

    def toConsole(self):
        print(self.name)
        #print("Mass:", self.mass)
        print("Position:", self.position)
        print("Diameter:", self.diameter)
        print("Color:", self.color)
        print()

    def isMobile(self):
        return False

    def isNBody(self):
        return False

    def updateState(self, dT):
        pass;

class keplerBody(object):
    def __init__(self, name, diameter, color):
        self.name = name
        self.diameter = diameter
        self.color = color
        self.markerSize = 0.01
        self.doCorrect = False
        self.position = np.zeros(dimensions)

    def isMobile(self):
        return True

    def isNBody(self):
        return False

    def setCorrectionFactor(self, b, c, s, f):
        self.doCorrect = True
        self.b = b
        self.c = c
        self.s = s
        self.f = f

    def toConsole(self):
        print(self.name)
        print("Mass:", self.mass)
        print("Position:", self.position)
        print("Diameter:", self.diameter)
        print("Color:", self.color)

    def updateKOEFromDate(self, newDate):
        deltaSeconds = (newDate - self.date).total_seconds()
        deltaCenturies = deltaSeconds / (60*60*24*365.25*100)
        self.a += self.aDot * deltaCenturies
        self.e += self.eDot * deltaCenturies
        self.i += self.iDot * deltaCenturies
        self.L += self.LDot * deltaCenturies
        self.periLon += self.periLonDot * deltaCenturies
        self.Omega += self.OmegaDot * deltaCenturies
        self.date = newDate

    def setKOE(self, a0, aDot, e0, eDot, i0, iDot, L0, LDot, periLon0, periLonDot, Omega0, OmegaDot):
        self.a = a0
        self.aDot = aDot
        self.e = e0
        self.eDot = a0
        self.i = i0
        self.iDot = a0
        self.L = L0
        self.LDot = LDot
        self.periLon = periLon0
        self.periLonDot = periLonDot
        self.Omega = Omega0
        self.OmegaDot = OmegaDot
        self.date = J2000

    def setCoordsFromKOE(self):
        argPeriH = self.periLon - self.Omega
        meanAnomaly = self.L - self.periLon
        if (self.doCorrect):
            deltaCenturies = (self.date-J2000).total_seconds()/(60*60*24*365.25*100)
            meanAnomaly += self.b * (deltaCenturies**2)
            meanAnomaly += self.c * np.cos(np.deg2rad(self.f * deltaCenturies))
            meanAnomaly += self.s * np.sin(np.deg2rad(self.f * deltaCenturies))

        meanAnomaly = np.deg2rad(meanAnomaly % 360)
        E = meanAnomaly
        dE = 1 #Kludge
        loop = 0

        while((np.abs(dE) > 1e-6) and (loop > 10)):
            loop += 1
            dE = (E - self.e * np.sin(E) - meanAnomaly)/(1-self.e * np.cos(E))
            E -= dE

        P = self.a * (np.cos(E) - self.e)
        #print("e: ", self.e)
        #print("e^2: ", (self.e)**2)
        Q = self.a * (np.sin(E) * np.sqrt(1 - (self.e)**2))

        omega = np.deg2rad(self.periLon - self.Omega)
        x = np.cos(omega) * P - np.sin(omega) * Q
        y = np.sin(omega) * P + np.cos(omega) * Q

        z = x * np.sin(np.deg2rad(self.i))
        x = x * np.cos(np.deg2rad(self.i))

        temp = x
        OmegaRad = np.deg2rad(self.Omega)
        x = temp * np.cos(OmegaRad) - y * np.sin(OmegaRad)
        y = temp * np.sin(OmegaRad) - y * np.cos(OmegaRad)
        self.position = np.array([x, y, z])

    def updateState(self, dT):
        newDate = self.date + datetime.timedelta(seconds = dT)
        self.updateKOEFromDate(newDate)
        self.setCoordsFromKOE()
