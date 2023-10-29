import time
import network

import app.utils as utils
#import app.secrets as secrets
import app.secrets as secrets

from app.components.relay import Relay
from app.components.temperature_sensor import TemperatureSensor
from app.components.pressure_sensor import PressureTempSensor
from app.components.voltage_sensor import VoltageSensor
from app.components.heater import Heater

heater_upper = Heater( Relay(48), TemperatureSensor(37, '28bd8380e3e13dde') )
heater_lower = Heater( Relay(47), TemperatureSensor(37, '286a0980e3e13de9') )

# BMP280
air_pressure_sensor = PressureTempSensor(scl_pin_num = 14, sda_pin_num = 13 )
air_temp_sensor = air_pressure_sensor

# DS18B20
case_temp_sensor = TemperatureSensor(10, '286aa880e3e13d17')

# Voltage dividers
battery_voltage = VoltageSensor( pin_num = 12, correction_val = 21.5605 )
vp_voltage = VoltageSensor( pin_num = 17, correction_val = 1 )


def record_telemetry() -> bool:
    """
    If the wireless connection starts to work, then this will send telemetry to the
    MQTT instance on the local server. But initially it will write out the JSON data
    to local storage.
    """
    # Build telemetry message
    message = {}
    message["measurement_time_local"] = time.localtime()
    message["air_temp_c"] = air_temp_sensor.temp_C
    message["air_pressure_pa"] = air_pressure_sensor.pressure_Pa
    message["case_temp_c"] = case_temp_sensor.temp_C
    message["heater_upper"] = { "temp_c" : heater_upper.temp_C, "state": heater_upper.state }
    message["heater_lower"] = { "temp_c" : heater_lower.temp_C, "state": heater_lower.state }
    message["battery_voltage"] = battery_voltage.voltage
    message["pv_voltage"] = vp_voltage.voltage
    
    print(message)


def main() -> None:
    while True:
        # Check for updates 


        # Get case temp
        case_temp_C = case_temp_sensor.temp_C
        
        print(case_temp_C)
        
        # Turn on the battery heaters if the temperature is below the "charge temp" of
        # the LifePo4 batteries.
        if case_temp_C < 1:
            heater_upper.activate()
            heater_lower.activate()
        else:
            heater_upper.deactivate()
            heater_lower.deactivate()
        

        # Test code only
        heater_upper.deactivate()
        heater_lower.deactivate()

        
        record_telemetry()
        
        # This time will probably need to be adjusted, but every 30 seconds should be
        # good for a first pass
    
        break

    #time.sleep(30)
    

main()

