"""
Helper class to wrap different kinds of temperature sensors
"""
from machine import Pin
import binascii
import onewire
import ds18x20

class TemperatureSensor:
    @property
    def temp_C(self) -> float:
        return self.__get_temp_c()
    
    @property
    def temp_F(self) -> float:
        return round( ((self.__get_temp_c() * 9/5) + 32.0 ),2)
    
    def __init__(self, pin_num: int, ic2_addr: str ):
        self._pin = Pin(pin_num, Pin.IN )
        self._i2c_addr = ic2_addr
        
        self._ds_sensor = ds18x20.DS18X20(onewire.OneWire(self._pin))

        # Request the rom variables
        roms = self._ds_sensor.scan()

        # Search for the sensor by address
        for rom in roms:
            # print(binascii.hexlify(rom).decode())
            if binascii.hexlify(rom).decode() == self._i2c_addr:
                self._rom = rom
                break
            
        #print('Found DS devices: ', roms)
            
    def __get_temp_c(self) -> float:
        self._ds_sensor.convert_temp()
        return round(self._ds_sensor.read_temp(self._rom), 2)
