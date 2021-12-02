#define _WINSOCK_DEPRECATED_NO_WARNINGS
#include <iostream> 
#include <cstdio> 
#include <winsock2.h> 
#include <vector>
#pragma comment(lib, "WS2_32.lib")
using namespace std;



int main() {
	setlocale(LC_ALL, "Russian");

	WSADATA WSAData;
	SOCKET server;
	SOCKADDR_IN addr;
	WSAStartup(MAKEWORD(2, 0), &WSAData);
	if ((server = socket(AF_INET, SOCK_STREAM, 0)) == INVALID_SOCKET) {
		cout << "Socket creation failed with error: " << WSAGetLastError() << endl;
		return -1;
	}

	addr.sin_addr.s_addr = inet_addr("127.0.0.1"); //коннект к серверу
	addr.sin_family = AF_INET;
	addr.sin_port = htons(5555); //порт
	while (connect(server, (SOCKADDR*)&addr, sizeof(addr)) == SOCKET_ERROR) {
		cout << "Server connection failed with error: " << WSAGetLastError() << endl;
	}

	cout << "Connected to server!" << endl;


	while(true)
	{ 
		int res_len = 0;
		string user_input;
		cin >> user_input;
		if (user_input == "")
			continue;
		res_len = send(server, user_input.c_str(), user_input.size(), 0);
		printf("Sent %d bytes\n", res_len);

		vector<char> recvbuf(100);

		res_len = recv(server, recvbuf.data(), 80, 0);

		printf(recvbuf.data());
		cout << endl;
		if (res_len > 0)
			printf("Bytes received: %d\n", res_len);
		else if (res_len == 0)
			printf("Connection closed\n");
		else
			printf("recv failed with error: %d\n", WSAGetLastError());
	}

	closesocket(server);
	WSACleanup();
}