"""Main file of the server"""

import logging
import sys

from server_builder import CommandLineArgumentsHandler as FirstConfigHandler

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


if __name__ == "__main__":
    """
    Reading Configuration order 
    - Command line
    - Local config file
    - Environment vars
    """
    client_socket_handler, socket_manager = FirstConfigHandler.handle()

    logger.info(f"Server mode selected: {client_socket_handler.__name__}")

    with socket_manager as connections_handler:
        while True:
            client_socket, client_address = connections_handler.wait_connection()
            client_socket_handler(client_socket, client_address)
