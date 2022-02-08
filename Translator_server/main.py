import logging
import sys

from my_translator import MyTranslator
from socket_manager import SocketManager

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


if __name__ == "__main__":
    MESSAGE_SIZE = 1024
    translator = MyTranslator()
    with SocketManager() as client_sock:
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
            logger.info("Запрос от клиента (decoded): type = {} value = {}".format(type(word_in_english), word_in_english))

            answer = translator.translate(word_in_english, dest='ru')

            client_sock.sendall(answer.encode("utf-8"))
            logger.info("Ответ клиенту: type = {} value = {}".format(type(answer), answer))
