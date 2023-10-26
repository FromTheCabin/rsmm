from app.ota_updater import OTAUpdater

def connectToWifiAndUpdate():
    import time, machine, network, gc, app.secrets as secrets
    time.sleep(1)
    print('Memory free', gc.mem_free())

    from app.ota_updater import OTAUpdater

    sta_if = network.WLAN(network.STA_IF)
    
    print(f"WIFI_SSID: {secrets.WIFI_SSID}")
    print(f"WIFI_PASSWORD: {secrets.WIFI_PASSWORD}")
    
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        try:
            sta_if.connect(secrets.WIFI_SSID, secrets.WIFI_PASSWORD)
        except OSError as error:
            print(error)
        
        while not sta_if.isconnected():
            pass
        
    print('network config:', sta_if.ifconfig())
    otaUpdater = OTAUpdater('https://github.com/FromTheCabin/rsmm.git', main_dir='app', secrets_file="secrets.py")
    hasUpdated = otaUpdater.install_update_if_available()
    print('here')
    if hasUpdated:
        machine.reset()
    else:
        del(otaUpdater)
        gc.collect()

def startApp():
    """
    
    Simple entrypoint for the app
    
    """
    import app.start


connectToWifiAndUpdate()
startApp()



