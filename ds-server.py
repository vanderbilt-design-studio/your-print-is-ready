import asyncio
import pathlib
import ssl
import websockets
import json
import http
import logging
import secrets
from typing import Set, List
import os
from config import logging_format

logging.basicConfig(filename=os.environ['HOME'] + '/poller-pi.log',
                    level=logging.INFO, format=logging_format)

x_api_key = os.environ['X_API_KEY']

# Last-value caching of the poller pi response
printer_jsons = []

poller_pi = None

clients: Set[websockets.WebSocketServerProtocol] = set()


def state_json() -> str:
    return json.dumps(printer_jsons)


async def notify_of_state_change():
    if len(clients) > 0:
        message = state_json()
        await asyncio.wait([client.send(message) for client in clients])


async def register_client(websocket: websockets.WebSocketServerProtocol):
    clients.add(websocket)
    logging.info(
        f'Client {websocket.remote_address[0]}:{websocket.remote_address[1]} joined')
    await websocket.send(state_json())


async def unregister_client(websocket: websockets.WebSocketServerProtocol):
    logging.info(
        f'Client {websocket.remote_address[0]}:{websocket.remote_address[1]} left')
    clients.remove(websocket)


async def reclassify_client_as_poller(websocket: websockets.WebSocketServerProtocol):
    if websocket in clients:
        logging.info(
            f'Client {websocket.remote_address[0]}:{websocket.remote_address[1]} is actually a poller, removing from clients list')
        clients.remove(websocket)


async def event_loop(websocket: websockets.WebSocketServerProtocol, path):
    global printer_jsons
    await register_client(websocket)
    try:
        # This forces the server to keep the connection alive until the client leaves, and for the poller, it can send messages
        async for message in websocket:
            message_json = json.loads(message)
            if message_json['key'] and secrets.compare_digest(message_json['key'], x_api_key):
                new_printer_jsons = message_json['printers']
                if new_printer_jsons != printer_jsons:
                    logging.info(
                        f'Poller at {websocket.remote_address[0]}:{websocket.remote_address[1]} sent new json {new_printer_jsons}')
                    printer_jsons = new_printer_jsons
                    await notify_of_state_change()
            continue
    finally:
        await unregister_client(websocket)


ssl_context: ssl.SSLContext = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain(pathlib.Path(
    '/etc/letsencrypt/live/iot.vanderbilt.design/fullchain.pem'),
    keyfile=pathlib.Path('/etc/letsencrypt/live/iot.vanderbilt.design/privkey.pem'))

asyncio.get_event_loop().run_until_complete(
    websockets.serve(event_loop, '0.0.0.0', 443, ssl=ssl_context))
asyncio.get_event_loop().run_forever()
