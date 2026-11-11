import base64
import contextlib
import http.client
import importlib.util
import io
from pathlib import Path
import subprocess
import tempfile
import threading
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'tools' / f'{name}.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


backup = load('recv_backup')
exploit = load('exploit_set_macfilter_rules')
TABLE = 'dev:    size   erasesize  name\n' + ''.join(
    f'mtd{i}: 00000004 00010000 "partition{i}"\n' for i in range(14))


class Issue9Tests(unittest.TestCase):
    def test_rd18_table_and_validation(self):
        self.assertEqual(backup.parse_mtd(TABLE), dict.fromkeys(range(14), 4))
        for text in ('', 'garbage', TABLE + 'mtd0: 4 1 "duplicate"\n'):
            with self.assertRaises(ValueError):
                backup.parse_mtd(text)
        self.assertEqual(backup.parse_mtd('mtd21: 00080000 00020000 "bdata"'), {21: 524288})

    def test_receiver(self):
        with tempfile.TemporaryDirectory() as directory:
            server = backup.http.server.ThreadingHTTPServer(('127.0.0.1', 0), backup.Handler)
            server.out, server.expected = directory, {}
            thread = threading.Thread(target=server.serve_forever)
            thread.start()
            def post(path, body):
                conn = http.client.HTTPConnection(*server.server_address, timeout=3)
                try:
                    conn.request('POST', path, body)
                    response = conn.getresponse()
                    return response.status, response.read()
                finally:
                    conn.close()
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(post('/mtd0.b64', base64.b64encode(b'abcd')), (200, b'UNCHECKED'))
                    self.assertEqual(post('/proc-mtd.txt', TABLE.encode()), (200, b'MTD'))
                    self.assertEqual(post('/mtd13.b64', b'YQBi\nYw==\n'), (200, b'OK'))
                    self.assertEqual(Path(directory, 'mtd13.bin').read_bytes(), b'a\x00bc')
                    self.assertEqual(post('/mtd0.b64', base64.b64encode(b'a')), (422, b'NG'))
                    self.assertEqual(post('/mtd14.b64', b'YWJjZA=='), (200, b'UNCHECKED'))
                    self.assertEqual(post('/mtd1.b64', b'!!!')[0], 400)
                    self.assertFalse(Path(directory, 'mtd1.bin').exists())
                    self.assertEqual(post('/proc-mtd.txt', b'broken')[0], 400)
                    self.assertEqual(server.expected, dict.fromkeys(range(14), 4))
                    self.assertEqual(post('/proc-mtd.txt', b'mtd0: 8 1 "other"')[0], 409)
            finally:
                server.shutdown()
                thread.join()
                server.server_close()

    def test_payload_shell_syntax(self):
        for commands in (exploit.DEFAULT_CMDS, exploit.TELNET_CMDS):
            payload = exploit.build_payload('\n'.join(commands))
            self.assertNotIn(';', payload)
            subprocess.run(['sh', '-n'], input=payload, text=True, check=True)
        self.assertNotIn('-l /bin/sh', '\n'.join(exploit.TELNET_CMDS))

    def test_default_selects_only_one_service(self):
        # Run the real conditional through harmless stand-ins, without contacting a router.
        for present in (True, False):
            commands = ['if true' if present else 'if false'] + exploit.DEFAULT_CMDS[1:]
            commands = [
                'echo SSH' if line == '/usr/sbin/dropbear -p 22' else
                'echo TELNET' if line == 'telnetd' else
                ':' if line not in ('if true', 'if false', 'then', 'else', 'fi') else line
                for line in commands
            ]
            result = subprocess.run(['sh'], input=exploit.build_payload('\n'.join(commands)),
                                    text=True, capture_output=True, check=True)
            self.assertEqual(result.stdout.strip(), 'SSH' if present else 'TELNET')


if __name__ == '__main__':
    unittest.main()
