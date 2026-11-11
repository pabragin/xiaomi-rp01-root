import importlib.util
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
spec = importlib.util.spec_from_file_location('launcher', ROOT / 'run.py')
launcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(launcher)


class LauncherTests(unittest.TestCase):
    def setUp(self):
        self.router_patch = patch('tools.exploit_set_macfilter_rules.Router')
        self.router = self.router_patch.start().return_value
        self.addCleanup(self.router_patch.stop)
        self.router.login.return_value = True
        self.router.inject.return_value = json.dumps({'code': 0})
        self.port_patch = patch.object(launcher.socket, 'create_connection')
        self.port = self.port_patch.start()
        self.addCleanup(self.port_patch.stop)

    def test_success_uses_authenticated_telnet_and_checks_port(self):
        launcher.enable_telnet('192.168.31.1', 'test-password')
        self.router.login.assert_called_once()
        payload = self.router.inject.call_args.args[0]
        self.assertIn('nvram set telnet_en=1', payload)
        self.assertIn('\ntelnetd\n', payload)
        self.port.assert_called_once_with(('192.168.31.1', 23), timeout=5)

    def test_bad_password_does_not_inject(self):
        self.router.login.return_value = False
        with self.assertRaisesRegex(RuntimeError, 'пароль'):
            launcher.enable_telnet('192.168.31.1', 'incorrect')
        self.router.inject.assert_not_called()

    def test_api_error_does_not_report_success(self):
        for response in ('<html>error</html>', '{"code":401}', '[]'):
            self.router.inject.return_value = response
            with self.assertRaises(RuntimeError):
                launcher.enable_telnet('192.168.31.1', 'test-password')
        self.port.assert_not_called()

    def test_api_timeout_can_still_start_service_but_closed_port_fails(self):
        self.router.inject.return_value = None
        launcher.enable_telnet('192.168.31.1', 'test-password')
        self.port.side_effect = OSError('refused')
        with self.assertRaisesRegex(RuntimeError, 'Порт 23'):
            launcher.enable_telnet('192.168.31.1', 'test-password')


if __name__ == '__main__':
    unittest.main()
