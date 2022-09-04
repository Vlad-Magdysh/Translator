import argparse
import configparser
import ipaddress
import os.path
from abc import ABC, abstractmethod

from my_translator import MyTranslator
from request_handlers import (DefaultClientHandler,
                              MultiprocessingClientHandler,
                              MultithreadingClientHandler)
from response_formatters import JsonFormatter, XmlFormatter
from socket_manager import SocketManager

IP = '127.0.0.1'
PORT = 5555

MULTIPROCESSING = "multiprocessing"
THREADING = "threading"
DEFAULT = "default"

JSON_OUTPUT_FORMAT = "JSON"
XML_OUTPUT_FORMAT = "XML"

MODE_TO_CLIENT_HANDLER = {
    THREADING: MultithreadingClientHandler,
    MULTIPROCESSING: MultiprocessingClientHandler,
    DEFAULT: DefaultClientHandler
}
FORMATTER_MAP = {
    JSON_OUTPUT_FORMAT: JsonFormatter,
    XML_OUTPUT_FORMAT: XmlFormatter
}

CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), "config.ini")


class ConfigurationObject:
    """
    Accumulates server configuration.
    Forbids updating an attribute if it has already been initialized.
    So if the first ConfigHandler has initialized an attribute - the next ConfigHandler must not override
    """
    __slots__ = ("server_mode", "response_formatter", "ip", "port", "listen")

    def __setattr__(self, name, value):
        if getattr(self, name, None) is None:
            super().__setattr__(name, value)


class BaseConfigHandler(ABC):
    @staticmethod
    @abstractmethod
    def handle(config_object: ConfigurationObject) -> None:
        raise NotImplementedError()


class EnvVariablesHandler(BaseConfigHandler):
    @staticmethod
    def handle(config_object: ConfigurationObject) -> None:
        config_object.server_mode = os.getenv("SERVER_MODE", DEFAULT)
        config_object.response_formatter = os.getenv("SERVER_RESPONSE_FORMAT", None)
        config_object.ip = os.getenv("SERVER_IP", "127.0.0.1")
        config_object.port = os.getenv("SERVER_PORT", 5555)
        config_object.listen = os.getenv("SERVER_LISTEN", 4)


class ConfigFileHandler(BaseConfigHandler):
    @staticmethod
    def handle(config_object: ConfigurationObject) -> None:
        if os.path.isfile(CONFIG_FILE_PATH):
            config = configparser.ConfigParser()
            config.read(CONFIG_FILE_PATH)

            if config.has_section("HANDLER"):
                config_object.server_mode = config["HANDLER"]["mode"]
                config_object.response_formatter = config["HANDLER"]["format"]

            if config.has_section("SOCKET_MANAGER"):
                config_object.ip = config["SOCKET_MANAGER"]["ip"]
                config_object.port = int(config["SOCKET_MANAGER"]["port"])
                config_object.listen = int(config["SOCKET_MANAGER"]["listen"])

        return EnvVariablesHandler.handle(config_object)


class CommandLineArgumentsHandler(BaseConfigHandler):
    @staticmethod
    def handle(config_object: ConfigurationObject) -> None:
        arguments = _get_args()

        config_object.server_mode = arguments.mode
        config_object.response_formatter = arguments.format
        config_object.ip = arguments.ip
        config_object.port = arguments.port
        config_object.listen = arguments.listen

        return ConfigFileHandler.handle(config_object)


def _get_args():
    parser = argparse.ArgumentParser(description="Translator server")

    parser.add_argument("-l", "--listen", type=int,
                        choices=list(range(1, 10)), default=4, help="Max number of connections")
    parser.add_argument("-ip", "--ip", type=ipaddress.ip_address, required=False, help="Server IP address")
    parser.add_argument("-port", "--port", dest="port", type=int, required=False, help="Server port")

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
    modes.add_argument("-dh", "--default_handler",
                       action='store_const',
                       const=DEFAULT,
                       dest='mode',
                       help="Start server in Default mode")

    formats = parser.add_mutually_exclusive_group()
    formats.add_argument("-j", "--json",
                         action='store_const',
                         const=JSON_OUTPUT_FORMAT,
                         dest='format',
                         help="Server will return responses in JSON format")
    formats.add_argument("-x", "--xml",
                         action='store_const',
                         const=XML_OUTPUT_FORMAT,
                         dest='format',
                         help="Server will return responses in XML format")

    parsed = parser.parse_args()
    return parsed


def build_server():
    """"""
    configs = ConfigurationObject()
    CommandLineArgumentsHandler.handle(config_object=configs)
    client_handler_class = MODE_TO_CLIENT_HANDLER.get(configs.server_mode)
    client_handler_object = client_handler_class(
        translator=MyTranslator(),
        response_formatter=FORMATTER_MAP.get(configs.response_formatter)
    )
    server_socket_manager_object = SocketManager(
        ip=configs.ip,
        port=configs.port,
        listen=configs.listen
    )
    return client_handler_object, server_socket_manager_object
