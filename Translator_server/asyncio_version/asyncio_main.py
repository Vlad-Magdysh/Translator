import asyncio, socket
import logging
import sys
from contextlib import closing
from async_google_trans_new import AsyncTranslator

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

IP = '127.0.0.1'
PORT = 5555
MESSAGE_SIZE = 1024

translator = AsyncTranslator()


async def client_processing(client_socket: socket, client_address: socket):
    with closing(client_socket):
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
                answer = await translator.translate(word_in_english, lang_src='en', lang_tgt='uk')
            except Exception as ex:
                logger.error(str(ex))
                continue

            client_socket.sendall(answer.encode("utf-8"))
            logger.info(f"Response {client_address}:  value = {answer}")

async def run_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto=0)
    server.bind((IP, PORT))
    server.listen(10)
    server.setblocking(False)

    loop = asyncio.get_event_loop()
    logger.info(f"The server has started ip: {IP} port {PORT}")
    while True:
        client_socket, client_address = await loop.sock_accept(server)
        client_socket.setblocking(False)
        loop.create_task(client_processing(client_socket, client_address))

if __name__ == "__main__":
    asyncio.run(run_server())