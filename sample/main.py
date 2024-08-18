import time
from network import (
    WLAN,
    STA_IF,
    STAT_GOT_IP,
    STAT_NO_AP_FOUND,
    STAT_CONNECT_FAIL,
    STAT_WRONG_PASSWORD,
)
from machine import reset

from wifi_setup import WifiConfig, WifiSetupPortal

class IoTDevice:
    def execute(self) -> None:
        try:
            if not WifiConfig().check():
                print("start wifi setup portal")
                WifiSetupPortal().execute()
            else:
                print("start iot device")
                if not self._connect_wifi():
                    raise Exception("cannot connect wifi")
                self._main_routine()
        except Exception as e:
            print(f"{e=}")
            time.sleep(1)
            reset()

    def _connect_wifi(self) -> bool:
        ssid: str
        key: str
        ssid, key = WifiConfig().get()
        wlan: WLAN = WLAN(STA_IF)
        wlan.active(True)
        wlan.connect(ssid, key)

        while True:
            time.sleep(1)
            status: int = wlan.status()
            if status == STAT_NO_AP_FOUND or status == STAT_CONNECT_FAIL:
                break
            elif status == STAT_WRONG_PASSWORD:
                print("cannot connect wifi because incorrect password so wifi_config reset")
                WifiConfig().delete()
                reset()
                break
            elif status == STAT_GOT_IP:
                return True
        return False

    def _main_routine(self) -> None:
        # Your main routine here
        print("main routine")

if __name__ == "__main__":
    IoTDevice().execute()
