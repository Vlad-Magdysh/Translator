import logging
import sys
import socket
from googletrans import Translator

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto=0)
serv_sock.bind(('127.0.0.1', 5555))
serv_sock.listen(10)

t = Translator(service_urls=['translate.googleapis.com', 'translate.google.com'])
t.raise_Exception = True

while True:
    client_sock, client_address = serv_sock.accept()
    logger.info('Connected: {}'.format(client_address))

    while True:
        data = None
        try:
            data = client_sock.recv(1024)
        except ConnectionResetError:
            logger.warning("Client {} dropped the existing connection".format(client_address))
        if not data:
            break
        word_in_english = data.partition(b'\n')[0]
        word_in_english = word_in_english.decode("cp1251")
        logger.info("Запрос от клиента (decoded): type = {} value = {}".format(type(word_in_english),word_in_english))
        for i in range(5):
            try:
                answer = t.translate(word_in_english, dest='ru').text
            except Exception as e:
                logger.warning(str(e))
            else:
                break
        logger.info("Ответ отправленный клиенту utf-8: type = {} value = {}".format(type(answer), answer))
        logger.info("Ответ отправленный клиенту cp1251: type = {} value = {}".format(type(answer.encode("cp1251")), answer.encode("cp1251")))
        client_sock.sendall(answer.encode("cp1251"))

    client_sock.close()
