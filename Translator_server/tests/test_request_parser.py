import pytest

from request_parser import RequestParser, LANGUAGE_PARAMETER, WORD_PARAMETER


@pytest.mark.parametrize(
    "input_request,expected",
    [("", {}),
     ("[en] hello", {LANGUAGE_PARAMETER: "en", WORD_PARAMETER: "hello"}),
     (" [ua] good", {LANGUAGE_PARAMETER: "ua", WORD_PARAMETER: "good"}),
     pytest.param("{en} bad", {LANGUAGE_PARAMETER: "en", WORD_PARAMETER:"bad"}, marks=pytest.mark.xfail),
     pytest.param("en bad", {LANGUAGE_PARAMETER: "en", WORD_PARAMETER:"bad"}, marks=pytest.mark.xfail)]
)
def test_parse_request(input_request, expected):
    rp = RequestParser()
    parsed_data = rp.parse_request(input_request)
    assert parsed_data == expected
