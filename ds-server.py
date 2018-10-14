import asyncio
import pathlib
import ssl
import websockets
import json
import http
import logging
import secrets
from typing import Set
import os

logging.basicConfig(filename='/var/log/ds-server.log')

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
    logging.info(f'Client {websocket.remote_address.host}:{websocket.remote_address.port} joined')
    await websocket.send(state_json())


async def unregister_client(websocket: websockets.WebSocketServerProtocol):
    logging.info(f'Client {websocket.remote_address.host}:{websocket.remote_address.port} left')
    clients.remove(websocket)


async def event_loop(websocket: websockets.WebSocketServerProtocol, path):
    # The first message should just be the API key if it's a poller, otherwise the word client.
    message = await websocket.recv()
    if secrets.compare_digest(message, x_api_key):
        poller_pi = websocket
        try:
            async for message in websocket:
                new_printer_jsons = json.loads(message)
                if new_printer_jsons != printer_jsons:
                    logging.info(f'Poller at {websocket.remote_address.host}:{websocket.remote_address.port} sent new json {new_printer_jsons}')
                    await notify_of_state_change()
                    printer_jsons = new_printer_jsons
        finally:
            poller_pi = None
    else:
        await register_client(websocket)
        try:
            # This just forces the server to keep the connection alive until the client leaves
            async for message in websocket:
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
