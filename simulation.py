import orbitUtils
import timeUtils
import json
import spaceBodies
import datetime

def initBodyFromDict(bodyDict):
    name = bodyDict["name"]
    p = bodyDict["physics"]
    mass = p["mass"]
    objType = p["type"]
    initType = p["type"]
    if (objType == "GENERAL"):
        body = spaceBodies.spaceBody(name, mass)
    elif (objType == "THRUSTSAT"):
        body = spaceBodies.thrustSatellite(name, mass)
    else:
        raise Exception("Invalid objType passed to ", name)
    return body

def initBodiesFromDict(bodiesDict):
    bodies = []
    bodiesIndexMap = {}
    for i, bodyDict in enumerate(bodiesDict):
        body = initBodyFromDict(bodyDict)
        bodies = bodies + [body]
        indexMap = {body.name:i}
        bodiesIndexMap.update(indexMap)

    return bodies, bodiesIndexMap

def setAbsoluteSV(body, initDict, initTime):
    initType = initDict["type"]
    if (initType == "cartesian"):
        body.setSV(initDict)
    elif (initType == "orbitElements"):
        body.setSVFromOE(initDict, initTime)
    else:
        raise Exception("Invalid Init method passed to ", body.name)

def setRelativeSV(body, parentBody, bodyDict, initTime):
    parentPos = parentBody.pos
    parentVel = parentBody.vel

def setAbsoluteSVs(bodies, bodiesDict, initTime):
    for i, b in enumerate(bodiesDict):
        body = bodies[i]
        bodyDict = bodiesDict[i]
        p = bodyDict["physics"]
        isAbsolute = True
        if "initRelativeTo" in p:
            if not (p["initRelativeTo"] == "ORIGIN"):
                isAbsolute = False
        if isAbsolute:
            initDict = p["initDict"]
            setAbsoluteSV(body, initDict, initTime)

def setRelativeSVs(bodies, bodiesDict, initTime, bodiesIndexMap):
    allInitialized = False
    while (allInitialized == False):
        allInitialized = True
        for i, bodyDict in enumerate(bodiesDict):
            p = bodyDict["physics"]
            isRelative = False
            relativeTo = p["initRelativeTo"]
            if "initRelativeTo" in p:
                if not (relativeTo == "ORIGIN"):
                    isRelative = True

            if isRelative:
                parentIndex = bodiesIndexMap["relativeTo"]
                parentBody = bodiesDict[parentIndex]
                setRelativeSV(body, parentBody, bodyDict, initTime)

            body = bodies[i]
            print(body.name + " " + str(body.hasInitSV))
            allInitialized = allInitialized and body.hasInitSV

def setBodiesSVs(bodies, bodiesDict, initTime, bodiesIndexMap):
    setAbsoluteSVs(bodies, bodiesDict, initTime)
    setRelativeSVs(bodies, bodiesDict, initTime, bodiesIndexMap)

with open("general.json") as g:
    gen = json.load(g)
g.close()

sceneFile = gen["sceneFileDir"] + "/" + gen["sceneFile"]
with open(sceneFile) as s:
    scene = json.load(s)
s.close()

numSteps = scene["numSteps"]
bodiesDict = scene["bodies"]
initTime = timeUtils.dictToDateTime(scene["initTime"])
bodies, bodiesIndexMap = initBodiesFromDict(bodiesDict)

setBodiesSVs(bodies, bodiesDict, initTime, bodiesIndexMap)

for b in bodies:
    print(b.name)
    print("Pos: ", b.pos)
    print("Vel: ", b.vel)
    print()
