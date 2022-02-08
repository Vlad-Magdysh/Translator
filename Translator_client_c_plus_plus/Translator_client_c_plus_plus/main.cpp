#define _WINSOCK_DEPRECATED_NO_WARNINGS
#include <iostream> 
#include <cstdio> 
#include <winsock2.h> 
#include <vector>

#pragma comment(lib, "WS2_32.lib")

#include "MySocket.h"

using namespace std;

using Message = std::vector<char>; // type alias for std::vector<char>

std::ostream& operator<< (std::ostream& out, const Message& v) {
	auto iter = v.begin();
	while (iter != v.end() && *iter !=0)
	{
		cout << *iter++;
	}
	cout << endl;
	return out;
}

int main() {
	// Setup utf-8 format
	SetConsoleOutputCP(CP_UTF8);
	setvbuf(stdout, nullptr, _IOFBF, 1000);
	
	const char* IP = "127.0.0.1";
	const int PORT = 5555;

	MySocket my_socket;

	try {
		my_socket.connect_to(IP, PORT);
	}
	catch (exception& ex)
	{
		cerr << ex.what() << endl;
		return -1;
	}
	
	const int MESSAGE_SIZE = 100;
	Message recvbuf(MESSAGE_SIZE+1);
	while(true)
	{ 
		int text_len = 0;
		string user_input;
		cin >> user_input;
		if (user_input == "")
			continue;

		text_len = my_socket.send_to(user_input.c_str(), user_input.size(), 0);
		cout << "Sent " << text_len << " bytes\n";

		//Cyrillic are encoded using 2 bytes 
		text_len = my_socket.recive(recvbuf.data(), MESSAGE_SIZE, 0);

		if (text_len > 0) {
			cout << "Recived " << text_len << " bytes\n";
			recvbuf[text_len] = 0; // END of the recived message
		}
		else if (text_len == 0) {
			cout << "Connection closed\n";
		}
		else {
			std::cerr << "Failed to receive\n";
		}

		cout << "RESULT: " << recvbuf;
	}
}