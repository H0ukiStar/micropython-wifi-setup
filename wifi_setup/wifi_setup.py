import os
import gc
import json
import machine
from asyncio import (
    run,
    Loop,
    sleep_ms,
    StreamReader,
    StreamWriter,
    start_server,
    get_event_loop,
)
from network import WLAN, AP_IF
from socket import socket, AF_INET, SOCK_DGRAM


class WifiConfig:
    WIFI_CONFIG_PATH: str = "/wifi_config.json"

    def get(self) -> tuple[str, str]:
        with open(self.WIFI_CONFIG_PATH, "r") as f:
            wifi_config: dict = json.load(f)
        return wifi_config["ssid"], wifi_config["key"]

    def check(self) -> bool:
        try:
            os.stat(self.WIFI_CONFIG_PATH)
            _ = self.get()
            return True
        except:
            return False

    def save(self, ssid: str, key: str) -> None:
        with open(self.WIFI_CONFIG_PATH, "w") as f:
            json.dump({
                "ssid": ssid,
                "key": key
            }, f)

    def delete(self) -> None:
        try:
            os.remove(self.WIFI_CONFIG_PATH)
        except:
            pass

class WifiSetupPortal:
    SERVER_IP: str = "192.168.4.1"
    SERVER_SUBNET: str = "255.255.255.0"

    def __init__(self, ssid: str = "", key: str = "", domain: str = "") -> None:
        self._ssid: str = ssid if ssid else "IoTDeviceSetUp"
        self._key: str = key
        self._domain: str = domain if domain else "iotdevice.setup"
        self._web_directory: str = "/".join(__file__.split("/")[:-1]) + "/web"

    def execute(self) -> None:
        self._start_access_point()
        run(self._start_captive_portal())

    def _start_access_point(self) -> None:
        ap: WLAN = WLAN(AP_IF)
        ap.ifconfig((
            self.SERVER_IP,
            self.SERVER_SUBNET,
            self.SERVER_IP,
            self.SERVER_IP
        ))
        if self._key:
            ap.config(ssid=self._ssid, key=self._key)
        else:
            ap.config(ssid=self._ssid, security=0)
        ap.active(True)

    async def _start_captive_portal(self):  # -> Coroutine
        loop: Loop = get_event_loop()
        loop.create_task(self._run_http_server())
        loop.create_task(self._run_dns_server())
        loop.run_forever()

    async def _handle_http_connection(self, reader: StreamReader, writer: StreamWriter):  # -> Coroutine
        def make_http_response(code: int, body: str = "", redirect: str = "") -> str:
            response: str = "HTTP/1.1 "
            statuscodes: dict = {
                200: "200 OK",
                302: "302 Found",
                500: "500 Internal Server Error"
            }
            response += f"{statuscodes[code]}\r\n"
            if code == 302:
                response += f"Location: {redirect}\r\n"
            response += "\r\n"
            if body:
                response += body
            return response

        gc.collect()
        response: str
        try:
            data: bytes = await reader.readline()
            request_line: str = data.decode().strip()
            method: str
            path: str
            version: str
            method, path, version = request_line.split()

            headers: dict = {}
            while True:
                header_line: bytes = await reader.readline()
                if header_line == b"\r\n":
                    break
                field: str
                value: str
                field, value = header_line.decode().split(":", 1)
                headers[field.strip()] = value.strip()
            host: str = headers["Host"]

            body: bytes = b""
            if (content_length := int(headers.get("Content-Length", 0))) > 0:
                body = await reader.read(content_length)

            # addr: tuple[str, int] = writer.get_extra_info("peername")
            # print(f"http request info:\n{method=}, {path=}, {version=}, {host=}, src_addr={addr[0]}")

            if method == "GET" and path == "/" and self._domain == host:
                with open(self._web_directory + "/index.html") as f:
                    response = make_http_response(200, body=f.read())
            elif method == "GET" and path == "/style.css" and self._domain == host:
                with open(self._web_directory + "/style.css") as f:
                    response = make_http_response(200, body=f.read())
            elif method == "POST" and path == "/wifi" and self._domain == host:
                params: list[str] = body.decode().split("&")
                ssid: str = [param for param in params if "ssid" in param][0].split("=")[1]
                key: str = [param for param in params if "key" in param][0].split("=")[1]
                WifiConfig().save(ssid, key)
                with open(self._web_directory + "/success.html") as f:
                    response = make_http_response(200, body=f.read())
            else:
                response = make_http_response(302, redirect=f"http://{self._domain}/")
        except Exception as e:
            print(f"{e=}")
            with open(self._web_directory + "/error.html") as f:
                response = make_http_response(500, body=f.read())

        await writer.awrite(response)
        await writer.aclose()

        if WifiConfig().check():
            await sleep_ms(5000)
            machine.reset()

    def _run_http_server(self):  # -> Coroutine
        return start_server(self._handle_http_connection, "0.0.0.0", 80)

    async def _run_dns_server(self):  # -> Coroutine
        def make_dns_response(data: bytes) -> bytes:
            packet: bytes = data[:2] + b"\x81\x80"
            packet += data[4:6] + data[4:6] + b"\x00\x00\x00\x00"  # Questions and Answers Counts
            packet += data[12:]  # Original Domain Name Question
            packet += b"\xC0\x0C"  # Pointer to domain name
            packet += b"\x00\x01\x00\x01\x00\x00\x00\x3C\x00\x04"  # Response type, ttl and resource data length -> 4 bytes
            packet += bytes(map(int, self.SERVER_IP.split(".")))  # 4bytes of IP
            return packet

        s: socket = socket(AF_INET, SOCK_DGRAM)
        s.setblocking(False)
        s.bind(("0.0.0.0", 53))

        while True:
            gc.collect()
            try:
                data: bytes
                addr: tuple[str, int]
                data, addr = s.recvfrom(4096)
                s.sendto(make_dns_response(data), addr)
            except:
                await sleep_ms(100)

        s.close()
