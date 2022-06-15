"""Socket manager main file"""

import logging
import socket

logger = logging.getLogger(__name__)


class SocketManager:
    def __init__(self, ip, port):
        self._serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto=0)
        self._ip = ip
        self._port = port
        self._client_sock = None

    def __enter__(self):
        self._serv_sock.bind((self._ip, self._port))
        self._serv_sock.listen(10)
        logger.info(f"The server has started ip: {self._ip} port {self._port}")
        self._client_sock, client_address = self._serv_sock.accept()
        logger.info('Connected: {}'.format(client_address))
        return self._client_sock

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._client_sock:
            self._client_sock.close()
