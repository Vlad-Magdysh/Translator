import socket
import threading
import multiprocessing
import re
import logging
from contextlib import closing

from typing import Union, Optional
from my_translator import BaseTranslator
from response_formatters import AbstractFormatter

logger = logging.getLogger(__name__)


MESSAGE_SIZE = 1024
REQUEST_PATTERN = r"\[(\w+)\]\s(\w+)"


class DefaultClientHandler:
    """
    The class use direct approach for client processing: one instance = one_client
    """
    def __init__(self, translator: BaseTranslator, response_formatter: Optional[AbstractFormatter] = None):
        """
        Args:
            translator (BaseTranslator): translates word from a language to another
            response_formatter (BaseFormatter): converts an answer from translator in a custom format
        """
        # Now the project has only one translator, but I left the opportunity to pass it as parameter to handlers
        # So in the future it will be easy to add a new translator, read the configs and create a handler with it.
        self.translator = translator
        self.response_formatter = response_formatter

    def handle_client(self, client_socket: socket, client_address: socket) -> None:
        """
        Skeleton of the client processing algorithm
        """
        with closing(client_socket):
            while True:
                data = None
                try:
                    data = client_socket.recv(MESSAGE_SIZE)
                except ConnectionResetError:
                    logger.warning("Client dropped the existing connection")
                if not data:
                    break

                parsed_request = re.search(REQUEST_PATTERN, data.decode("utf-8"))
                if parsed_request is not None:
                    language, word_to_translate = parsed_request.groups()
                else:
                    continue
                logger.info(
                    f"Client {client_address} request: destination lang = {language} value = {word_to_translate}")

                try:
                    answer = self.translator.translate(word_to_translate, dest=language)
                except Exception as ex:
                    logger.error(str(ex))
                    continue

                if self.response_formatter is not None:
                    answer = self.response_formatter(answer)

                client_socket.sendall(answer.encode("utf-8"))
                logger.info(f"Response {client_address}:  value = {answer}")

    @property
    def response_formatter(self) -> Union[AbstractFormatter, None]:
        return self.__response_formatter

    @response_formatter.setter
    def response_formatter(self, response_formatter: Union[AbstractFormatter, None]) -> None:
        self.__response_formatter = response_formatter


class MultithreadingClientHandler(DefaultClientHandler):
    def handle_client(self, client_socket: socket, client_address: socket) -> None:
        thread = threading.Thread(target=super().handle_client, args=(client_socket, client_address))
        thread.daemon = True
        thread.start()


class MultiprocessingClientHandler(DefaultClientHandler):
    def handle_client(self, client_socket: socket, client_address: socket) -> None:
        process = multiprocessing.Process(target=super().handle_client, args=(client_socket, client_address))
        # When a main process exits, it attempts to terminate all of its daemonic child processes.
        process.daemon = True
        process.start()
