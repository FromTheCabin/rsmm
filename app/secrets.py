# Micropython hack for using a .env file.
from micropython import const

WIFI_SSID = None
WIFI_PASSWORD = None

UTC_OFFSET = -6
NTP_SERVER = "time.nist.gov"

HOSTNAME = None
UTC_OFFSET = None
UPDATE_CHECK_INTERVAL_SECS = 86400

MQTT_HOST = None
MQTT_PORT = 1883
MQTT_USER = None
MQTT_PASSWORD = None

GIT_URL = None

BATTERY_MIN_VOLTAGE = const(10.0)


with open('.env', 'r') as env:
    while (line := env.readline()):
        
        if len( line.split('=')) != 2: continue
    
        key,value = (s.strip() for s in line.split('=') )
        
        # If the line contains a comment at the end, strip it off
        value = value.split("#")[0].strip().strip('"')
        
        #print( f'key: {key}, value: {value}')
        if key == "GIT_URL":
            GIT_URL = value
        elif key == "WIFI_SSID":
            WIFI_SSID = value
        elif key == "WIFI_PASSWORD":
            WIFI_PASSWORD = value
        
        elif key == "HOSTNAME":
            HOSTNAME = value
        elif key == "UTC_OFFSET":
            UTC_OFFSET = int(value)
        elif key == "NTP_SERVER":
            NTP_SERVER = value    
        elif key == "UPDATE_CHECK_INTERVAL_SECS":
            UPDATE_CHECK_INTERVAL_SECS = int(value)
            
        elif key == "MQTT_HOST":
            MQTT_HOST = value
        elif key == "MQTT_PORT":
            MQTT_PORT = value
        elif key == "MQTT_USER":
            MQTT_USER = value
        elif key == "MQTT_PASSWORD":
            MQTT_PASSWORD = value

assert GIT_URL != None
assert WIFI_SSID != None
assert WIFI_PASSWORD != None
assert HOSTNAME != None
assert UTC_OFFSET != None
assert NTP_SERVER != None
assert MQTT_HOST != None
assert MQTT_PORT != None
assert MQTT_USER != None
assert MQTT_PASSWORD != None

