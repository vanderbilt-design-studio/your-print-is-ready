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

logging.basicConfig()

x_api_key = os.environ['X_API_KEY']

# Last-value caching of printers
printers = []

poller_pi = None

clients: Set[websockets.WebSocketServerProtocol] = set()


def state_json() -> str:
    return json.dumps(printers)


async def notify_of_state_change():
    if len(clients) > 0:
        message = state_json()
        await asyncio.wait([client.send(message) for client in clients])


async def register_client(websocket: websockets.WebSocketServerProtocol):
    clients.add(websocket)
    await websocket.send(state_json())


async def unregister_client(websocket: websockets.WebSocketServerProtocol):
    clients.remove(websocket)


async def event_loop(websocket: websockets.WebSocketServerProtocol, path):
    message = await websocket.recv()
    if secrets.compare_digest(message, x_api_key):
        poller_pi = websocket
        try:
            async for message in websocket:
                new_printers = json.loads(message)
                if new_printers != printers:
                    await notify_of_state_change()
                    printers = new_printers
        finally:
            poller_pi = None
    else:
        try:
            await register_client(websocket)
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
