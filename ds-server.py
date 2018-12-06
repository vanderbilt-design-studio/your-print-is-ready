from config import logging_format
import os
from typing import Set, List
import secrets
import logging
import http
import json
import ssl
import pathlib
from datetime import datetime, timedelta
from flask import Flask
from flask_sockets import Sockets
import gevent
from geventwebsocket.websocket import WebSocket

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
sockets = Sockets(app)

logging.basicConfig(level=logging.INFO, format=logging_format)

x_api_key = os.environ['X_API_KEY']

# Last-value caching of the poller pi response
printer_jsons: List = []
printer_jsons_last: datetime = None

clients: Set[WebSocket] = set()


def state_json() -> str:
    if printer_jsons_last is None or datetime.utcnow() - printer_jsons_last > timedelta(seconds=30):
        return '{ "printers": [] }'
    return json.dumps({
        'printers': printer_jsons,
    })


# This is needed to prevent Heroku from closing WebSockets
# Heroku's timeout is at 55 seconds, so this should be safe
# enough to prevent connection killing.
# https://devcenter.heroku.com/articles/websockets#timeouts
def keep_alive(ws: WebSocket):
    if ws and ws in clients and not ws.closed:
        ws.send(state_json())
        gevent.spawn_later(50, lambda: keep_alive(ws))


def update(ws: WebSocket):
    if ws and ws in clients and not ws.closed:
        ws.send(state_json())


@sockets.route('/')
def your_print_is_ready(ws: WebSocket):
    global printer_jsons, printer_jsons_last
    clients.add(ws)
    logging.info(f'Client {ws} joined')
    try:
        keep_alive(ws)
        while not ws.closed:
            gevent.sleep(0.1)
            msg = ws.receive()
            if msg:
                message_json = json.loads(msg)
                if 'key' in message_json and secrets.compare_digest(message_json['key'], x_api_key):
                    if ws in clients:
                        clients.remove(ws)
                    if 'printers' not in message_json:
                        print(
                            f'Poller {ws} sent a message but it had no printers')
                        continue
                    new_printer_jsons = message_json['printers']
                    if new_printer_jsons != printer_jsons:
                        logging.info(
                            f'Poller {ws} updated values')
                        printer_jsons = new_printer_jsons
                        printer_jsons_last = datetime.utcnow()
                        for client in clients:
                            gevent.spawn(lambda: update(client))
                    print(f'Done processing updates for poller {ws}')
                else:
                    print(f'Client {ws} key did not match expected key')
    finally:
        if ws and not ws.closed:
            ws.close()
        logging.info(f'Client {ws} left')
        clients.remove(ws)


if __name__ == '__main__':
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
    server.serve_forever()
