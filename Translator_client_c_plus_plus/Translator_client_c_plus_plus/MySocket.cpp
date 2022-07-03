#define _WINSOCK_DEPRECATED_NO_WARNINGS
#include "MySocket.h"

#pragma comment(lib, "WS2_32.lib")

const int ERROR_BUFFER_SIZE = 1024;

void check_operation_status(const int bytes_number)
{
	if (bytes_number == -1)
	{
		std::vector<char> buf(ERROR_BUFFER_SIZE);
		strerror_s(buf.data(), ERROR_BUFFER_SIZE, errno);
		throw std::runtime_error(buf.data());
	}
}

MySocket::MySocket() : server_socket(socket(AF_INET, SOCK_STREAM, 0)), addr({ 0 }) {}

void MySocket::connect_to(const char* ip, int port, int number_of_attempts)
{
	if (server_socket == INVALID_SOCKET)
	{
		throw std::runtime_error("Invalid socket");
	}
	addr.sin_addr.s_addr = inet_addr(ip);
	addr.sin_family = AF_INET;
	addr.sin_port = htons(port);
	while (connect(server_socket, (SOCKADDR*)&addr, sizeof(addr)) == SOCKET_ERROR)
	{
		if (--number_of_attempts == 0)
		{
			throw std::runtime_error("Couldn't connect to the server");
		}
	}
}

int MySocket::send_message(const char* buffer, int len, int flags) {
	const int bytes_number = send(server_socket, buffer, len, flags);
	check_operation_status(bytes_number);
	return bytes_number;
}

int MySocket::receive_message(char* buffer, int len, int flags) {
	const int bytes_number = recv(server_socket, buffer, len, flags);
	if (bytes_number == -1)
	check_operation_status(bytes_number);
	return bytes_number;
}

MySocket::~MySocket() {
	closesocket(server_socket);
}