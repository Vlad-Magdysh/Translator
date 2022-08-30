import argparse
import os.path
from abc import ABC, abstractmethod
from typing import Optional
import ipaddress
import configparser
from my_translator import MyTranslator
from socket_manager import SocketManager
from handlers import DefaultClientHandler, MultithreadingClientHandler, MultiprocessingClientHandler
from response_formatters import JsonFormatter, XmlFormatter

IP = '127.0.0.1'
PORT = 5555

MULTIPROCESSING = "multiprocessing"
THREADING = "threading"
DEFAULT= "default"

JSON_OUTPUT_FORMAT = "JSON"
XML_OUTPUT_FORMAT = "XML"

CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), "config.ini")


class BaseConfigHandler(ABC):
    mode_to_handler = {
        THREADING: MultithreadingClientHandler,
        MULTIPROCESSING: MultiprocessingClientHandler,
        DEFAULT: DefaultClientHandler
    }
    formatter_map = {
        JSON_OUTPUT_FORMAT: JsonFormatter,
        XML_OUTPUT_FORMAT: XmlFormatter
    }

    @staticmethod
    @abstractmethod
    def handle(client_handler_object: Optional[DefaultClientHandler] = None,
               socket_manager_object: Optional[SocketManager] = None):
        raise NotImplementedError()

class EnvVariablesHandler(BaseConfigHandler):
    @staticmethod
    def handle(client_handler_object: Optional[DefaultClientHandler] = None,
               socket_manager_object: Optional[SocketManager] = None):
        if client_handler_object is None:
            client_socket_handler_class = BaseConfigHandler.mode_to_handler[os.getenv("SERVER_MODE", DEFAULT)]
            client_handler_object = client_socket_handler_class(
                translator=MyTranslator(),
                response_formatter=BaseConfigHandler.formatter_map.get(os.getenv("SERVER_RESPONSE_FORMAT", None))
            )

        if socket_manager_object is None:
            socket_manager_object = SocketManager(
                ip=os.getenv("SERVER_IP", "127.0.0.1"),
                port=os.getenv("SERVER_PORT", 5555),
                listen=os.getenv("SERVER_LISTEN", 4)
            )
        return client_handler_object, socket_manager_object


class ConfigFileHandler(BaseConfigHandler):
    @staticmethod
    def handle(client_handler_object: Optional[DefaultClientHandler] = None,
               socket_manager_object: Optional[SocketManager] = None):

        if os.path.isfile(CONFIG_FILE_PATH):
            config = configparser.ConfigParser()
            config.read(CONFIG_FILE_PATH)

            if client_handler_object is None and config.has_section("HANDLER"):
                handler_options = dict(config.items('HANDLER'))
                client_socket_handler_class = BaseConfigHandler.mode_to_handler[handler_options["mode"]]
                client_handler_object = client_socket_handler_class(
                    translator=MyTranslator(),
                    response_formatter=BaseConfigHandler.formatter_map.get(handler_options["format"])
                )

            if socket_manager_object is None and config.has_section("SOCKET_MANAGER"):
                socket_manager_options = dict(config.items('SOCKET_MANAGER'))
                socket_manager_object = SocketManager(
                    ip=socket_manager_options["ip"],
                    port=socket_manager_options["port"],
                    listen=socket_manager_options["listen"]
                )

        return EnvVariablesHandler.handle(client_handler_object, socket_manager_object)


class CommandLineArgumentsHandler(BaseConfigHandler):
    @staticmethod
    def handle(client_handler_object: Optional[DefaultClientHandler] = None,
               socket_manager_object: Optional[SocketManager] = None):
        arguments = get_args()

        if client_handler_object is None and arguments.mode is not None:
            client_socket_handler_class = BaseConfigHandler.mode_to_handler[arguments.mode]
            client_handler_object = client_socket_handler_class(
                translator=MyTranslator()
            )

        if client_handler_object.response_formatter is None:
            client_handler_object.response_formatter = BaseConfigHandler.formatter_map.get(arguments.format)

        if socket_manager_object is None and arguments.ip is not None and arguments.port is not None:
            socket_manager_object = SocketManager(ip=arguments.ip, port=arguments.port, listen=arguments.listen)

        return ConfigFileHandler.handle(client_handler_object, socket_manager_object)

def get_args():
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