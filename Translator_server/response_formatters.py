import json
from abc import ABC, abstractmethod

from dicttoxml import dicttoxml

WORD = "word"


class AbstractFormatter(ABC):
    @abstractmethod
    def format_data(self, original_data: str) -> str:
        """
        Make class callable and formats an answer for the user

        Args:
            original_data (str) : data to format

        Returns:
            Formatted string
        """
        pass


class JsonFormatter(AbstractFormatter):
    @classmethod
    def format_data(cls, original_data: str) -> str:
        return json.dumps({WORD: original_data}, indent=4)


class XmlFormatter(AbstractFormatter):
    @classmethod
    def format_data(cls, original_data: str) -> str:
        data_to_format = [{WORD: original_data}]
        return dicttoxml(data_to_format, attr_type=False)
