from IC import keplerian2
from datetime import datetime

myDate = datetime.now()
bodies, scaleFactor = keplerian2(myDate)

for b in bodies:
    b.cartesianToConsole()
