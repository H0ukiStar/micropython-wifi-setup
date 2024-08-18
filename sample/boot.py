import time

from wifi_setup import WifiConfig

# Sample of deleting settings when some button is pressed at boot.
# For RaspberryPi Pico W
if WifiConfig().check():
    time.sleep_ms(3000)
if rp2.bootsel_button() == 1:
    WifiConfig().delete()
