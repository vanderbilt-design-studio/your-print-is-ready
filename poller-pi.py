import asyncio
import wiringpi
import websockets
import requests
from zeroconf import ServiceBrowser, Zeroconf, ZeroconfServiceTypes, ServiceInfo
from typing import Dict, List
import socket
from ultimaker import Printer
from config import server_uri, ultimaker_application_name, ultimaker_user_name, logging_format
from uuid import UUID
import json
import os
import ssl
import logging
import socket


logging.basicConfig(filename='/dev/null',
                    level=logging.INFO, format=logging_format)

x_api_key = os.environ['X_API_KEY']

printers_by_name: Dict[str, Printer] = {}


class PrinterListener:
    def remove_service(self, zeroconf, type, name):
        printers_by_name.pop(name)
        logging.info(f"Service {name} removed")

    def add_service(self, zeroconf, type, name):
        info: ServiceInfo = zeroconf.get_service_info(type, name)
        printer = Printer(socket.inet_ntoa(info.address), info.port)
        printers_by_name[name] = printer
        logging.info(
            f"Service {name} added: {info} guid:{printer.guid} status: {printer.get_printer_status()}")


zeroconf = Zeroconf()
listener = PrinterListener()
browser = ServiceBrowser(zeroconf, "_ultimaker._tcp.local.", listener)

ssl_context = ssl.create_default_context()


async def send_printer_status():
    async with websockets.connect(server_uri, ssl=ssl_context) as websocket:
        while True:
            printer_jsons: List[Dict[str, str]] = []
            printer: Printer
            for printer in list(printers_by_name.values()):
                try:
                    printer_status_json: Dict[str, str] = printer.into_ultimaker_json()
                    printer_jsons.append(printer_status_json)
                except Exception as e:
                    logging.warning(
                        f'Exception getting info for printer {printer.guid}, it may no longer exist: {e}')
                    continue
            printer_jsons_str: str = json.dumps({'printers': printer_jsons, 'key': x_api_key})
            logging.info(f'Sending {printer_jsons_str}')
            await websocket.send(printer_jsons_str)
            await asyncio.sleep(3)


try:
    while True:
        try:
            asyncio.get_event_loop().run_until_complete(send_printer_status())
        except Exception as serr:
            logging.warning(
                f"Exception while sending status to ds-server, attempting to start again: {serr}")
finally:
    zeroconf.close()
