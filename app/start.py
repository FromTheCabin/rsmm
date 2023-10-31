import gc
import time
import machine
import esp

import app.utils as utils
import app.secrets as secrets

from umqtt.robust import MQTTClient

from app.components.relay import Relay
from app.components.temperature_sensor import TemperatureSensor
from app.components.pressure_sensor import PressureTempSensor
from app.components.voltage_sensor import VoltageSensor
from app.components.heater import Heater

reset_requested = False

heater_upper = Heater( relay_pin = 48, i2c_pin = 37, i2c_addr = '28bd8380e3e13dde' )
heater_lower = Heater( relay_pin = 47, i2c_pin = 37, i2c_addr = '286a0980e3e13de9' )

usb_power = Relay( pin_num = 1, normally_open = False ) 

# BMP280
outside = PressureTempSensor(scl_pin_num = 14, sda_pin_num = 13 )

# DS18B20
case = TemperatureSensor( i2c_pin = 10, i2c_addr = '286aa880e3e13d17' )

# Voltage dividers
battery = VoltageSensor( pin_num = 12, correction_val = 21.1 )
solar = VoltageSensor( pin_num = 17, correction_val = 1 )

mqtt_client = MQTTClient( client_id = secrets.HOSTNAME,
                          server = secrets.MQTT_HOST,
                          port = secrets.MQTT_PORT,
                          user = secrets.MQTT_USER,
                          password = secrets.MQTT_PASSWORD,
                          keepalive = 60
                        )

MQTT_TOPICS = {'app_version': bytes(f"telemetry/{secrets.HOSTNAME}/app_version", 'utf-8'),
               'mem_free': bytes(f"telemetry/{secrets.HOSTNAME}/mcu/mem_free", 'utf-8'),
               'flash_size' : bytes(f"telemetry/{secrets.HOSTNAME}/mcu/flash_size", 'utf-8'),
               'mcu_freq': bytes(f"telemetry/{secrets.HOSTNAME}/mcu/freq", 'utf-8'),
               'last_boot': bytes(f"telemetry/{secrets.HOSTNAME}/mcu/last_boot", 'utf-8'),
               'battery_volt'		: bytes(f"telemetry/{secrets.HOSTNAME}/battery/voltage", 'utf-8'),
               'solar_volt'			: bytes(f"telemetry/{secrets.HOSTNAME}/battery/voltage", 'utf-8'),
               'case_temp_c'		: bytes(f"telemetry/{secrets.HOSTNAME}/case/temp_c", 'utf-8'),
               'outside_temp_c'		: bytes(f"telemetry/{secrets.HOSTNAME}/outside/air/temp_c", 'utf-8'),
               'outside_pressure_pa': bytes(f"telemetry/{secrets.HOSTNAME}/outside/air/pressure_pa", 'utf-8'),
               'heater_upper_temp_c': bytes(f"telemetry/{secrets.HOSTNAME}/heater_upper/temp_c", 'utf-8'),
               'heater_upperr_state': bytes(f"telemetry/{secrets.HOSTNAME}/heater_upper/state", 'utf-8'),
               'heater_lower_temp_c': bytes(f"telemetry/{secrets.HOSTNAME}/heater_lower/temp_c", 'utf-8'),
               'heat_lower_state'	: bytes(f"telemetry/{secrets.HOSTNAME}/heater_lower/state", 'utf-8'),
               }

MQTT_SUBS = {'reset': bytes(f"actions/{secrets.HOSTNAME}/reset", 'utf-8'),
             'usb_power': bytes(f"actions/{secrets.HOSTNAME}/usb_power", 'utf-8')
            }

def mqtt_connect( client: MQTTClient, try_count: int = 5 ) -> bool:
    connected = False
    for i in range(0, try_count):
        try:
            mqtt_client.connect()
            utils.flash_rgb( 1, utils.GREEN, 200 )
            connected = True
            break
        except OSError as err:
            print(f"OSERROR: {err}")
            utils.flash_rgb( try_count, utils.RED, 200 )

    return connected

def mqtt_disconnect( client: MQTTClient ) -> bool:
    try:
        mqtt_client.disconnect()
    except OSError as err:
        print(f"OSERROR: {err}")

def mqtt_callback( topic: bytes, message: bytes ) -> None:
    global reset_requested
    
    print(f"topic: {topic}, message: {message}")
    
    if topic == MQTT_SUBS['reset'] and message == b"1":
        print("-----------> Reset requested")
        reset_requested = True

    if topic == MQTT_SUBS['usb_power'] and message == b"bounce":
        print("-----------> USB Power")
        usb_power.activate()
        time.sleep(2)
        usb_power.deactivate()

def mqtt_setup_subscriptions( client: MQTTClient, subscriptions: dict ) -> None:
    try:
        
        for sub in subscriptions.values():
            print(f"Sub Added: {sub}")
            
            mqtt_client.subscribe(sub, qos=0)
        
    except Exception as err:
        print(f"Exception: {err}")

def main() -> None:
    global reset_requested
    
    mqtt_client.set_callback( mqtt_callback )
    mqtt_connect( mqtt_client )
    time.sleep(.1)
    mqtt_setup_subscriptions( mqtt_client, MQTT_SUBS )
    
    # Capture initial telemetry
    mqtt_client.publish( MQTT_TOPICS['app_version'], utils.app_version() )
    mqtt_client.publish( MQTT_TOPICS['mem_free'], str(gc.mem_free()) )
    mqtt_client.publish( MQTT_TOPICS['last_boot'], utils.last_boot_time() )
    mqtt_client.publish( MQTT_TOPICS['flash_size'], str(esp.flash_size()) )
    mqtt_client.publish( MQTT_TOPICS['mcu_freq'], str(machine.freq()) )
    
    bv_prev = None
    sv_prev = None
    ct_prev = None
    at_prev = None
    ap_prev = None
    hu_s_prev = None
    hu_t_prev = None
    hl_s_prev = None
    hl_t_prev = None
    
    # Calling the time.time() call repeatedly, in a short timeframe, is causing some issues.
    # This will server a similar purpose.
    loop_cnt = 30
    
    while True:
        
        mqtt_client.check_msg()
        
        if reset_requested:
            print("Reset request")
            break
        
        try:
            # Capture telemetry data every 30 seconds
            if loop_cnt == 30:
                
                #print(f"Telemetry {utils.format_datetimetuple(time.localtime())}")
                utils.flash_rgb(1, utils.PURPLE, 200)
            
                #bv = battery.voltage
                bv = battery.voltage
                if bv_prev != bv:
                    bv_prev = bv
                    mqtt_client.publish( MQTT_TOPICS['battery_volt'], str(bv)  )
                    
                sv = solar.voltage
                if sv_prev != sv:
                    sv_prev = sv
                    mqtt_client.publish( MQTT_TOPICS['solar_volt'], str(sv)  )
                    
                ct = case.temp_C
                if ct_prev != ct:
                    ct_prev = ct
                    mqtt_client.publish( MQTT_TOPICS['case_temp_c'], str(ct)  )
        
                at, ap = outside.take_measurement()
                
                if at_prev != at:
                    at_prev = at
                    mqtt_client.publish( MQTT_TOPICS['outside_temp_c'], str(at)  )
                
                if ap_prev != ap:
                    at_prev = ap
                    mqtt_client.publish( MQTT_TOPICS['outside_pressure_pa'], str(ap)  )
        
                hu_t = heater_upper.temp_C
                if hu_t_prev != hu_t:
                    hu_t_prev = hu_t
                    mqtt_client.publish( MQTT_TOPICS['heater_upper_temp_c'], str(hu_t) )
                    
                hu_s = heater_upper.state
                if hu_s_prev != hu_s:
                    hu_s_prev = hu_s
                    mqtt_client.publish( MQTT_TOPICS['heater_upperr_state'], str(hu_s) )
                
                hl_t = heater_lower.temp_C
                if hl_t_prev != hl_t:
                    hl_t_prev = hl_t
                    mqtt_client.publish( MQTT_TOPICS['heater_lower_temp_c'], str(hl_t) )
                    
                hl_s = heater_lower.state
                if hl_s_prev != hl_s:
                    hl_s_prev = hl_s
                    mqtt_client.publish( MQTT_TOPICS['heat_lower_state'], str(hl_s) )
            
                mqtt_client.publish( MQTT_TOPICS['mem_free'], str(gc.mem_free()) )
                
                gc.collect()
                
                time.sleep_ms(200)
                
        except Exception as err:
            print(f'Exception: telemetry loop() - {err}')
        
        # Reset the loop
        loop_cnt = loop_cnt - 1
        
        if loop_cnt == 0:            
            loop_cnt = 30
        
        time.sleep_ms(500)
    
    mqtt_disconnect( mqtt_client )
    
    # Reset so that the OTA process can check for updates.
    utils.flash_rgb( 10, utils.PURPLE, 200 )
    
    machine.reset()


main()


