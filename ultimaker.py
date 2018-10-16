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
        guid: UUID
        credentials: Credentials
        for guid, credentials in credentials_json.items():
            try:
                # Convert json to a dictionary of field to value mappings
                kwargs = dict([(field, credentials[field])
                               for field in Credentials._fields])
                self[UUID(guid)] = Credentials(**kwargs)
            except Exception as e:
                print(
                    f'Exception in parsing the credentials instance in credentials.json with guid {guid}, skipping it: {e}')

    def save(self):
        credentials_json: Dict[str, str] = {}
        guid: UUID
        credentials: Credentials
        for guid, credentials in self.items():
            credentials_json[guid.hex] = credentials._asdict()
        with open(self.credentials_filename, 'w') as credentials_file:
            json.dump(credentials_json, credentials_file)


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
                                   'datetime_cleaned', 'source', 'source_user', 'source_application', 'name', 'uuid', 'reprint_original_uuid', 'state', 'progress'])


class Printer():
    def __init__(self, address: str, port: str, guid=None):
        self.host = f'{address}:{port}'
        self.credentials_dict = ultimaker_credentials_dict
        self.guid = guid if guid else self.get_system_guid()
        self.credentials_verified = False

    def acquire_credentials(self):
        credentials_json = self.post_auth_request()
        self.set_credentials(credentials_json)

    def credentials(self) -> Credentials:
        if self.guid not in self.credentials_dict:
            self.acquire_credentials()
        elif not self.credentials_verified and not self.get_auth_verify(self.credentials_dict[self.guid]):
            del self.credentials_dict[self.guid]
            self.acquire_credentials()
        self.credentials_verified = True
        return self.credentials_dict[self.guid]

    def digest_auth(self) -> HTTPDigestAuth:
        credentials = self.credentials()
        return HTTPDigestAuth(credentials.id, credentials.key)

    def is_authorized(self) -> bool:
        self.credentials()
        return self.get_auth_check() == 'authorized'

    def set_credentials(self, credentials_json: Dict):
        self.credentials_dict[self.guid] = Credentials(**credentials_json)
        self.credentials_dict.save()

    def into_ultimaker_json(self) -> Dict[str, str]:
        try:
            status = self.get_printer_status()
            ultimaker_json = {
                'system': {
                    'name': self.get_system_name(),
                },
                'printer': {
                    'status': status,
                },
            }
            if status == 'printing':
                ultimaker_json['print_job'] = {
                    'time_elapsed': self.get_print_job_time_elapsed(),
                    'time_total': self.get_print_job_time_total(),
                    'progress': self.get_print_job_progress(),
                    'state': self.get_print_job_state(),
                }
        except:
            return {
                'name': self.get_system_name(),
            }

    # All of the request functions below are from the Ultimaker Swagger Api available at http://PRINTER_ADDRESS/docs/api/
    # You can only call things other than /auth/check and /auth/request when you have credentials.
    # -------------------------------------------------------------------------------------------------------------------

    def post_auth_request(self) -> Dict:
        return requests.post(url=f"http://{self.host}/api/v1/auth/request",
                             data={'application': ultimaker_application_name, 'user': ultimaker_user_name}).json()

    # Returns the response from an authorization check
    def get_auth_check(self) -> str:
        return requests.get(url=f"http://{self.host}/api/v1/auth/check/{self.credentials_dict[self.guid].id}").json()['message']

    # Returns whether the credentials are known to the printer. They may not be if the printer was reset.
    # Note that this is completely different from get_auth_check.
    def get_auth_verify(self, credentials: Credentials) -> bool:
        return requests.get(
            url=f"http://{self.host}/api/v1/auth/verify", auth=HTTPDigestAuth(credentials.id, credentials.key)).ok

    def get_printer_status(self) -> str:
        return requests.get(
            url=f"http://{self.host}/api/v1/printer/status", auth=self.digest_auth()).json()

    def get_print_job(self) -> PrintJob:
        return PrintJob(**requests.get(
            url=f"http://{self.host}/api/v1/print_job", auth=self.digest_auth()).json())

    def get_print_job_state(self) -> str:
        return requests.get(
            url=f"http://{self.host}/api/v1/print_job/state", auth=self.digest_auth()).json()

    def get_print_job_time_elapsed(self) -> int:
        return requests.get(
            url=f"http://{self.host}/api/v1/print_job/time_elapsed", auth=self.digest_auth()).json()

    def get_print_job_time_total(self) -> int:
        return requests.get(
            url=f"http://{self.host}/api/v1/print_job/time_total", auth=self.digest_auth()).json()

    def get_print_job_progress(self) -> float:
        return requests.get(
            url=f"http://{self.host}/api/v1/print_job/progress", auth=self.digest_auth()).json()

    def get_print_job_name(self) -> str:
        return requests.get(
            url=f"http://{self.host}/api/v1/print_job/name", auth=self.digest_auth()).json()

    def put_system_display_message(self, message: str, button_caption: str) -> str:
        return requests.put(url=f"http://{self.host}/api/v1/system/display_message", auth=self.digest_auth(), json={'message': message, 'button_caption': button_caption}).json()

    # Doesn't work as far as I've tested it
    def put_beep(self, frequency: float, duration: float) -> str:
        return requests.put(url=f"http://{self.host}/api/v1/beep", auth=self.digest_auth(), json={'frequency': frequency, 'duration': duration}).json()

    def get_system_guid(self) -> UUID:
        return UUID(requests.get(url=f'http://{self.host}/api/v1/system/guid').json())

    def get_system_name(self) -> str:
        return requests.get(url=f'http://{self.host}/api/v1/system/name').json()
