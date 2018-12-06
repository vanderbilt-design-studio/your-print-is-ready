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

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
sockets = Sockets(app)

logging.basicConfig(level=logging.INFO, format=logging_format)

x_api_key = os.environ['X_API_KEY']

# Last-value caching of the poller pi response
printer_jsons = []
printer_jsons_last: datetime = None

clients: Set = set()


def state_json() -> str:
    return json.dumps({
        'printers': printer_jsons,
    })


def notify_of_state_change(ws):
    if ws in clients:
        if printer_jsons_last is None or datetime.utcnow() - printer_jsons_last > timedelta(seconds=30):
            print('Poller has not sent a message in > 30 seconds, sending nothing')
            ws.send('[]')
        ws.send(state_json())


@sockets.route('/')
def your_print_is_ready(ws):
    global printer_jsons, printer_jsons_last
    clients.add(ws)
    logging.info(f'Client {ws} joined')
    try:
        while not ws.closed:
            gevent.sleep(0.1)
            msg = ws.receive()
            if msg:
                message_json = json.loads(msg)
                if 'key' in message_json and secrets.compare_digest(message_json['key'], x_api_key):
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
                            notify_of_state_change(client)
                else:
                    print(f'Client {ws} key did not match expected key')
    finally:
        if not ws.closed:
            ws.close()
        logging.info(f'Client {ws} left')
        clients.remove(ws)


if __name__ == '__main__':
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
    server.serve_forever()
