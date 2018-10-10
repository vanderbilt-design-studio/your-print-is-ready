import unittest
from unittest.mock import Mock
from ultimaker import Printer, CredentialsDict


class UltimakerTest(unittest.TestCase):
    def setUp(self):
        printer = Printer('mockName', 'localhost', '8081')
        printer.save_credentials = Mock()
        printer.post_auth_request = Mock(
            return_value={'id': 'mockId', 'key': 'mockKey'})
        printer.get_auth_check = Mock(return_value={'authorized'})
        self.printer = printer

    def test_printer_authorize(self):
        self.printer.acquire_authorization()
        self.printer.save_credentials.assert_called_once()
        self.printer.post_auth_request.assert_called_once()
        self.printer.get_auth_check.assert_not_called()


if __name__ == '__main__':
    unittest.main()
