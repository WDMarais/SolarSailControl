#!/bin/bash
python3 physicsTest.py
blender textLoad.blend -P coordsToScene.py
