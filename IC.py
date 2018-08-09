import numpy as np
from spaceBodies import spaceBody

dimensions = 3
from scipy.constants import G # Newton's gravitational constant
from scipy.constants import au

def basicScene():
    name = 'Sun'
    mass = 1.98892 * 10 ** 30
    position = np.zeros(dimensions)
    velocity = np.zeros(dimensions)
    diameter = 0.2
    color = (1.0, 1.0, 0.0)
    Sun = spaceBody(name, mass, position, velocity, diameter, color)

    name = 'Venus'
    mass = 4.8685 * 10 ** 24
    position = np.array([0.723 * au, 0.0, 0.0])
    velocity = np.array([0.0, -35.02 * 1000, 0.0])
    diameter = 0.1
    color = (1.0, 0.15, 0.0)
    Venus = spaceBody(name, mass, position, velocity, diameter, color)

    name = 'Earth'
    mass = 10.0
    position = np.array([-1 * au, 0.0, 0.0])
    velocity = np.array([0, 29.783 * 1000, 0])
    diameter = 0.1
    color = (0.0, 0.0, 1.0)
    Earth = spaceBody(name, mass, position, velocity, diameter, color)

    bodies = [Sun, Venus, Earth]
    return bodies
