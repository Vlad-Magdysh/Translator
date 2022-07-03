"""Main file of the server"""

import logging
import sys

from my_translator import MyTranslator
from socket_manager import SocketManager

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

MESSAGE_SIZE = 1024
IP = '127.0.0.1'
PORT = 5555

if __name__ == "__main__":
    translator = MyTranslator()
    with SocketManager(ip=IP, port=PORT) as client_sock:
        while True:
            data = None
            try:
                data = client_sock.recv(MESSAGE_SIZE)
            except ConnectionResetError:
                logger.warning("Client dropped the existing connection")
            if not data:
                break

            word_in_english = data.partition(b'\n')[0]
            word_in_english = word_in_english.decode("utf-8")
            logger.info(f"Client request (decoded): type = {type(word_in_english)} value = {word_in_english}")
            try:
                answer = translator.translate(word_in_english, dest='uk')
            except Exception as ex:
                logger.error(str(ex))
                continue

            client_sock.sendall(answer.encode("utf-8"))
            logger.info(f"Response: type = {type(answer)} value = {answer}")
