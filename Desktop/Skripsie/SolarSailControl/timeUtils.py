import datetime

def sec2Cent(seconds):
    return seconds / (60 * 60 * 24 * 365.25 * 100)

def centuriesSinceJ2000(givenDateTime):
    J2000 = datetime.datetime(2000, 1, 1, 12, 0, 0)
    deltaSeconds = (givenDateTime - J2000)
    deltaCenturies = sec2Cent(deltaSeconds)
    return deltaCenturies

def dictToDateTime(timeDict):
    y = timeDict["year"]
    m = timeDict["month"]
    d = timeDict["day"]
    h = timeDict["hour"]
    mi = timeDict["minute"]
    s = timeDict["second"]
    us = timeDict["microsecond"]
    return datetime.datetime(y, m, d, h, mi, s, us)
