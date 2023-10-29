import gc
import app.utils as utils
import app.secrets as secrets
#import app.config = config

from app.lib.ota_updater import OTAUpdater

def download_and_install_update_if_available():
        
    o = OTAUpdater(secrets.GIT_URL, main_dir='app', secrets_file="secrets.py")
    o.check_for_update_to_install_during_next_reboot()
    #o.download_install_update_if_available_after_boot(secrets.WIFI_SSID, secrets.WIFI_PASSWORD)


def initialize():
    # Connect to wifi and start the app
    utils.connect_to_wifi()

    # Check for updates
    download_and_install_update_if_available()

    # Attempt to sync the RTC with the NTP server.
    # If successful, adjust the system's localtime with
    # the provided UTC offset.
    if utils.sync_time_with_ntp():
        utils.apply_utc_offset_to_rtc(secrets.UTC_OFFSET)

    
def start_app():
    """
    
    Simple entrypoint for the app
    
    """
    
    import app.start


initialize()
start_app()

