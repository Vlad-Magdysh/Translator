import pytest
import pytest_timeout
from mock import patch, Mock
from mock.mock import PropertyMock

from request_handlers import DefaultClientHandler, MESSAGE_SIZE

# with pytest.raises(Exception)
# with patch('foo.call_api', ):
#     with pytest.raises(ConnectionResetError) as excinfo:
#         create_key('localhost:8080', 'spam', 'eggs')
#     assert excinfo.value.message == 'mocked error'

def test_read_data():
    input_bytes = b'hello'
    expected_data = "hello"

    translator_mock = Mock()
    client_socket_mock = Mock()
    client_socket_mock.recv.return_value = input_bytes

    dch = DefaultClientHandler(translator_mock)
    result = dch._read_data(client_socket_mock)

    assert result == expected_data
    client_socket_mock.recv.assert_called_with(MESSAGE_SIZE)
    translator_mock.assert_not_called()


def test_read_data_empty_bytes():
    input_bytes = b''
    expected_data = ""

    translator_mock = Mock()
    client_socket_mock = Mock()
    client_socket_mock.recv.return_value = input_bytes

    dch = DefaultClientHandler(translator_mock)
    result = dch._read_data(client_socket_mock)

    assert result == expected_data
    client_socket_mock.recv.assert_called_with(MESSAGE_SIZE)
    translator_mock.assert_not_called()

def test_read_data_connection_exception_is_caught():
    input_bytes = b'hello'
    expected_data = None

    translator_mock = Mock()
    client_socket_mock = Mock()
    client_socket_mock.recv.side_effect = ConnectionResetError('mocked error')

    dch = DefaultClientHandler(translator_mock)
    result = dch._read_data(client_socket_mock)

    assert result == expected_data
    client_socket_mock.recv.assert_called_with(MESSAGE_SIZE)
    translator_mock.assert_not_called()

def test_read_data_another_exception_is_not_caught():
    translator_mock = Mock()
    client_socket_mock = Mock()
    client_socket_mock.recv.side_effect = Exception('mocked error')

    dch = DefaultClientHandler(translator_mock)
    with pytest.raises(Exception) as excinfo:
        dch._read_data(client_socket_mock)
    assert str(excinfo.value) == 'mocked error'

    client_socket_mock.recv.assert_called_with(MESSAGE_SIZE)
    translator_mock.assert_not_called()

#with patch('request_handlers.RequestParser') as mock_request_parser:
def test_process_request_successful():
    input_data_to_translate = "[en] привіт"
    parsed_input_data = {"language": "en", "word_to_translate": "привіт"}
    unformatted_translate_answer = "hello"
    formatted_data = {"word": "hello"}

    request_parser_mock = Mock()
    request_parser_mock.parse_request.return_value = parsed_input_data

    translator_mock = Mock()
    translator_mock.translate.return_value = unformatted_translate_answer

    response_formatter_mock = Mock()
    response_formatter_mock.format_data.return_value = formatted_data

    dch = DefaultClientHandler(
        translator_mock,
        response_formatter=response_formatter_mock,
        request_parser=request_parser_mock
        )
    result = dch._process_request(input_data_to_translate)

    assert result == formatted_data

    request_parser_mock.parse_request.assert_called_with(input_data_to_translate)
    translator_mock.translate.assert_called_with(word="привіт", dest="en")
    response_formatter_mock.format_data.assert_called_with(unformatted_translate_answer)


def test_process_request_no_response_formatter():
    input_data_to_translate = "[en] привіт"
    parsed_input_data = {"language": "en", "word_to_translate": "привіт"}
    unformatted_translate_answer = "hello"

    request_parser_mock = Mock()
    request_parser_mock.parse_request.return_value = parsed_input_data

    translator_mock = Mock()
    translator_mock.translate.return_value = unformatted_translate_answer

    dch = DefaultClientHandler(
        translator_mock,
        response_formatter=None,
        request_parser=request_parser_mock
        )
    result = dch._process_request(input_data_to_translate)

    assert result == unformatted_translate_answer

    request_parser_mock.parse_request.assert_called_with(input_data_to_translate)
    translator_mock.translate.assert_called_with(word="привіт", dest="en")


def test_process_request_translator_exception_is_caught():
    input_data_to_translate = "[en] привіт"
    parsed_input_data = {"language": "en", "word_to_translate": "привіт"}
    exception_message = "mocked message"
    expected_message = f"EXCEPTION!{exception_message}"

    request_parser_mock = Mock()
    request_parser_mock.parse_request.return_value = parsed_input_data

    translator_mock = Mock()
    translator_mock.translate.side_effect = Exception('mocked message')

    response_formatter_mock = Mock()

    dch = DefaultClientHandler(
        translator_mock,
        response_formatter=None,
        request_parser=request_parser_mock
        )
    result = dch._process_request(input_data_to_translate)

    assert result == expected_message

    request_parser_mock.parse_request.assert_called_with(input_data_to_translate)
    translator_mock.translate.assert_called_with(word="привіт", dest="en")
    response_formatter_mock.format_data.assert_not_called()


def test_process_request_empty_response():
    input_data_to_translate = "[en] привіт"
    parsed_input_data = {"language": "en", "word_to_translate": "привіт"}
    translator_empty_response = ""
    formatted_data = {"word": translator_empty_response}
    expected_value = "EXCEPTION!empty_response"

    request_parser_mock = Mock()
    request_parser_mock.parse_request.return_value = parsed_input_data

    translator_mock = Mock()
    translator_mock.translate.return_value = translator_empty_response

    dch = DefaultClientHandler(
        translator_mock,
        response_formatter=None,
        request_parser=request_parser_mock
        )
    result = dch._process_request(input_data_to_translate)

    assert result == expected_value

    request_parser_mock.parse_request.assert_called_with(input_data_to_translate)
    translator_mock.translate.assert_called_with(word="привіт", dest="en")


def test_send_data():
    input_data = "hello"
    expected_value = None

    translator_mock = Mock()
    client_socket_mock = Mock()
    client_socket_mock.sendall.return_value = input_data

    dch = DefaultClientHandler(translator_mock)
    result = dch._send_data(input_data, client_socket_mock, '127.0.0.1')

    assert result == expected_value

    client_socket_mock.sendall.assert_called_with(b"hello")
    translator_mock.assert_not_called()


# Marked timeout to prevent infinity loop in handle_client function
@pytest.mark.timeout(30)
def test_handle_client():
    mock_received_bytes = b"[en] hello"
    mock_process_request_return_value = "translated"
    input_client_address = "127.0.0.1"

    translator_mock = Mock()
    client_socket_mock = Mock()
    # The second element is required to break the loop
    client_socket_mock.recv.side_effect = [mock_received_bytes, b'']
    with patch.object(DefaultClientHandler, "_process_request", return_value=mock_process_request_return_value) \
            as process_request_mock:
        # WHEN
        dch = DefaultClientHandler(translator_mock)
        result = dch.handle_client(client_socket_mock, input_client_address)
        # THEN
        assert result is None
        process_request_mock.assert_called_with("[en] hello", input_client_address)
    client_socket_mock.sendall.assert_called_with(b"translated")


@pytest.mark.timeout(10)
def test_handle_client_empty_input_from_client():
    mock_received_bytes = b"[en] hello"
    mock_process_request_return_value = "translated"
    input_client_address = "127.0.0.1"

    translator_mock = Mock()
    client_socket_mock = Mock()

    client_socket_mock.recv.side_effect = [b'']
    with patch.object(DefaultClientHandler, "_process_request", return_value=mock_process_request_return_value) \
            as process_request_mock:

        dch = DefaultClientHandler(translator_mock)
        result = dch.handle_client(client_socket_mock, input_client_address)

        assert result is None
        process_request_mock.assert_not_called()
    client_socket_mock.sendall.assert_not_called()


@pytest.mark.timeout(10)
def test_handle_client_empty_answer():
    mock_received_bytes = b"[en] hello"
    mock_process_request_return_value = "translated"
    input_client_address = "127.0.0.1"

    translator_mock = Mock()
    client_socket_mock = Mock()
    # The second element is required to break the loop
    client_socket_mock.recv.side_effect = [mock_received_bytes, b'']
    with patch.object(DefaultClientHandler, "_process_request", return_value="") as process_request_mock:
        # WHEN
        dch = DefaultClientHandler(translator_mock)
        result = dch.handle_client(client_socket_mock, input_client_address)
        # THEN
        assert result is None
        process_request_mock.assert_called_with("[en] hello", input_client_address)
    # It`s important
    client_socket_mock.sendall.assert_not_called()
