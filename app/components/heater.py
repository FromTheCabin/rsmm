from .relay import Relay
from .temperature_sensor import TemperatureSensor


class Heater():
    """
     Composite object used to group together components related to heating the batteries.
    """
    @property
    def state(self) -> str:
        return self._heater_relay.state
    
    @property
    def temp_C(self) -> float:
        return self._temperature_sensor.temp_C
    
    @property
    def max_temp_C(self) -> float:
        return self._max_temp_C
    
    def __init__(self, relay_pin: int, i2c_pin: int, i2c_addr: str, max_temp_C: int = 60, tags: Dict = {} ):
        self._heater_relay = Relay(pin_num = relay_pin)
        self._temperature_sensor = TemperatureSensor( i2c_pin = i2c_pin, i2c_addr = i2c_addr )
        self._max_temp_C = max_temp_C
        self._tags = tags

    def activate(self) -> bool:
        
        if self.temp_C < self.max_temp_C:
            return self._heater_relay.activate()
        
        self.deactivate()
        return False
    
    def deactivate(self) -> bool:
        return self._heater_relay.deactivate()
    



