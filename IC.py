import numpy as np
import json
from spaceBodies import spaceBody
from spaceBodies import thrustSatellite
from keplerBodies import immobileBody
from keplerBodies import keplerBody
from keplerBodies import generalBody

import datetime

dimensions = 3
from scipy.constants import G # Newton's gravitational constant
from scipy.constants import au

with open('colors.json') as f:
    colors = json.load(f)
f.close()

with open('general.json') as g:
    generalDetails = json.load(g)
    sceneFile = generalDetails["sceneFile"]
g.close()

def basicScene():
    name = 'Sun'
    mass = 1.98892 * 10 ** 30
    position = np.zeros(dimensions)
    velocity = np.zeros(dimensions)
    diameter = 0.2
    color = colors["yellow"]
    Sun = spaceBody(name, mass, position, velocity, diameter, color)

    name = 'Venus'
    mass = 4.8685 * 10 ** 24
    position = np.array([0.723 * au, 0.0, 0.0])
    velocity = np.array([0.0, -35.02 * 1000, 0.0])
    diameter = 0.1
    color = colors["vYellow"]
    Venus = spaceBody(name, mass, position, velocity, diameter, color)

    name = 'Earth'
    mass = 10.0
    position = np.array([-1 * au, 0.0, 0.0])
    velocity = np.array([0, 29.783 * 1000, 0])
    diameter = 0.1
    color = colors["blue"]
    Earth = spaceBody(name, mass, position, velocity, diameter, color)

    bodies = [Sun, Venus, Earth]
    scaleFactor = 1 * au
    return bodies, scaleFactor

def basicScene2():
    with open("setupBasic.json") as basic:
        theScene = json.load(basic)
    basic.close()
    with open('colors.json') as f:
        colors = json.load(f)
    f.close()

    bodyInfo = theScene["bodies"]
    bodies = []

    scaleFactor = 1 * au

    for b in bodyInfo:
        name = b["name"]
        diameter = np.array(b["diameter"])
        colorID = b["color"]
        color = colors[colorID]
        mass = b["mass"]
        startPos = np.array(b["startPos"]) * scaleFactor
        startVel = np.array(b["startVel"]) * scaleFactor
        body = spaceBody(name, diameter, color, mass, startPos, startVel)
        bodies = bodies + [body]

    return bodies, scaleFactor

def keplerian(startDate):
    bodies = []

    name = 'Sun'
    diameter = 0.06
    position = np.array([0.0, 0.0, 0.0])
    color = colors["yellow"]
    print("Yellow: ", color)
    sun = immobileBody(name, position, diameter, color)
    bodies = bodies + [sun]

    name = 'Mercury'
    diameter = 0.03
    color = colors["magenta"]
    mercury = keplerBody(name, diameter, color)
    a0 = 0.38709843
    e0 = 0.20563661
    i0 = 7.00559432
    L0 = 252.25166724
    periLon0 = 77.45771895
    Omega0 = 48.33961819
    aDot = 0.00000037
    eDot = 0.00002123
    iDot = -0.00590158
    LDot = 149472.67486623
    periLonDot = 0.15940013
    OmegaDot = -0.12214182
    mercury.setKOE(a0, aDot, e0, eDot, i0, iDot, L0, LDot, periLon0, periLonDot, Omega0, OmegaDot)
    mercury.updateKOEFromDate(startDate)
    mercury.setCoordsFromKOE()
    bodies = bodies + [mercury]

    name = 'Venus'
    diameter = 0.03
    color = colors["vYellow"]
    venus = keplerBody(name, diameter, color)
    a0 = 0.72332102
    aDot = -0.00000026
    e0 = 0.00676399
    eDot = -0.00005107
    i0 = 3.39777545
    iDot = 0.00043494
    L0 = 181.97970850
    LDot = 58517.81560260
    periLon = 131.76755713
    periLonDot = 0.05679648
    Omega0 = 76.67261496
    OmegaDot = -0.27274174
    venus.setKOE(a0, aDot, e0, eDot, i0, iDot, L0, LDot, periLon0, periLonDot, Omega0, OmegaDot)
    venus.updateKOEFromDate(startDate)
    venus.setCoordsFromKOE()
    bodies = bodies + [venus]

    name = 'Earth'
    diameter = 0.03
    color = colors["blue"]
    earth = keplerBody(name, diameter, color)
    a0 = 1.00000018
    aDot = -0.00000003
    e0 = 0.01673163
    eDot = -0.00003661
    i0 = -0.00054346
    iDot = -0.01337178
    L0 = 100.46691572
    LDot = 35999.37306329
    periLon = 102.93005885
    periLonDot = 0.31795260
    Omega0 = -5.11260389
    OmegaDot = -0.24123856
    earth.setKOE(a0, aDot, e0, eDot, i0, iDot, L0, LDot, periLon0, periLonDot, Omega0, OmegaDot)
    earth.updateKOEFromDate(startDate)
    earth.setCoordsFromKOE()
    bodies = bodies + [earth]

    name = 'Mars'
    diameter = 0.03
    color = colors["red"]
    mars = keplerBody(name, diameter, color)
    a0 = 1.52371243
    aDot = 0.00000097
    e0 = 0.09336511
    eDot = 0.00009149
    i0 = 1.85181869
    iDot = -0.00724757
    L0 = -4.56813164
    LDot = 19140.29934243
    periLon = -23.91744784
    periLonDot = 0.45223625
    Omega0 = 49.71320984
    OmegaDot = -0.26852431
    mars.setKOE(a0, aDot, e0, eDot, i0, iDot, L0, LDot, periLon0, periLonDot, Omega0, OmegaDot)
    mars.updateKOEFromDate(startDate)
    mars.setCoordsFromKOE()
    bodies = bodies + [mars]
    '''
    name = 'Jupiter'
    diameter = 0.03
    color = colors["orange"]
    jupiter = keplerBody(name, diameter, color)
    a0 = 5.20248019
    aDot = -0.00002864
    e0 = 0.04853590
    eDot = 0.00018026
    i0 = 1.29861416
    iDot = -0.00322699
    L0 = 34.33479152
    LDot = 3034.90371757
    periLon = 14.27495244
    periLonDot = 0.18199196
    Omega0 = 100.29282654
    OmegaDot = 0.13024619
    b = -0.00012452
    c = 0.06064060
    s = -0.35635438
    f = 38.35125000
    jupiter.setKOE(a0, aDot, e0, eDot, i0, iDot, L0, LDot, periLon0, periLonDot, Omega0, OmegaDot)
    jupiter.setCorrectionFactor(b, c, s, f)
    jupiter.updateKOEFromDate(startDate)
    jupiter.setCoordsFromKOE()
    bodies = bodies + [jupiter]

    name = 'Saturn'
    diameter = 0.03
    color = colors["cream"]
    saturn = keplerBody(name, diameter, color)
    a0 = 9.54149883
    aDot = -0.00003065
    e0 = 0.05550825
    eDot = -0.00032044
    i0 = 2.49424102
    iDot = 0.00451969
    L0 = 50.07571329
    LDot = 1222.11494724
    periLon = 92.86136063
    periLonDot = 0.54179478
    Omega0 = 113.63998701
    OmegaDot = -0.25015002
    b = 0.00025899
    c = -0.13434469
    s = 0.87320147
    f = 38.35125000
    saturn.setKOE(a0, aDot, e0, eDot, i0, iDot, L0, LDot, periLon0, periLonDot, Omega0, OmegaDot)
    saturn.setCorrectionFactor(b, c, s, f)
    saturn.updateKOEFromDate(startDate)
    saturn.setCoordsFromKOE()
    bodies = bodies + [saturn]

    name = 'Uranus'
    diameter = 0.03
    color = colors["foamGreen"]
    uranus = keplerBody(name, diameter, color)
    a0 = 19.18797948
    aDot = -0.00020455
    e0 = 0.04685740
    eDot = -0.00001550
    i0 = 0.77298127
    iDot = -0.00180155
    L0 = 314.20276625
    LDot = 428.49512595
    periLon = 172.43404441
    periLonDot = 0.09266985
    Omega0 = 73.96250215
    OmegaDot = 0.05739699
    b = 0.00058331
    c = -0.97731848
    s = 0.17689245
    f = 7.67025000
    uranus.setKOE(a0, aDot, e0, eDot, i0, iDot, L0, LDot, periLon0, periLonDot, Omega0, OmegaDot)
    uranus.setCorrectionFactor(b, c, s, f)
    uranus.updateKOEFromDate(startDate)
    uranus.setCoordsFromKOE()
    bodies = bodies + [uranus]

    name = 'Neptune'
    diameter = 0.03
    color = colors["cyan"]
    neptune = keplerBody(name, diameter, color)
    a0 = 30.06952752
    aDot = 0.00006447
    e0 = 0.00895439
    eDot = 0.00000818
    i0 = 1.77005520
    iDot = 0.00022400
    L0 = 304.22289287
    LDot = 218.46515314
    periLon0 = 46.68158724
    periLonDot = 0.01009938
    Omega0 = 131.78635853
    OmegaDot = -0.00606302
    b = -0.00041348
    c = 0.68346318
    s = -0.10162547
    f = 7.6702500
    neptune.setKOE(a0, aDot, e0, eDot, i0, iDot, L0, LDot, periLon0, periLonDot, Omega0, OmegaDot)
    neptune.setCorrectionFactor(b, c, s, f)
    neptune.updateKOEFromDate(startDate)
    neptune.setCoordsFromKOE()
    bodies = bodies + [neptune]
    '''
    scaleFactor = 1
    return bodies, scaleFactor

def keplerian2(startDate):
    with open(sceneFile) as s:
        myScene = json.load(s)
    s.close()

    bodyDict = myScene["bodies"]
    bodies = []

    for b in bodyDict:
        name = b["name"]
        mass = b["mass"]
        type = b["type"]
        diameter = b["diameter"]
        colorName = b["color"]
        color = colors[colorName]

        if "orbitElements" in b:
            orbitElements = b["orbitElements"]
            body = spaceBody(name, diameter, color, mass)
            body.initFromOE(orbitElements, startDate)

        else:
            if "startPos" in b:
                startPos = np.array(b["startPos"])
            if "startVel" in b:
                startVel = np.array(b["startVel"])
            if (type == "p"):
                body = spaceBody(name, diameter, color, mass, startPos, startVel)
            elif (type == "ts"):
                body = thrustSatellite(name, diameter, color, mass, startPos, startVel)

        bodies = bodies + [body]

    distanceUnit = myScene["distanceUnit"]
    timeUnit = myScene["timeUnit"]

    if (distanceUnit == "au"):
        dScaleFactor = au
    else:
        dScaleFactor = 1.0

    if (timeUnit == "cty"):
        tScaleFactor = 100 * 365.25 * 24 * 60 * 60
    else:
        tScaleFactor = 1.0

    return bodies, dScaleFactor, tScaleFactor
