import pytest
from mock import patch, Mock
from mock.mock import PropertyMock
from request_handlers import DefaultClientHandler, MultithreadingClientHandler


def test_handle_client():
    input_user_address = "127.0.0.1"

    mock_translator = Mock()
    mock_client_socket = Mock()

    with patch('threading.Thread') as mock_process, \
            patch.object(DefaultClientHandler, "handle_client") as mock_handle_client:
        # When
        mch = MultithreadingClientHandler(mock_translator)
        mch.handle_client(mock_client_socket, input_user_address)
        # Then
        assert mock_process.return_value.daemon is True
        mock_process.assert_called_with(target=mock_handle_client, args=(mock_client_socket, input_user_address))
        mock_process.return_value.start.assert_called()
