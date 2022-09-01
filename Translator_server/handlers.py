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

LANG_IDENTIFIER_PATTERN = r"(?<=\[)(\w+)(?=\])"
WORD_IDENTIFIER_PATTERN = r"(?<!\[)(\w+)(?!\])(?:\s|$)"

LANGUAGE_PARAMETER = "language"
WORD_PARAMETER = "word_to_translate"

class RequestParser:
    """
    Try to get specified field from the request string
    """
    def __init__(self):
        self.key_to_regex ={
            LANGUAGE_PARAMETER: LANG_IDENTIFIER_PATTERN,
            WORD_PARAMETER: WORD_IDENTIFIER_PATTERN
        }

    def parse_request(self, data: str) -> dict:
        result = {}
        for key, regex_pattern in self.key_to_regex.items():
            match = re.search(regex_pattern, data)
            if match is not None:
                result[key] = match.group()

        return result


class DefaultClientHandler:
    """
    The class use direct approach for client processing: one instance = one_client
    """
    def __init__(
            self, translator: BaseTranslator,
            response_formatter: Optional[AbstractFormatter] = None,
            request_parser: Optional[RequestParser] = None):
        """
        Args:
            translator (BaseTranslator): translates word from a language to another
            response_formatter (BaseFormatter): converts an answer from translator in a custom format
        """
        # Now the project has only one translator, but I left the opportunity to pass it as parameter to handlers
        # So in the future it will be easy to add a new translator, read the configs and create a handler with it.
        self.translator = translator
        self.response_formatter = response_formatter
        self.request_parser = request_parser if request_parser is not None else RequestParser()

    def _init_regex(self):
        """
        Creates a dictionary attr_name to special regex. Regex will be used to identify an attribute in the request str.
        Method may be overwritten in the inherited classes
        Args:

        :return:
        """

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

                parameters = self.request_parser.parse_request(data.decode("utf-8"))
                logger.info(
                    f"Client {client_address} request: "
                    f"lang = {parameters.get(LANGUAGE_PARAMETER, 'uk')} "
                    f"value = {parameters.get(WORD_PARAMETER, '')}")

                try:
                    answer = self.translator.translate(word=parameters.get(WORD_PARAMETER, ""),
                                                       dest=parameters.get(LANGUAGE_PARAMETER, "uk"))
                except Exception as ex:
                    logger.error(str(ex))
                    client_socket.sendall(f"EXCEPTION!{ex}".encode("utf-8"))
                    continue

                if self.response_formatter is not None:
                    answer = self.response_formatter(answer)
                if not len(answer):
                    answer = 'EXCEPTION!empty_response'
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
