"""Main file of the server"""

import logging
import sys

from server_builder import build_server

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def main():
    """
    Reading Configuration order
    - Command line
    - Local config file
    - Environment vars
    """
    client_socket_handler, socket_manager = build_server()
    logger.info(f"Server mode selected: {client_socket_handler.__class__.__name__}")

    with socket_manager as connections_handler:
        while True:
            client_socket, client_address = connections_handler.wait_connection()
            client_socket_handler.handle_client(client_socket, client_address)


if __name__ == "__main__":
    main()