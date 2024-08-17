# micropython-wifi-setup
A MicroPython library that implements a captive portal, allowing devices to configure the SSID and password needed to connect to an access point (AP).

## Installation

Copy the `wifi_setup` folder into the `/lib` directory on your MicroPython device.

## Usage

- **To configure Wi-Fi:**
  Call `WifiSetupPortal().execute()` to set up the Wi-Fi.

- **To retrieve Wi-Fi configuration details:**
  Use `WifiConfig().get()` to obtain the SSID and Key.
