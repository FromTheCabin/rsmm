import time
import ntptime
import network
import machine
import neopixel
   
import app.secrets as secrets

def download_and_install_update_if_available():
    from lib.ota_updater import OTAUpdater
        
    o = OTAUpdater(secrets.GIT_URL)
    o.install_update_if_available_after_boot(secrets.WIFI_SSID, secrets.WIFI_PASSWORD)

def format_time( datetimetuple ) -> str:
    return f"{datetimetuple[3]}:{datetimetuple[4]:02}:{datetimetuple[5]:02}"
    
def format_date( datetimetuple ) -> str:
    return f"{datetimetuple[0]}-{datetimetuple[1]:02}-{datetimetuple[3]:02}"

def format_datetimetuple( datetimetuple ) -> str:
    return f"{format_date(datetimetuple)} {format_time(datetimetuple)}"

def connect_to_wifi() -> None:
    # Set the hostname for easier identification on the router.
    network.hostname(secrets.HOSTNAME)
    
    wlan = network.WLAN(network.STA_IF)

    if wlan.isconnected():
        print("Disconnect called")
        wlan.disconnect()

    if not wlan.active():
        print("Activating WiFi")
        wlan.active(True)

    # Grab a list of available ssids
    ssids = [ssid.decode() for ssid, _, _, _, _, _ in wlan.scan() if len(ssid) > 0 ]
    
    if secrets.WIFI_SSID in ssids:
        print('WIFI_SSID found!')
        wlan.connect(secrets.WIFI_SSID, secrets.WIFI_PASSWORD)
        while not wlan.isconnected():
            machine.idle() # save power while waiting
        print('WLAN connection succeeded!')        
    else:
        print(f"{secrets.WIFI_SSID} not found!")
        print("SSIDs available:")
        print(ssids)

def disconnect_from_wifi():
    wlan = network.WLAN(network.STA_IF)
    
    if wlan.isconnected():
        wlan.disconnect()
        wlan.active(False)
    

def flash_rgb( count: int = 3, color = (50,0,0) ) -> None:
    pixels = neopixel.NeoPixel(Pin(48),1)
    
    for i in range(0,count):
        pixels.fill( color )
        pixels.write()
        time.sleep_ms(500)
        pixels.fill( (0,0,0) )
        pixels.write()
        time.sleep_ms(500)
    
def log_message( message: str, severity: str = 'INFO' ) -> None:
    try:
        now = time.localtime()
        
        message = f"{now[0]:02}/{now[1]:02}/{now[2]:02} {now[3]:02}:{now[4]:02}:{now[5]:02}.{now[6]:02} | {message} | {severity}\n"
        print(message)
    
        with open('errors.log', 'a') as outfile:
            outfile.write( message )
    except Exception as e:
        print(e)

    
def apply_utc_offset_to_rtc(utc_offset: int = 0 ):
    """
    Adjust time.localtime from UTC to actual local time.
    """

    rtc = machine.RTC()
    
    orig_time = time.localtime()
    
    # Add the UTC offset 
    time_with_offset = int( time.time() + (utc_offset * 60 * 60) )

    year, month, day, hour, minute, second, weekday, _ = time.localtime(time_with_offset)
    
    rtc.datetime((year, month, day, weekday, hour, minute, second, 0 ) )

    orig_time = format_datetimetuple(orig_time)
    current_time = format_datetimetuple(time.localtime())
    
    if orig_time != current_time:
        print(f"RTC time updated from {orig_time} to {current_time}")

def sync_time_with_ntp(retries: int = 5) -> bool:
    """
    Utility function to sync the localtime with the NTP server output.
    """
    
    sync_successful = False
    
    ntptime.host = secrets.NTP_SERVER
    retry = 0
    
    # Update the RTC with the NTP output. If the call fails, wait 5 seconds and try again
    while (retry := retry + 1 ) <= retries:
        try:
            # Set the local time
            ntptime.settime()
            
            sync_successful = True
            break
        except OSError as err:
            print(f"NTP called failed: {err}. Retry {retry} of {retries}...")
        
        time.sleep(5)
        
    if sync_successful:
        print('Local time sync with NTP successful.')
    else:
        print( f'NTP call failed after {retries} retries. Using existing local time.')
    
    return sync_successful


