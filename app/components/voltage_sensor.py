"""
Helper class for interacting with voltage sensors.
At the moment this means voltage dividers, but will include other
mechanisms in the future.
"""

from machine import Pin, ADC

class VoltageSensor():
    @property
    def voltage(self) -> float:
        return self.__get_voltage()
    

    def __init__(self, pin_num: int, correction_val: float ):
        self._adc = ADC(Pin(pin_num))
        #self._adc.atten(ADC.ATTN_11DB)
        self._adc.width(ADC.WIDTH_12BIT)
        
        self._correction_val = correction_val
        
    def __get_voltage(self) -> float:
        return round((self._adc.read_u16() / 65_535) * self._correction_val, 2)


