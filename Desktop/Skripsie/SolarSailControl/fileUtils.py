import os

def createDir(newDirectory):
    if not os.path.exists(os.path.dirname(newDirectory)):
    	try:
            os.makedirs(os.path.dirname(newDirectory), exist_ok=True)
    	except OSError as exc:
    		raise

def createDirs(spaceBodies, subDir = None):
    for s in spaceBodies:
        dirPath = ""
        if not (subDir == None):
            dirPath += (subDir + "/")
        dirPath += (s.name + "/")
        createDir(dirPath)
