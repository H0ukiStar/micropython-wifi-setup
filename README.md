# micropython-wifi-setup
A MicroPython library that implements a captive portal, allowing devices to configure the SSID and password needed to connect to an access point (AP).

I checked the works in the following environment:
- Micropython v1.23.0
- RaspberryPi Pico W

## Installation

Copy the `wifi_setup` folder into the `/lib` directory on your MicroPython device.

## Usage

- **To configure Wi-Fi:**
  Call `WifiSetupPortal().execute()` to set up the Wi-Fi.

- **To retrieve Wi-Fi configuration details:**
  Use `WifiConfig().get()` to obtain the SSID and Key.

main.py and boot.py sample is here: [sample](https://github.com/H0ukiStar/micropython-wifi-setup/tree/main/sample)

## Notes

- Author: H0ukiStar
- License: [MIT](https://github.com/H0ukiStar/micropython-wifi-setup/blob/main/LICENSE)
- Repository: [micropython-wifi-setup](https://github.com/H0ukiStar/micropython-wifi-setup)

## References

Captive Portal was implemented with reference to:
[micropython-captiveportal](https://github.com/metachris/micropython-captiveportal)
