import json
from abc import abstractmethod, ABC
from dicttoxml import dicttoxml


class AbstractFormatter(ABC):
    @abstractmethod
    def __call__(self, original_data: str) -> str:
        """
        Make class callable and formats an answer for the user

        Args:
            original_data (str) : data to format

        Returns:
            Formatted string
        """
        pass

class JsonFormatter(AbstractFormatter):
    def __call__(self, original_data: str) -> str:
        return json.dumps({"word": original_data}, indent=4)

class XmlFormatter(AbstractFormatter):
    def __call__(self, original_data: str) -> str:
        data_to_format = [{"word": original_data}]
        return dicttoxml(data_to_format, custom_root='response', attr_type=False)



