import asyncio
import wiringpi
import websockets
import requests
from zeroconf import ServiceBrowser, Zeroconf, ZeroconfServiceTypes, ServiceInfo
from typing import Dict, List
import socket
from ultimaker import Printer
from config import server_uri, ultimaker_application_name, ultimaker_user_name
from uuid import UUID
import json
import os

x_api_key = os.environ['X_API_KEY']

printers: Dict[str, Printer] = {}


class PrinterListener:
    def remove_service(self, zeroconf, type, name):
        printers.pop(name)
        print("Service %s removed" % (name,))

    def add_service(self, zeroconf, type, name):
        print("Service %s added" % (name,))
        info: ServiceInfo = zeroconf.get_service_info(type, name)
        printer = Printer(socket.inet_ntoa(info.address), info.port)
        printers[name] = printer
        print(printer.guid, printer.get_printer_status())


zeroconf = Zeroconf()
listener = PrinterListener()
browser = ServiceBrowser(zeroconf, "_ultimaker._tcp.local.", listener)


async def send_printer_status():
    async with websockets.connect(server_uri) as websocket:
        while True:
            printer: Printer
            for printer in list(printers.values()):
                try:
                    printer_status_json: Dict[str, str] = printer.into_printer_status_json()
                except Exception as e:
                    print(
                        f'Exception getting info for printer {printer.guid}, it may no longer exist: {e}')
                    continue
                await websocket.send(json.dumps(printer_status_json))
                await asyncio.sleep(0.5)

try:
    asyncio.get_event_loop().run_until_complete(send_printer_status())
finally:
    zeroconf.close()
