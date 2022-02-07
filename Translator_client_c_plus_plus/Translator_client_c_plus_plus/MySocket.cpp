#define _WINSOCK_DEPRECATED_NO_WARNINGS
#include "MySocket.h"

using namespace std;

MySocket::MySocket()
{
	WSAStartup(MAKEWORD(2, 0), &WSAData);
	server = socket(AF_INET, SOCK_STREAM, 0);
}

void MySocket::connect_to(const char* ip, int port, int number_of_attempts)
{
	if (server == INVALID_SOCKET)
	{
		throw exception("Invalid socket");
	}
	addr.sin_addr.s_addr = inet_addr(ip); //коннект к серверу
	addr.sin_family = AF_INET;
	addr.sin_port = htons(port); //порт
	while (connect(server, (SOCKADDR*)&addr, sizeof(addr)) == SOCKET_ERROR) {
		if (--number_of_attempts == 0)
		{
			throw exception("Couldn't connect to the server");
		}
	}
}

int MySocket::send_to(const char* buffet, int len, int flags) {
	return send(server, buffet, len, flags);
}

int MySocket::recive(char* buffer, int len, int flags) {
	return recv(server, buffer, len, flags);
}

MySocket::~MySocket() {
	closesocket(server);
	WSACleanup();
}