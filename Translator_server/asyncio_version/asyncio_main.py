import asyncio, socket
import logging
import sys
from contextlib import closing
from gpytranslate import Translator


logging.basicConfig(stream=sys.stderr, level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

IP = '127.0.0.1'
PORT = 5555
MESSAGE_SIZE = 1024

translator = Translator()


async def client_processing(client_socket: socket, client_address: socket):
    loop = asyncio.get_event_loop()
    with closing(client_socket):
        while True:
            data = None
            try:
                data = await loop.sock_recv(client_socket, MESSAGE_SIZE)
            except ConnectionResetError:
                logger.warning("Client dropped the existing connection")
            if not data:
                break

            word_in_english = data.partition(b'\n')[0]
            if not word_in_english:
                continue

            word_in_english = word_in_english.decode("utf-8")
            logger.info(f"Client {client_address} request: value = {word_in_english}")
            try:
                answer = await translator.translate(word_in_english, sourcelang="en", targetlang="uk")

            except Exception as ex:
                logger.error(str(ex))
                continue

            client_socket.sendall(answer.text.encode("utf-8"))
            logger.info(f"Response {client_address}:  value = {answer.text}")

async def run_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto=0)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.setblocking(False)
    server.bind((IP, PORT))
    server.listen(10)

    loop = asyncio.get_event_loop()
    logger.info(f"The server has started ip: {IP} port {PORT}")
    while True:
        # If I don`t use await loop.sock_accept - I get BlockingIOError
        # I tried block try/except + pass but server.accept didn`t return control to process client_processing
        client_socket, client_address = await loop.sock_accept(server)
        logger.info('Connected: {}'.format(client_address))
        client_socket.setblocking(False)
        loop.create_task(client_processing(client_socket, client_address))

if __name__ == "__main__":
    asyncio.run(run_server())