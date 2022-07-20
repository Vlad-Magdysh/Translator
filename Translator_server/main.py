"""Main file of the server"""
import argparse
import logging
import multiprocessing
import sys

from socket_manager import SocketManager
from handlers import threading_handler, multiprocessing_handler, default_single_client_handler

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

IP = '127.0.0.1'
PORT = 5555

MULTIPROCESSING = "multiprocessing"
THREADING = "threading"

def get_args():
    if __name__ == "__main__":

        parser = argparse.ArgumentParser(description="Translator server")

        parser.add_argument("-l", "--listen", type=int,
                            choices=list(range(1, 10)), default=4, help="Max number of connections")

        modes = parser.add_mutually_exclusive_group()
        modes.add_argument("-t", "--threading",
                           action='store_const',
                           const=THREADING,
                           dest='mode',
                           help="Start server in Threading mode")
        modes.add_argument("-p", "--multiprocessing",
                           action='store_const',
                           const=MULTIPROCESSING,
                           dest='mode',
                           help="Start server in Threading mode")

        parsed = parser.parse_args()
        return parsed

if __name__ == "__main__":
    mode_to_handler = {
        THREADING: threading_handler,
        MULTIPROCESSING: multiprocessing_handler,
        None: default_single_client_handler
    }
    arguments = get_args()
    client_socket_handler = mode_to_handler.get(arguments.mode, default_single_client_handler)

    logger.info(f"Server mode selected: {client_socket_handler.__name__ }")

    with SocketManager(ip=IP, port=PORT, listen=arguments.listen) as client_socket_generator:
        for client_socket, client_address in client_socket_generator:
            test_1 = client_socket_handler(client_socket, client_address)

