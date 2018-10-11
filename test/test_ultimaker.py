import unittest
from unittest.mock import Mock
import config
config.ultimaker_credentials_filename = '/tmp/credentials.json'
from ultimaker import Printer, CredentialsDict

mock_name = '2D printer'
mock_address = '127.0.0.1'
mock_port = '8080'
mock_id = '1234'
mock_key = 'abcd'
mock_credentials = {mock_name: {'id': mock_id, 'key': mock_key}}


class AquireCredentials(unittest.TestCase):
    def setUp(self):
        printer = Printer(mock_name, mock_address, mock_port)
        printer.credentials_dict = {}
        printer.save_credentials = Mock()
        printer.post_auth_request = Mock(
            return_value={'id': mock_id, 'key': mock_key})
        printer.get_auth_check = Mock(return_value={'authorized'})
        printer.get_auth_verify = Mock(return_value=True)
        self.printer = printer

    def test_printer_acquire_credentials(self):
        self.printer.acquire_credentials()
        self.printer.save_credentials.assert_called_once()
        self.printer.post_auth_request.assert_called_once()
        self.printer.get_auth_check.assert_not_called()
        self.printer.get_auth_verify.assert_not_called()

class DontAcquireCredentials(unittest.TestCase):
    def setUp(self):
        printer = Printer(mock_name, mock_address, mock_port)
        printer.credentials_dict = mock_credentials
        printer.save_credentials = Mock()
        printer.post_auth_request = Mock(
            return_value={'id': mock_id, 'key': mock_key})
        printer.get_auth_check = Mock(return_value={'authorized'})
        printer.get_auth_verify = Mock(return_value=True)
        self.printer = printer

    def test_printer_doesnt_acquire_credentials(self):
        self.printer.acquire_credentials()
        self.printer.save_credentials.assert_not_called()
        self.printer.post_auth_request.assert_not_called()
        self.printer.get_auth_check.assert_not_called()
        self.printer.get_auth_verify.assert_called_once()


if __name__ == '__main__':
    unittest.main()
