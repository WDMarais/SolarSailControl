import numpy as np
import datetime
from scipy.constants import au

J2000 = datetime.datetime(2000, 1, 1, 12, 0)
def keplerElliptical(M, ecc, tol, maxIter):
    dE = 1
    E = M
    loops = 0
    while((np.abs(dE) > tol) and (loops < maxIter)):
        loops += 1
        dE = (E - ecc * np.sin(E) - M)/(1 - ecc * np.cos(E))
        E -= dE

    return E

def solveKepler(M, ecc, tol=1e-6, maxIter=5):
    if (ecc < 0.9):
        E = keplerElliptical(M, ecc, tol, maxIter)
    else:
        raise Exception("Eccentricity near-hyperbolic")
    return E

def addCorrectionFactor(oE, deltaCenturies, b, c, s, f):
    newOE = oE
    newOE += b * (deltaCenturies**2.0)
    newOE += c * np.cos(f * deltaCenturies)
    newOE += s * np.sin(f * deltaCenturies)
    return newOE

def getCurrentOE(oE0, oEDot, deltaCenturies, cF=False):
    oE = oE0 + oEDot * deltaCenturies
    if not (cF == False):
        b, c, s, f = cF["b"], cF["c"], cF["s"], cF["f"]
        oE = addCorrectionFactor(b, c, s, f)

    return oE

def getAllCurrentOEs(orbitDict, initTime):
    deltaSeconds = (initTime - J2000).total_seconds()
    deltaCenturies = deltaSeconds / (60*60*24*365.25*100)
    a = getCurrentOE(orbitDict["a0"], orbitDict["aDot"], deltaCenturies, cF=False) # au, au/cty
    ecc = getCurrentOE(orbitDict["e0"], orbitDict["eDot"], deltaCenturies, cF=False) # unitless
    I = getCurrentOE(orbitDict["I0"], orbitDict["IDot"], deltaCenturies, cF=False) # deg, deg/cty
    LOP = getCurrentOE(orbitDict["LOP0"], orbitDict["LOPDot"], deltaCenturies, cF=False) # deg, deg/cty
    LAN = orbitDict["LAN0"] + deltaCenturies * orbitDict["LANDot"] # deg. deg/cty
    if "cF" in orbitDict:
        cF = orbitDict["cF"]
        L = getCurrentOE(orbitDict["L0"], orbitDict["LDot"], deltaCenturies, cF)
    else:
        L = getCurrentOE(orbitDict["L0"], orbitDict["LDot"], deltaCenturies, cF=False) # deg, deg/cty

    return a, ecc, I, L, LOP, LAN

def degModuloHalfTopHalfBot(degrees): #Modulo an angle to fall between -180 degrees and 180 degrees
    newDeg = degrees % 360
    if (newDeg > 180):
        newDeg = newDeg - 360
    return newDeg

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
    velocity = np.array([vX, vY, vZ])

    return position, velocity

def getSVFromOE(orbitDict, initTime, parent):
    a, ecc, I, L, LOP, LAN = getAllCurrentOEs(orbitDict, initTime)
    AOP = LOP - LAN
    AOPRad = np.deg2rad(AOP)
    M = L - LOP
    M = degModuloHalfTopHalfBot(M)
    MRad = np.deg2rad(M)
    IRad = np.deg2rad(I)
    LANRad = np.deg2rad(LAN)
    LDot = orbitDict["LDot"]
    LDotRad = np.deg2rad(LDot)
    E = solveKepler(MRad, ecc)
    pos, vel = perifocalToCartesian(a, ecc, E, AOPRad, IRad, LANRad, LDotRad)
    pos = pos * au
    vel = vel * au / (100 * 365.25 * 24 * 60 * 60) #Convert from au / cty to m / s
    if not (parent == None):
        pos += parent.pos
        vel += parent.vel
    return pos, vel
