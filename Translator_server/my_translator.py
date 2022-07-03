"""Module with MyTranslator implementation"""

import functools
import logging
import time

from googletrans import Translator

logger = logging.getLogger(__name__)


def retry(number=5, timeout=0.1):
    """
    If the function raises an exception, it is called again 'number' times.
    Pass last exception
    :param timeout: duration between requests
    :param number: number of retries
    :return: function return value
    """
    def internal(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = None
            for _ in range(number-1):
                try:
                    result = func(*args, **kwargs)
                except Exception as ex:
                    logger.warning(str(ex))
                    time.sleep(timeout)
                else:
                    break

            if result is None:
                result = func(*args, **kwargs)

            return result

        return wrapper

    return internal


class MyTranslator:
    """
    Wrapper on the googletrans.Translator
    """
    def __init__(self):
        self._translator = Translator(service_urls=['translate.googleapis.com', 'translate.google.com'])
        self._translator.raise_Exception = True

    @retry(number=10, timeout=0.5)
    def translate(self, word, dest='uk', src='auto'):
        """
        Translate a word from a language to another
        :param word: Word to translate
        :param dest: Language to translate
        :param src: Input word language, default auto
        :return: str , a translated word
        """
        return self._translator.translate(word, dest=dest, src=src).text
