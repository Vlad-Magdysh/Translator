from abc import abstractmethod, ABC


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
    pass

class XmlFormatter(AbstractFormatter):
    pass



