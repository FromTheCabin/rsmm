"""
Helper class for interacting with relays
"""

from machine import Pin

class Relay:
    """
     Helper class for a standard relay
    """
    @property
    def state(self) -> str:
        return "on" if not self.energized and not self._normally_open else "off"
        
    @property
    def energized(self):
        return self._pin.value() == self._activate_is_high
    
    def __init__(self, pin_num: pin_num, normally_open: bool = True ):
        self._pin = Pin(pin_num, Pin.OUT)
        self._activate_is_high = True
        self._normally_open = normally_open
        
    def activate(self):
        #self._pin.value(self._activate_is_high)
        self._pin.on()
    
    def deactivate(self):
        #self._pin.value(not self._activate_is_high)
        self._pin.off()
    
    def __repr__(self):
 
        return f'Relay(pin={self._pin}, relay_on={self.relay_on})'
    
    def __str__(self):
        return __repr__()

