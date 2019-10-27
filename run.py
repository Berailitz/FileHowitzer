import argparse
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from ipaddress import ip_address, IPv4Address, IPv6Address
import logging
import os
from pathlib import Path
import qrcode
import socket
from typing import Union


DEFAULT_PORT = 8000
DEFAULT_ROOT = os.getcwd()


REMOTE_IPV4 = '8.8.8.8'
REMOTE_IPV6 = '2001:4860:4860::8888'
DEFAULT_IPV4 = '127.0.0.1'
DEFAULT_IPV6 = '::1'


def get_ip(force_v4: bool = False) -> str:
    if not force_v4 and socket.has_ipv6:
        family = socket.AF_INET6
        remote_ip = REMOTE_IPV6
    else:
        family = socket.AF_INET
        remote_ip = REMOTE_IPV4
    try:
        s = socket.socket(family, socket.SOCK_DGRAM)
        s.connect((remote_ip, 1))
        ip = s.getsockname()[0]
    except socket.timeout:
        if not force_v4 and socket.has_ipv6:
            ip = DEFAULT_IPV6
        else:
            ip = DEFAULT_IPV4
    finally:
        s.close()
    return ip_address(ip)


class IPv4ThreadingHTTPServer(ThreadingHTTPServer):
    address_family = socket.AF_INET


class IPv6ThreadingHTTPServer(ThreadingHTTPServer):
    address_family = socket.AF_INET6


class FileHowitzer(object):
    def __init__(self, port: int, root: Path,
                 host: Union[IPv4Address, IPv6Address, str],
                 ip: Union[IPv4Address, IPv6Address]):
        self.host = host
        self.port = port
        self.ip = ip
        self.root = root

    def show_qr_code(self):
        if isinstance(self.host, IPv6Address):
            url = f'http://[{self.host}]:{self.port}/'
        else:
            url = f'http://{self.host}:{self.port}/'
        logging.warning(f'URL is `{url}`.')
        qr = qrcode.QRCode()
        qr.add_data(url)
        qr.make()
        img = qr.make_image()
        img.show()

    def run(self):
        server_address = (str(self.ip), self.port)
        logging.warning(
            f'Listen on `{self.ip}, {self.port}` from `{self.root}`.')
        if self.ip.version == 4:
            httpd = IPv4ThreadingHTTPServer(
                server_address, partial(SimpleHTTPRequestHandler, directory=str(self.root)))
        else:
            httpd = IPv6ThreadingHTTPServer(
                server_address, partial(SimpleHTTPRequestHandler, directory=str(self.root)))
        httpd.serve_forever()


def ip_constructor(ip_text: str) -> Union[IPv4Address, IPv6Address, str]:
    try:
        ip = ip_address(ip_text)
    except ValueError:
        ip = ip_text
    finally:
        return ip


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--host', type=ip_constructor, help='Host in URL.')
    parser.add_argument(
        '--ip', '-i', type=ip_constructor, help='IP address to bind.')
    parser.add_argument(
        '--port', '-p', type=int, default=DEFAULT_PORT, help='Port to bind.')
    parser.add_argument(
        '--root', '-r', type=Path, default=DEFAULT_ROOT, help='Root directory to share.')
    parser.add_argument(
        "--no-qr", '-n', help="Do not show QR code.", action="store_true")
    args = parser.parse_args()
    if args.ip is None:
        if args.host is None:
            if socket.has_ipv6:
                args.ip = IPv6Address('::')
            else:
                args.ip = IPv4Address('0.0.0.0')
            args.host = get_ip()
        else:
            host_ip = ip_constructor(args.host)
            if isinstance(host_ip, IPv4Address):
                # Host is an IPv4 address
                args.ip = get_ip(force_v4=True)
            else:
                # Host is an IPv6 address or other strings
                args.ip = get_ip(force_v4=False)
    else:
        if isinstance(args.ip, IPv4Address):
            # IP is an IPv4 address
            if args.host is None:
                args.host = get_ip(force_v4=True)
            elif isinstance(args.host, IPv6Address):
                raise ValueError(
                    f'{args.ip} is an IPv4 while {args.host} is an IPv6.')
        elif isinstance(args.ip, IPv6Address):
            # IP is an IPv6 address
            if args.host is None:
                args.host = get_ip(force_v4=False)
            elif isinstance(args.host, IPv4Address):
                raise ValueError(
                    f'{args.ip} is an IPv6 while {args.host} is an IPv4.')
        else:
            raise ValueError(f'{args.ip} does not appear to be an IP address.')
    no_qr = args.no_qr
    delattr(args, 'no_qr')
    howitzer = FileHowitzer(**vars(args))
    if not no_qr:
        howitzer.show_qr_code()
    howitzer.run()


if __name__ == "__main__":
    main()
