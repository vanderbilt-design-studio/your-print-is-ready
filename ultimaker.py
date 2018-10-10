from collections import namedtuple, OrderedDict
from typing import Dict
from zeroconf import ServiceInfo
import requests
from requests.auth import HTTPDigestAuth
from config import ultimaker_application_name, ultimaker_user_name, ultimaker_credentials_filename
import json

# The mDNS response looks like this:
#   ServiceInfo(
#       type='_printer._tcp.local.',
#       name='ultimakersystem-REDACTED._printer._tcp.local.',
#       address=b'\xc0\xa8\x01\x12',
#       port=80,
#       weight=0,
#       priority=0,
#       server='ultimakersystem-REDACTED.local.',
#       properties={
#           b'type': b'printer',
#           b'hotend_serial_0': b'REDACTED',
#           b'cluster_size': b'1',
#           b'firmware_version': b'4.3.3.20180529',
#           b'machine': b'REDACTED',
#           b'name': b'U1',
#           b'hotend_type_0': b'AA 0.4'
#       }
#   )

# Serial number identifying the machine


class Serial(str):
    def __init__(self, serial_string: str = None):
        self.serial_string = serial_string


# A user/password pair
Credentials = namedtuple('Credentials', ['id', 'key'])


class CredentialsDict(OrderedDict):
    def __init__(self, credentials_filename):
        self.credentials_filename = credentials_filename
        with open(credentials_filename, 'r+') as credentials_file:
            credentials_json = json.load(credentials_file)
        try:
            for serial, credentials in credentials_json.items():
                # Convert json to a dictionary of field to value mappings
                kwargs = dict([(field, credentials[field])
                               for field in Credentials._fields])
                self[Serial(serial_string=serial)] = Credentials(**kwargs)
        except Exception as e:
            print(f'Encountered exception trying to load credentials.json {e}')
            return None

    def save(self):
        credentials_json: Dict[str, str] = {}
        for serial, credentials in credentials_json.items():
            credentials_json[serial] = credentials._asdict()
        with open(self.credentials_filename, 'w') as credentials_file:
            json.dump(self, credentials_file)


ultimaker_credentials: Dict[Serial, Credentials] = CredentialsDict(
    ultimaker_credentials_filename)


class Printer():
    def __init__(self, name, address, port):
        self.name = name
        self.address = address
        self.port = port
        print(self.name, self.address)

    def acquire_authorization(self):
        if self.is_authorized():
            return
        credentials_json = self.post_auth_request()
        self.save_credentials(credentials_json)

    def is_authorized(self) -> bool:
        if self.name in ultimaker_credentials:
            return self.get_auth_check()["message"] == "authorized"
        return False

    def save_credentials(self, credentials_json: Dict):
        ultimaker_credentials[Credentials(**credentials_json)]
        ultimaker_credentials.save()

    def post_auth_request(self) -> Dict:
        res = requests.post(url=f"{self.address}/auth/request",
                            data={'application': ultimaker_application_name, 'user': ultimaker_user_name})
        return json.load(res.content)

    def get_auth_check(self) -> Dict:
        res = requests.get(url=f"{self.address}/auth/check",
                           params={'id': ultimaker_credentials[self.name].id})
        return json.load(res.content)
