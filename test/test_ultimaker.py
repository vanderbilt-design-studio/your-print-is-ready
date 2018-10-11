import unittest
from unittest.mock import Mock, patch
import json
import config
config.ultimaker_credentials_filename = '/tmp/credentials.json'
with open(config.ultimaker_credentials_filename, 'w+') as credentials_file:
    json.dump({}, credentials_file)
from ultimaker import Printer, CredentialsDict, Credentials
from uuid import UUID, uuid4
import os

mock_guid: UUID = uuid4()
mock_address = '127.0.0.1'
mock_port = '8080'
mock_id = '1234'
mock_key = 'abcd'
mock_credentials = Credentials(mock_id, mock_key)
mock_credentials_json = mock_credentials._asdict()


def default_printer_mock() -> Printer:
    printer = Printer(mock_address, mock_port, mock_guid)
    printer.credentials_dict = default_credentials_dict_mock()
    # TODO: understand unittest.mock patch method so the set_credentials method can be asserted on
    #printer.set_credentials = patch.object(printer, 'set_credentials', wraps=printer.set_credentials)
    printer.post_auth_request = Mock(
        return_value=mock_credentials_json)
    printer.get_auth_check = Mock(return_value='authorized')
    printer.get_auth_verify = Mock(return_value=True)
    return printer


def default_credentials_dict_mock() -> CredentialsDict:
    credentials_dict = CredentialsDict('/tmp/credentials.json')
    credentials_dict[mock_guid] = Credentials(**mock_credentials_json)
    credentials_dict.save = Mock()
    return credentials_dict


class AcquireCredentialsTest(unittest.TestCase):
    def setUp(self):
        printer = default_printer_mock()
        del printer.credentials_dict[mock_guid]
        self.printer = printer

    def test_printer_acquires_credentials(self):
        self.printer.credentials()
        self.assertDictEqual(self.printer.credentials_dict,
                             default_credentials_dict_mock())
        self.printer.post_auth_request.assert_called_once()
        self.printer.get_auth_check.assert_not_called()
        self.printer.get_auth_verify.assert_not_called()

    def test_printer_acquires_credentials_only_once(self):
        self.printer.credentials()
        self.assertDictEqual(self.printer.credentials_dict,
                             default_credentials_dict_mock())
        self.printer.post_auth_request.assert_called_once()
        self.printer.get_auth_check.assert_not_called()
        self.printer.get_auth_verify.assert_not_called()


class AlreadyHasCredentialsTest(unittest.TestCase):
    def setUp(self):
        printer = default_printer_mock()
        printer.credentials = Mock(
            return_value=Credentials(**mock_credentials_json))
        self.printer = printer

    def test_printer_is_authorized(self):
        self.assertTrue(self.printer.is_authorized())
        self.printer.credentials.assert_called_once()
        self.printer.post_auth_request.assert_not_called()
        self.printer.get_auth_check.assert_called_once()


class CredentialsDictTest(unittest.TestCase):
    def setUp(self):
        self.credentials_dict_json = {mock_guid.hex: mock_credentials_json}
        random_filename = f'/tmp/credentials_{uuid4()}.json'
        with open(random_filename, 'w+') as credentials_file:
            json.dump(self.credentials_dict_json, credentials_file)
        self.credentials_dict = CredentialsDict(random_filename)

    def test_credentials_file_loads_correctly(self):
        self.assertTrue(mock_guid in self.credentials_dict)
        self.assertDictEqual(mock_credentials_json,
                             self.credentials_dict[mock_guid]._asdict())

    def test_credentials_file_saves_correctly(self):
        self.credentials_dict.save()
        with open(self.credentials_dict.credentials_filename, 'r') as credentials_file:
            saved_json = json.load(credentials_file)
        self.assertDictEqual(self.credentials_dict_json, saved_json)

    def tearDown(self):
        os.remove(self.credentials_dict.credentials_filename)


class CredentialsDictEdgeCaseTest(unittest.TestCase):
    def test_credentials_file_loads_empty_when_json_completely_invalid(self):
        invalid_json_credentials_dict = CredentialsDict(
            f'/tmp/credentials_{uuid4()}.json')
        self.assertDictEqual(invalid_json_credentials_dict, {})
        os.remove(invalid_json_credentials_dict.credentials_filename)

    def test_credentials_file_loads_some_when_json_partially_invalid(self):
        partially_valid_json_filename = f'/tmp/credentials_{uuid4()}.json'
        with open(partially_valid_json_filename, 'w') as credentials_file:
            json.dump({mock_guid.hex: mock_credentials_json,
                       uuid4().hex: 'invalid'}, credentials_file)
        partially_valid_json_credentials_dict = CredentialsDict(
            partially_valid_json_filename)
        self.assertTrue(
            mock_guid in partially_valid_json_credentials_dict)
        self.assertDictEqual(
            mock_credentials_json, partially_valid_json_credentials_dict[mock_guid]._asdict())
        os.remove(partially_valid_json_credentials_dict.credentials_filename)


if __name__ == '__main__':
    unittest.main()
