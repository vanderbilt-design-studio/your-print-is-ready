import unittest
from unittest.mock import Mock, patch
import json
import config
config.ultimaker_credentials_filename = '/tmp/credentials.json'
with open(config.ultimaker_credentials_filename, 'w+') as credentials_file:
    json.dump({}, credentials_file)
from ultimaker import Printer, CredentialsDict, Credentials
from uuid import UUID, uuid4

mock_uuid: UUID = uuid4()
mock_address = '127.0.0.1'
mock_port = '8080'
mock_id = '1234'
mock_key = 'abcd'
mock_credentials_json = {'id': mock_id, 'key': mock_key}


def default_printer_mock() -> Printer:
    printer = Printer(mock_uuid, mock_address, mock_port)
    printer.credentials_dict = default_credentials_dict_mock()
    #printer.set_credentials = patch.object(printer, 'set_credentials', wraps=printer.set_credentials)
    printer.post_auth_request = Mock(
        return_value=mock_credentials_json)
    printer.get_auth_check = Mock(return_value='authorized')
    printer.get_auth_verify = Mock(return_value=True)
    return printer


def default_credentials_dict_mock() -> CredentialsDict:
    credentials_dict = CredentialsDict('/tmp/credentials.json')
    credentials_dict[mock_uuid] = Credentials(**mock_credentials_json)
    credentials_dict.save = Mock()
    return credentials_dict


class AcquireCredentials(unittest.TestCase):
    def setUp(self):
        printer = default_printer_mock()
        del printer.credentials_dict[mock_uuid]
        self.printer = printer

    def test_printer_acquires_credentials(self):
        self.printer.credentials()
        self.assertDictEqual(self.printer.credentials_dict, default_credentials_dict_mock())
        self.printer.post_auth_request.assert_called_once()
        self.printer.get_auth_check.assert_not_called()
        self.printer.get_auth_verify.assert_not_called()

    def test_printer_acquires_credentials_only_once(self):
        self.printer.credentials()
        self.assertDictEqual(self.printer.credentials_dict, default_credentials_dict_mock())
        self.printer.post_auth_request.assert_called_once()
        self.printer.get_auth_check.assert_not_called()
        self.printer.get_auth_verify.assert_not_called()


class AlreadyHasCredentials(unittest.TestCase):
    def setUp(self):
        printer = default_printer_mock()
        printer.credentials = Mock(return_value=Credentials(**mock_credentials_json))
        self.printer = printer

    def test_printer_is_authorized(self):
        self.assertTrue(self.printer.is_authorized())
        self.printer.credentials.assert_called_once()
        self.printer.post_auth_request.assert_not_called()
        self.printer.get_auth_check.assert_called_once()


if __name__ == '__main__':
    unittest.main()
