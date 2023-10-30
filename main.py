import gc
import machine

from app.lib.ota_updater import OTAUpdater

import app.utils as utils
from app.utils import YELLOW, GREEN
import app.secrets as secrets


def download_and_install_update_if_available():
        
    o = OTAUpdater(secrets.GIT_URL, main_dir='app', secrets_file="secrets.py")
    
    # Check for new version.
    # Connection resets occur in this environment, so try a few times to
    # download and install any new versions.
    
    try_count = 1
    while try_count <= 5:
        try:
            if o.install_update_if_available():
                machine.reset()
            else:
                break
        except OSError as err:
            try_count += 1
            print(f"OSERROR: {err}")
            utils.flash_rgb( try_count, RED, 200 )
    
        try_count += 1

def initialize():
    utils.flash_rgb(3, GREEN, 200)
                    
    # Connect to wifi and start the app
    utils.connect_to_wifi()
    
    # Attempt to sync the RTC with the NTP server.
    # If successful, adjust the system's localtime with
    # the provided UTC offset.
    if utils.sync_time_with_ntp():
        utils.apply_utc_offset_to_rtc(secrets.UTC_OFFSET)
    
    # Record the boot time after syncing the time
    utils.record_boot_time()

    # Check for updates
    download_and_install_update_if_available()


def start_app():
    """
    
    Simple entrypoint for the app
    
    """
    
    import app.start


initialize()
start_app()



