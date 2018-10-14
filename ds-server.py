import asyncio
import pathlib
import ssl
import websockets


async def echo(websocket, path):
    async for message in websocket:
        await websocket.send(message)

ssl_context: ssl.SSLContext = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain(pathlib.Path(
    '/etc/letsencrypt/live/iot.vanderbilt.design/fullchain.pem'),
    keyfile=pathlib.Path('/etc/letsencrypt/live/iot.vanderbilt.design/privkey.pem'))

asyncio.get_event_loop().run_until_complete(
    websockets.serve(echo, '0.0.0.0', 443, ssl=ssl_context))
asyncio.get_event_loop().run_forever()
