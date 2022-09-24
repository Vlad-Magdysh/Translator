import re

LANG_IDENTIFIER_PATTERN = r"(?<=\[)(\w+)(?=\])"
WORD_IDENTIFIER_PATTERN = r"(?<!\[)(\w+)(?!\])(?:\s|$)"

LANGUAGE_PARAMETER = "language"
WORD_PARAMETER = "word_to_translate"

class RequestParser:
    """
    Try to get specified field from the request string
    """
    def __init__(self):
        self.key_to_regex ={
            LANGUAGE_PARAMETER: LANG_IDENTIFIER_PATTERN,
            WORD_PARAMETER: WORD_IDENTIFIER_PATTERN
        }

    def parse_request(self, data: str) -> dict:
        result = {}
        for key, regex_pattern in self.key_to_regex.items():
            match = re.search(regex_pattern, data)
            if match is not None:
                result[key] = match.group()

        return result