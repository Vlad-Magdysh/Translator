#pragma once
#include <iostream> 
#include <cstdio> 
#include <winsock2.h> 
#include <vector>
#include <string.h>
#include <errno.h>
#include <memory>
#pragma comment(lib, "WS2_32.lib")

class MySocket
{
public:
	MySocket();
	void connect_to(const char* ip, int port, int number_of_attempts = 5);
	int send_to(const char* buffet, int len, int flags);
	int recive(char* buffer, int len, int flags);
	~MySocket();

private:
	SOCKET server;
	SOCKADDR_IN addr;
};