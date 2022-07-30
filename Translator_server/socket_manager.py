"""Socket manager main file"""

import logging
import socket

logger = logging.getLogger(__name__)

class ConnectionsHandler:
    def __init__(self, server_socket: socket):
        self._server_socket = server_socket

    def wait_connection(self) -> socket:
        client_sock, client_address = self._server_socket.accept()
        client_ip_port = f"{client_address[0]}:{client_address[1]}"
        logger.info('Connected: {}'.format(client_ip_port))
        return client_sock, client_address

class SocketManager:
    def __init__(self, ip, port, listen=4):
        self._ip = ip
        self._port = port
        self._listen = listen
        self._init_socket()

    def _init_socket(self):
        self._serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto=0)
        self._serv_sock.bind((self._ip, self._port))
        self._serv_sock.listen(self._listen)

    def __enter__(self) -> ConnectionsHandler:
        if self._serv_sock is None:
            self._init_socket()
        logger.info(f"The server has started ip: {self._ip} port {self._port}")
        return ConnectionsHandler(self._serv_sock)

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.info(f"The server has closed: {self._ip} port {self._port}")
        self._serv_sock.close()
        self._serv_sock = None
