#!/usr/bin/env python3
"""Russian interactive launcher for RD18; run with Python 3 on Windows/macOS/Linux."""
import contextlib
import getpass
import io
import ipaddress
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import venv

ROOT = Path(__file__).resolve().parent


def prepare_environment():
    executable = ROOT / '.venv' / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
    if '--ready' in sys.argv[1:]:
        return
    if not executable.exists():
        print('Подготавливаю Python. Это нужно только при первом запуске.', flush=True)
        venv.EnvBuilder(with_pip=True).create(ROOT / '.venv')
    available = subprocess.run([str(executable), '-c', 'import requests'],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if available.returncode:
        print('Устанавливаю requests. Нужен интернет.', flush=True)
        subprocess.run([str(executable), '-m', 'pip', 'install', 'requests'], check=True)
    raise SystemExit(subprocess.call([str(executable), str(ROOT / 'run.py'), '--ready']))


def enable_telnet(ip, password):
    from tools.exploit_set_macfilter_rules import Router, TELNET_CMDS, build_payload
    import random
    router = Router(ip, password)
    # The underlying script's diagnostics are Chinese; keep the simple flow in Russian.
    with contextlib.redirect_stdout(io.StringIO()):
        try:
            router.detect()
        except SystemExit:
            raise RuntimeError('Не удалось найти роутер. Проверьте IP и подключение к его сети.') from None
        if not router.login():
            raise RuntimeError('Не удалось войти. Проверьте пароль веб-интерфейса роутера.')
        mac = '02:' + ':'.join(f'{random.randrange(256):02X}' for _ in range(5))
        response = router.inject(build_payload('\n'.join(TELNET_CMDS)), mac)
    if response:
        try:
            result = json.loads(response)
        except (ValueError, TypeError):
            raise RuntimeError('Роутер вернул неожиданный ответ. Telnet не подтверждён.') from None
        if not isinstance(result, dict) or result.get('code') != 0:
            raise RuntimeError('Роутер отклонил команду. Telnet не подтверждён.')
    # A request may time out after executing; verify the actual service port.
    try:
        with socket.create_connection((ip, 23), timeout=5):
            pass
    except OSError:
        raise RuntimeError('Порт 23 недоступен. Telnet не запустился или соединение заблокировано.') from None


def open_client(ip):
    candidates = [ROOT / 'putty.exe']
    found = shutil.which('putty')
    if found:
        candidates.append(Path(found))
    if os.name == 'nt':
        for variable in ('ProgramFiles', 'ProgramFiles(x86)'):
            if os.environ.get(variable):
                candidates.append(Path(os.environ[variable]) / 'PuTTY' / 'putty.exe')
    for client in candidates:
        if client.is_file():
            subprocess.Popen([str(client), '-telnet', ip, '-P', '23'])
            print('Открыл PuTTY. Введите логин root и root-пароль.')
            return
    print(f'Откройте PuTTY: Host Name = {ip}, Connection type = Telnet, Port = 23.')
    print(f'В macOS/Linux с установленным клиентом: telnet {ip}')


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    print('Xiaomi BE5000 (RD18), прошивка 1.0.91 — включение Telnet\n', flush=True)
    prepare_environment()
    ip = input('IP роутера [192.168.31.1]: ').strip() or '192.168.31.1'
    try:
        ipaddress.IPv4Address(ip)
    except ValueError:
        raise RuntimeError('Введите IPv4-адрес, например 192.168.31.1.') from None
    password = getpass.getpass('Пароль веб-интерфейса роутера (ввод скрыт): ')
    sn = input('Серийный номер SN для расчёта root-пароля (Enter — пропустить): ').strip()
    if sn:
        from tools.calc_root_pwd import root_pwd
        print(f'Логин: root. Расчётный root-пароль: {root_pwd(sn)}')
        print('Если root-пароль меняли, используйте установленный пароль.')
    print('Подключаюсь к роутеру и включаю Telnet…', flush=True)
    enable_telnet(ip, password)
    print('\nПорт Telnet 23 доступен. Логин: root.')
    open_client(ip)
    print('После перезагрузки при необходимости запустите этот файл ещё раз.')


if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print('\nЗапуск отменён.')
        sys.exit(1)
    except (RuntimeError, OSError, subprocess.SubprocessError) as exc:
        print(f'\nОшибка: {exc}')
        sys.exit(1)
