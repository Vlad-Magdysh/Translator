import socket
import threading
import multiprocessing

import logging
from my_translator import MyTranslator

logger = logging.getLogger(__name__)

translator = MyTranslator()

MESSAGE_SIZE = 1024


def client_processing(client_address, client_socket):
    while True:
        data = None
        try:
            data = client_socket.recv(MESSAGE_SIZE)
        except ConnectionResetError:
            logger.warning("Client dropped the existing connection")
        if not data:
            break

        word_in_english = data.partition(b'\n')[0]
        word_in_english = word_in_english.decode("utf-8")
        logger.info(f"Client {client_address} request: value = {word_in_english}")
        try:
            answer = translator.translate(word_in_english, dest='uk')
        except Exception as ex:
            logger.error(str(ex))
            continue

        client_socket.sendall(answer.encode("utf-8"))
        logger.info(f"Response {client_address}:  value = {answer}")
    client_socket.close()


def threading_handler(client_socket: socket, client_address: socket):
    """
    Takes a new client socket, creates a thread to handle user` requests
    :return:
    """
    thread = threading.Thread(target=client_processing, args=(client_address, client_socket))
    thread.start()
    return thread


def multiprocessing_handler(client_address: socket, client_socket: socket):
    """
    Takes a new client socket, creates a new process to handle users` requests
    :return:
    """
    process = multiprocessing.Process(target=client_processing, args=(client_address, client_socket))
    # When a main process exits, it attempts to terminate all of its daemonic child processes.
    process.daemon = True
    process.start()
    return process


def default_single_client_handler(client_socket: socket, client_address: socket):
    """
    Takes a new client socket and processing only this one, until client will close the connection
    :param client_address: Client IP and port, like 127.0.0.1:1234
    :param client_socket: Client Socket object
    :return:
    """
    return client_processing(client_socket, client_address)