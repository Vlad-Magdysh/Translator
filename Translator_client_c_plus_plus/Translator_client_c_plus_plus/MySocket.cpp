#define _WINSOCK_DEPRECATED_NO_WARNINGS
#include "MySocket.h"

int ERROR_BUFFER_SIZE = 1024;

MySocket::MySocket() : server(socket(AF_INET, SOCK_STREAM, 0)) {}

void MySocket::connect_to(const char* ip, int port, int number_of_attempts)
{
	if (server == INVALID_SOCKET)
	{
		throw std::runtime_error("Invalid socket");
	}
	addr.sin_addr.s_addr = inet_addr(ip); //connect to server
	addr.sin_family = AF_INET;
	addr.sin_port = htons(port); //port
	while (connect(server, (SOCKADDR*)&addr, sizeof(addr)) == SOCKET_ERROR) {
		if (--number_of_attempts == 0)
		{
			throw std::runtime_error("Couldn't connect to the server");
		}
	}
}

int MySocket::send_to(const char* buffer, int len, int flags) {
	int number = send(server, buffer, len, flags);
	if (number == -1) {
		std::unique_ptr<char[]> buf(new char[ERROR_BUFFER_SIZE]);
		strerror_s(buf.get(), ERROR_BUFFER_SIZE, errno);
		throw std::runtime_error(buf.get());
	}
	return number;
}

int MySocket::recive(char* buffer, int len, int flags) {
	int number = recv(server, buffer, len, flags);
	if (number == -1) {
		std::unique_ptr<char[]> buf(new char[ERROR_BUFFER_SIZE]);
		strerror_s(buf.get(), ERROR_BUFFER_SIZE, errno);
		throw std::runtime_error(buf.get());
	}
	return number;
}

MySocket::~MySocket() {
	closesocket(server);
}