import numpy as np
import datetime

dimensions = 3
G = 6.67408 * 10 ** -11# Newton's gravitational constant

J2000 = datetime.datetime(2000, 1, 1, 12, 0, 0)
now = datetime.datetime.now()
now = now + datetime.timedelta(seconds=3600)
print(now)

class immobileBody(object):
    def __init__(self, name, position, diameter, color):
        self.name = name
        self.diameter = diameter
        self.color = color
        self.markerSize = 0.02
        self.doCorrect = False
        self.position = position

    def isMobile(self):
        return False

    def isNBody(self):
        return False

    def updateState(self, dT):
        pass;

    def getPosition():
        return self.position

class keplerBody(object):
    def __init__(self, name, diameter, color):
        self.name = name
        self.diameter = diameter
        self.color = color
        self.markerSize = 0.02
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

        meanAnomaly = meanAnomaly % 360
        if (meanAnomaly > 180):
            meanAnomaly = 180 - meanAnomaly

        E = meanAnomaly
        dE = 1 #Kludge
        loop = 0
        #print(self.name)
        e = (np.rad2deg(self.e)) % 360
        #print(e)
        while((np.abs(dE) > 1e-6) and (loop < 10)):
            loop += 1
            dM = meanAnomaly - (E - e * np.sin(E))
            dE = dM/(1- self.e * np.cos(E))
            E += dE

        #if (loop == 10):
            #print("Loop exceeded")

        P = self.a * (np.cos(E) - self.e)
        #print()
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
