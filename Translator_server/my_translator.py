import functools
from googletrans import Translator

import logging
logger = logging.getLogger(__name__)


def retry(number=5):
    """
    If the function raises an exception, it is called again 'number' times.
    :param number: number of retries
    :return: function return value
    """
    def internal(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = None
            for _ in range(number):
                try:
                    result = func(*args, **kwargs)
                except Exception as ex:
                    logger.warning(str(ex))
                else:
                    break

            return result

        return wrapper

    return internal


class MyTranslator:
    def __init__(self):
        self.translator = Translator(service_urls=['translate.googleapis.com', 'translate.google.com'])
        self.translator.raise_Exception = True

    @retry(10)
    def translate(self, word, dest='ru', src='auto'):
        return self.translator.translate(word, dest=dest, src=src).text
