"""Socket manager main file"""

import logging
import socket

logger = logging.getLogger(__name__)


class SocketManager:
    def __init__(self, ip, port, listen=4):
        self._serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto=0)
        self._ip = ip
        self._port = port
        self._listen = listen
        self._client_sockets_generator = None

    def __enter__(self):
        self._serv_sock.bind((self._ip, self._port))
        self._serv_sock.listen(self._listen)
        logger.info(f"The server has started ip: {self._ip} port {self._port}")
        self._client_sockets_generator = SocketManagerIterator(self._serv_sock)
        return self._client_sockets_generator

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.info(f"The server has closed: {self._ip} port {self._port}")
        self._serv_sock.close()


class SocketManagerIterator:
    def __init__(self, server_socket: socket):
        self._server_socket = server_socket

    def __iter__(self):
        return self

    def __next__(self) -> socket:
        client_sock, client_address = self._server_socket.accept()
        client_ip_port = f"{client_address[0]}:{client_address[1]}"
        logger.info('Connected: {}'.format(client_ip_port))
        return client_sock, client_address
