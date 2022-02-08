import socket

import logging
logger = logging.getLogger(__name__)


class SocketManager:
    def __init__(self, ip='127.0.0.1', port=5555):
        self.serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto=0)
        self.ip = ip
        self.port = port
        self.client_sock = None

    def __enter__(self):
        self.serv_sock.bind((self.ip, self.port))
        self.serv_sock.listen(10)
        self.client_sock, client_address = self.serv_sock.accept()
        logger.info('Connected: {}'.format(client_address))
        return self.client_sock

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.client_sock:
            self.client_sock.close()
