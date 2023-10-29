
class Heater():
    """
     Composite object used to group together components related to heating the batteries.
    """
    @property
    def state(self) -> str:
        return "on" if self._heater_relay.relay_on else "off"
    
    @property
    def temp_C(self) -> float:
        return self._temperature_sensor.temp_C
    
    def __init__(self, heater_relay: Relay, temperature_sensor: TemperatureSensor, tags: Dict = {} ):
        self._heater_relay = heater_relay
        self._temperature_sensor = temperature_sensor
        self._tags = tags

    def activate(self) -> bool:
        return self._heater_relay.activate()
    
    def deactivate(self) -> bool:
        return self._heater_relay.deactivate()
    

