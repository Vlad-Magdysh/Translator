import pytest
from mock import patch, Mock
from mock.mock import PropertyMock
from request_handlers import DefaultClientHandler, MultiprocessingClientHandler

def test_run_parallel():
    input_user_address = "127.0.0.1"

    mock_translator = Mock()
    mock_client_socket = Mock()
    with patch.object(DefaultClientHandler, "handle_client") as mock_handle_client:
        # When
        mch = MultiprocessingClientHandler(mock_translator)
        mch.run_parallel(mock_client_socket, input_user_address)
        # Then
        mock_handle_client.assert_called_with(mock_client_socket, input_user_address)


def test_handle_client():
    input_user_address = "127.0.0.1"

    mock_translator = Mock()
    mock_client_socket = Mock()

    with patch('multiprocessing.Process') as mock_process:
        # When
        mch = MultiprocessingClientHandler(mock_translator)
        mch.handle_client(mock_client_socket, input_user_address)
        # Then
        assert mock_process.return_value.daemon is True
        mock_process.assert_called_with(target=mch.run_parallel, args=(mock_client_socket, input_user_address))
        mock_process.return_value.start.assert_called()


