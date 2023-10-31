from machine import Pin, ADC, SoftI2C

from ..lib.bmp280 import *

class PressureTempSensor:
    """
    BMP-280 helper class
    """
    @property
    def temp_C(self) -> float:
        return round(self._bmp.temperature,2)

    @property
    def pressure_Pa(self) -> float:
        return self._bmp.pressure

    @property
    def pressure_inches_Hg(self) -> float:
        # inch Hg == 3386.39 Pascal
        return self._bmp.pressure / 3386.39
    
    def pressure_inches_mb(self) -> float:
        # millibar == 100 Pascal 
        return self._bmp.pressure / 100

    def __init__(self, scl_pin_num: int, sda_pin_num: int ):
        bus = SoftI2C(scl= Pin(scl_pin_num),sda=Pin(sda_pin_num))
        self._bmp = BMP280(bus)
        
        self._bmp.use_case(BMP280_CASE_WEATHER)
        self._bmp.oversample(BMP280_OS_HIGH)
        
        self._bmp.temp_os = BMP280_TEMP_OS_8
        self._bmp.press_os = BMP280_PRES_OS_4
        
        self._bmp.standby = BMP280_STANDBY_250
        self._bmp.iir = BMP280_IIR_FILTER_2
        
        self._bmp.spi3w = BMP280_SPI3W_OFF
        
        self._bmp.power_mode = BMP280_POWER_SLEEP

    def take_measurement(self) -> tuple:
        return ( self.temp_C, self.pressure_Pa )

