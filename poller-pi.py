import asyncio
import wiringpi
import websockets
import requests
from zeroconf import ServiceBrowser, Zeroconf, ZeroconfServiceTypes, ServiceInfo
from typing import Dict, List
import socket
from ultimaker import Serial, Printer
from config import server_uri, ultimaker_application_name, ultimaker_user_name
import unittest
import unittest.mock

printers: Dict[Serial, Printer] = {}


class PrinterListener:
    def remove_service(self, zeroconf, type, name):
        info: ServiceInfo = zeroconf.get_service_info(type, name)
        printers.pop(Serial(info.name))
        print("Service %s removed" % (name,))

    def add_service(self, zeroconf, type, name):
        print("Service %s added" % (name,))
        info: ServiceInfo = zeroconf.get_service_info(type, name)
        serial = Serial(info)
        printer = Printer(info.properties[b'name'], socket.inet_ntoa(
            info.address), info.port)
        printers[serial] = printer
        # printer.acquire_authorization()


zeroconf = Zeroconf()
listener = PrinterListener()
browser = ServiceBrowser(zeroconf, "_printer._tcp.local.", listener)


async def send_printer_status():
    async with websockets.connect(server_uri) as websocket:
        while True:
            await websocket.send("Hello world!")

try:
    # asyncio.get_event_loop().run_until_complete(send_printer_status())
    input("Press enter to exit...\n\n")
finally:
    zeroconf.close()