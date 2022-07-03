#pragma once
#include <iostream> 
#include <cstdio> 
#include <winsock2.h> 
#include <vector>
#include <string.h>
#include <errno.h>
#include <memory>

class MySocket
{
public:
	MySocket();
	void connect_to(const char* ip, int port, int number_of_attempts = 5);
	int send_message(const char* buffet, int len, int flags);
	int receive_message(char* buffer, int len, int flags);
	~MySocket();

private:
	SOCKET server_socket;
	SOCKADDR_IN addr;
};