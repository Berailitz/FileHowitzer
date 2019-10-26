import socket
import qrcode
import logging
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

HOST = socket.gethostbyname(socket.gethostname())
PORT = 8000
URL = f'http://{HOST}:{PORT}/'


def show_qr_code():
    qr = qrcode.QRCode()
    qr.add_data(URL)
    qr.make()
    img = qr.make_image()
    img.show()


def serve_forever():
    server_address = (HOST, PORT)
    httpd = ThreadingHTTPServer(server_address, SimpleHTTPRequestHandler)
    httpd.serve_forever()


def main():
    logging.warning(f'Server on `{URL}`.')
    show_qr_code()
    serve_forever()


if __name__ == "__main__":
    main()
