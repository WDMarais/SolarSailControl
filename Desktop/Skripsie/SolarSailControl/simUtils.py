from spaceBodies import spaceBody
from spaceBodies import thrustSatellite
from spaceBodies import solarSailSatellite

def initBody(bodyDict, initTime, parent = None):
    name = bodyDict["name"]
    p = bodyDict["physics"]
    mass = p["mass"]
    category = p["category"]
    if (category =="GENERAL"):
        body = spaceBody(name, mass)
    elif (category =="THRUSTSAT"):
        body = thrustSatellite(name, mass)
    elif (category =="SOLSAT"):
        p = bodyDict["physics"]
        area = p["sailArea"],
        print("InitSailArea")
        print(area)
        sailDir = p["sailDirection"],
        body = solarSailSatellite(name, mass, area, sailDir)
        body.setIdealPsolar()
    i = p["initialization"]
    iCategory = i["category"]

    if (iCategory == "CARTESIAN"):
        body.setSV(i, parent)
    elif (iCategory == "JPLOE"):
        body.setSVFromOE(i, initTime, parent)
    else:
        raise Expection("Invalid type provided to " + name)

    return body

def initBodiesRecursive(bodiesDict, initTime, parent = None):
    bodies = []
    for b in bodiesDict:
        body = initBody(b, initTime, parent)
        bodies = bodies + [body]
        if "children" in b:
            children = initBodiesRecursive(b["children"], initTime, body)
            bodies = bodies + children
    return bodies
