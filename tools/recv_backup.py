#!/usr/bin/env python3
"""Receive base64 flash backups, checked against the device's /proc/mtd.

Usage: python3 tools/recv_backup.py [output_dir] [port] [--mtd proc-mtd.txt]
Upload /proc/mtd to /proc-mtd.txt before sending partitions, or supply --mtd.
BusyBox wget can truncate binary POST bodies at NUL; send partitions as base64.
"""
import argparse
import base64
import binascii
import http.server
import os
import re


def parse_mtd(text):
    """Read hexadecimal partition sizes from a Linux /proc/mtd snapshot."""
    sizes = {}
    for line in text.splitlines():
        if not line.strip() or re.fullmatch(r'\s*dev:\s+size\s+erasesize\s+name\s*', line):
            continue
        match = re.fullmatch(r'mtd(\d+):\s+([0-9a-fA-F]+)\s+[0-9a-fA-F]+\s+"[^"]*"\s*', line)
        if not match:
            raise ValueError(f"Invalid /proc/mtd line: {line!r}")
        index, size = int(match[1]), int(match[2], 16)
        if index in sizes or size <= 0:
            raise ValueError(f"Invalid or duplicate mtd{index}")
        sizes[index] = size
    if not sizes:
        raise ValueError("No partitions in /proc/mtd")
    return sizes


class Handler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def do_POST(self):
        try:
            total = int(self.headers.get("Content-Length", ""))
            if total <= 0:
                raise ValueError("Missing or invalid Content-Length")
        except ValueError as exc:
            self._reply(str(exc).encode(), 400)
            return
        buf = bytearray()
        while len(buf) < total:
            chunk = self.rfile.read(min(65536, total - len(buf)))
            if not chunk:
                self._reply(b"incomplete upload", 400)
                return
            buf += chunk
        fn = os.path.basename(self.path.strip("/"))
        data = bytes(buf)
        if fn == "proc-mtd.txt":
            try:
                sizes = parse_mtd(data.decode("ascii"))
            except (UnicodeError, ValueError) as exc:
                self._reply(str(exc).encode(), 400)
                return
            # One receiver session belongs to one device. Do not silently switch tables.
            if self.server.expected and sizes != self.server.expected:
                self._reply(b"partition table changed; start a new receiver/output directory", 409)
                return
            self.server.expected = sizes
            mark, note = "MTD", f"  {len(sizes)} partitions"
        else:
            match = re.fullmatch(r"mtd(\d+)\.(b64|bin)", fn)
            if not match:
                self._reply(b"expected proc-mtd.txt or mtdN.b64/bin", 400)
                return
            if match[2] == "b64":
                try:
                    data = base64.b64decode(b"".join(data.split()), validate=True)
                except (ValueError, binascii.Error):
                    self._reply(b"invalid base64", 400)
                    return
            fn = f"mtd{match[1]}.bin"
            expected = self.server.expected.get(int(match[1]))
            if expected is None:
                mark, note = "UNCHECKED", "  upload /proc/mtd as proc-mtd.txt first"
            elif len(data) == expected:
                mark, note = "OK", ""
            else:
                mark, note = "NG", f"  <-- expected {expected:,} bytes"
        path = os.path.join(self.server.out, fn)
        with open(path, "wb") as stream:
            stream.write(data)
        print(f"[{mark}] {path}  {len(data):,} bytes{note}", flush=True)
        self._reply(mark.encode(), 422 if mark == "NG" else 200)

    def _reply(self, body, status=200):
        self.send_response(status)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        self._reply(b"recv_backup ready\n")

    def log_message(self, *args):
        pass


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", nargs="?", default="./rp01_backup")
    parser.add_argument("port", nargs="?", type=int, default=8001)
    parser.add_argument("--mtd", help="local copy of the target device's /proc/mtd")
    args = parser.parse_args()
    expected = {}
    if args.mtd:
        try:
            with open(args.mtd, encoding="ascii") as stream:
                expected = parse_mtd(stream.read())
        except (OSError, UnicodeError, ValueError) as exc:
            parser.error(str(exc))
    os.makedirs(args.output, exist_ok=True)
    server = http.server.ThreadingHTTPServer(("0.0.0.0", args.port), Handler)
    server.out, server.expected = args.output, expected
    print(f"[*] Output: {os.path.abspath(args.output)}", flush=True)
    print(f"[*] Listening on 0.0.0.0:{args.port}; upload /proc/mtd to /proc-mtd.txt first.", flush=True)
    print("[*] [OK]=size matches, [NG]=size mismatch, [UNCHECKED]=no device size available", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
