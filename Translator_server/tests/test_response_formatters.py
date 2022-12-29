import pytest
from mock import patch, Mock
from mock.mock import PropertyMock

from response_formatters import JsonFormatter, XmlFormatter


@pytest.mark.parametrize(
    "input_data,expected",
    [("", '{\n    "word": ""\n}'),
     ("hello", '{\n    "word": "hello"\n}')]
)
def test_json_formatter(input_data, expected):
    jf = JsonFormatter.format_data(input_data)
    assert jf == expected


@pytest.mark.parametrize(
    "input_data,expected",
    [("", b'<?xml version="1.0" encoding="UTF-8" ?><root><item><word></word></item></root>'),
     ("hello", b'<?xml version="1.0" encoding="UTF-8" ?><root><item><word>hello</word></item></root>')]
)
def test_xml_formatter(input_data, expected):
    xf = XmlFormatter.format_data(input_data)
    assert xf == expected
