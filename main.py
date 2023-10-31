import gc
import machine

from app.lib.ota_updater import OTAUpdater

import app.utils as utils
import app.secrets as secrets


def download_and_install_update_if_available():
        
    o = OTAUpdater(secrets.GIT_URL, main_dir='app', secrets_file="secrets.py")
    
    # Check for new version.
    # Connection resets occur in this environment, so try a few times to
    # download and install any new versions.
    
    try_count = 1
    while try_count <= 5:
        try:
            print('Running install_update_if_available()')
            if o.install_update_if_available():
                utils.flash_rgb( 1, utils.BLUE, 500 )
                utils.flash_rgb( 1, utils.YELLOW, 500 )
                utils.flash_rgb( 1, utils.BLUE, 500 )
                
                machine.reset()
            else:
                break
        except OSError as err:
            try_count += 1
            print(f"OSERROR: install_update_if_available() {err}")
            utils.flash_rgb( try_count, utils.RED, 200 )
    
        try_count += 1

    

def initialize():
                    
    # Connect to wifi and start the app
    connected = utils.connect_to_wifi()

    print( f'Wifi connected: {connected}')

    # Put the system into deep sleep for 1 minute before restarting
    # and trying again.
    if not connected:
        print('Sleeping')
        machine.sleep( 30 )
        machine.reset()

    
    # Attempt to sync the RTC with the NTP server.
    # If successful, adjust the system's localtime with
    # the provided UTC offset.
    
    if utils.sync_time_with_ntp():
        utils.apply_utc_offset_to_rtc(secrets.UTC_OFFSET)
    
    # Record the boot time after syncing the time
    utils.record_boot_time()

    # Check for updates
    download_and_install_update_if_available()
    
    gc.collect()

def start_app():
    """
    
    Entrypoint for the app
    
    """

    utils.flash_rgb(3, utils.GREEN)

    import app.start


utils.flash_rgb( 1, utils.PURPLE )
utils.flash_rgb( 1, (50,50,50) )
utils.flash_rgb( 1, utils.PURPLE )

initialize()

start_app()

