import logging
import multiprocessing
import socket
import threading
from contextlib import closing
from typing import Optional

from my_translator import BaseTranslator
from request_parser import LANGUAGE_PARAMETER, WORD_PARAMETER, RequestParser
from response_formatters import AbstractFormatter

logger = logging.getLogger(__name__)


MESSAGE_SIZE = 1024


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
            _translator (Base_translator): translates word from a language to another
            _response_formatter (BaseFormatter): converts an answer from _translator in a custom format
        """
        # Now the project has only one _translator, but I left the opportunity to pass it as parameter to handlers
        # So in the future it will be easy to add a new _translator, read the configs and create a handler with it.
        self._translator = translator
        self.response_formatter = response_formatter
        self._request_parser = request_parser if request_parser is not None else RequestParser()

    def _read_data(self, client_socket: socket):
        try:
            data = client_socket.recv(MESSAGE_SIZE)
            return data.decode("utf-8")
        except ConnectionResetError:
            logger.warning("Client dropped the existing connection")

    def _process_request(self, data, client_address=''):
        parameters = self._request_parser.parse_request(data)
        lang = parameters.get(LANGUAGE_PARAMETER, 'uk')
        word = parameters.get(WORD_PARAMETER, '')
        logger.info(f"Client {client_address} request: lang = {lang} value = {word}")
        try:
            answer = self._translator.translate(word=parameters.get(WORD_PARAMETER, ""),
                                               dest=lang)
        except Exception as ex:
            logger.error(str(ex))
            answer = f"EXCEPTION!{ex}".encode("utf-8")
        else:
            if self.response_formatter is not None:
                answer = self.response_formatter.format_data(answer)
        if not len(answer):
            answer = 'EXCEPTION!empty_response'
        return answer

    def _send_data(self, data, client_socket: socket, client_address):
        client_socket.sendall(data.encode("utf-8"))
        logger.info(f"Response {client_address}:  value = {data}")

    def handle_client(self, client_socket: socket, client_address: socket) -> None:
        """
        Skeleton of the client processing algorithm
        """
        with closing(client_socket):
            while True:
                logging.info(f"Reading data from {client_address}")
                data = self._read_data(client_socket)

                if not data:
                    logging.info(f"No data received from {client_address}")
                    break

                logging.info(f"Processing request from {client_address}")
                answer = self._process_request(data, client_address)

                if not answer:
                    logging.warning(f"Skip empty response {client_address}")
                    continue

                logging.info(f"Sending response to {client_address}")
                self._send_data(answer, client_socket, client_address)

    @property
    def response_formatter(self) -> Optional[AbstractFormatter]:
        return self._response_formatter

    @response_formatter.setter
    def response_formatter(self, response_formatter: Optional[AbstractFormatter]) -> None:
        self._response_formatter = response_formatter


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
