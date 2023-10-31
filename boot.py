import os
import esp
import machine

esp.osdebug(None)
machine.freq(240000000)


"""
if not os.path.isfile('observer.ini'):
    print('observer.ini does not exist! Entering AP mode')
else:
    print('observer.ini exists! Entering client mode' )
"""


