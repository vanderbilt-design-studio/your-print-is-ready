from collections import namedtuple, OrderedDict
from typing import Dict
from zeroconf import ServiceInfo
import requests
from requests.auth import HTTPDigestAuth
from config import ultimaker_application_name, ultimaker_user_name, ultimaker_credentials_filename
import json
from uuid import UUID
import re

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
#           b'machine': b'9066.0',
#           b'name': b'U1',
#           b'hotend_type_0': b'AA 0.4'
#       }
#   )

# A user/password pair
Credentials = namedtuple('Credentials', ['id', 'key'])

def parse_server(server: str) -> UUID:
    server_pattern = re.compile('ultimakersystem(\w+?)\.local\.')
    return server_pattern.match(server).group(0)


class CredentialsDict(OrderedDict):
    def __init__(self, credentials_filename):
        self.credentials_filename = credentials_filename
        with open(credentials_filename, 'a+') as credentials_file:
            try:
                credentials_file.seek(0)
                credentials_json = json.load(credentials_file)
            except Exception as e:
                print(
                    f'Exception in parsing credentials.json, pretending it is empty: {e}')
                credentials_json = {}
        for uuid, credentials in credentials_json.items():
            try:
                # Convert json to a dictionary of field to value mappings
                kwargs = dict([(field, credentials[field])
                               for field in Credentials._fields])
                self[UUID(uuid)] = Credentials(**kwargs)
            except Exception as e:
                print(
                    f'Exception in parsing the credentials instance in credentials.json with uuid {uuid}, skipping it: {e}')

    def save(self):
        credentials_json: Dict[str, str] = {}
        for serial, credentials in credentials_json.items():
            credentials_json[serial] = credentials._asdict()
        with open(self.credentials_filename, 'w+') as credentials_file:
            json.dump(self, credentials_file)


ultimaker_credentials_dict: Dict[UUID, Credentials] = CredentialsDict(
    ultimaker_credentials_filename)

# {
#   "time_elapsed": 0,
#   "time_total": 0,
#   "datetime_started": "2018-10-10T00:46:40.776Z",
#   "datetime_finished": "2018-10-10T00:46:40.776Z",
#   "datetime_cleaned": "2018-10-10T00:46:40.776Z",
#   "source": "string",
#   "source_user": "string",
#   "source_application": "string",
#   "name": "string",
#   "uuid": "string",
#   "reprint_original_uuid": "string",
#   "state": "none"
# }
PrintJob = namedtuple('PrintJob', ['time_elapsed', 'time_total', 'datetime_started', 'datetime_finished',
                                   'datetime_cleaned', 'source', 'source_user', 'source_application', 'name', 'uuid', 'reprint_original_uuid', 'state'])


class Printer():
    def __init__(self, uuid: UUID, address: str, port: str):
        self.uuid = uuid
        self.address = address
        self.port = port
        self.credentials_dict = ultimaker_credentials_dict

    def acquire_credentials(self):
        credentials_json = self.post_auth_request()
        self.set_credentials(credentials_json)

    def credentials(self) -> Credentials:
        if self.uuid not in self.credentials_dict or not self.get_auth_verify():
            self.acquire_credentials()
        return self.credentials_dict[self.uuid]

    def digest_auth(self) -> HTTPDigestAuth:
        credentials = self.credentials()
        return HTTPDigestAuth(credentials.id, credentials.key)

    def is_authorized(self) -> bool:
        self.credentials()
        return self.get_auth_check() == 'authorized'

    def set_credentials(self, credentials_json: Dict):
        self.credentials_dict[self.uuid] = Credentials(**credentials_json)
        self.credentials_dict.save()

    # All of the request functions below are from the Ultimaker Swagger Api available at http://PRINTER_ADDRESS/docs/api/
    # You can only call things other than /auth/check and /auth/request when you have credentials.
    # -------------------------------------------------------------------------------------------------------------------

    def post_auth_request(self) -> Dict:
        res = requests.post(url=f"{self.address}/auth/request",
                            data={'application': ultimaker_application_name, 'user': ultimaker_user_name})
        return json.load(res.content)

    # Returns the response from an authorization check
    def get_auth_check(self) -> str:
        res = requests.get(url=f"{self.address}/auth/check",
                           params={'id': self.credentials_dict[self.uuid].id})
        return json.load(res.content)["message"]

    # Returns whether the credentials are known to the printer. They may not be if the printer was reset.
    # Note that this is completely different from get_auth_check.
    def get_auth_verify(self) -> bool:
        res = requests.get(
            url=f"{self.address}/auth/verify", auth=self.digest_auth())
        return res.ok

    def get_printer_status(self) -> str:
        res = requests.get(
            url=f"{self.address}/printer/status", auth=self.digest_auth())
        return res.text

    def get_print_job(self) -> PrintJob:
        res = requests.get(
            url=f"{self.address}/print_job", auth=self.digest_auth())
        return PrintJob(**json.load(res))

    def get_print_job_state(self) -> str:
        res = requests.get(
            url=f"{self.address}/print_job/state", auth=self.digest_auth())
        return res.text
