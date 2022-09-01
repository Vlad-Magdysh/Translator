#define _WINSOCK_DEPRECATED_NO_WARNINGS
#define _CRT_SECURE_NO_WARNINGS
#include <iostream> 
#include <cstdio> 
#include <winsock2.h> 

#include <fstream>
#include <codecvt>
#include <locale>
#include <string>
#pragma comment(lib, "WS2_32.lib")

#include "MySocket.h"

using Message = std::vector<char>; // type alias for std::vector<char>

std::ostream& operator<< (std::ostream& out, const Message& v) {
	auto iter = v.begin();
	while (iter != v.end() && *iter !=0)
	{
		std::cout << *iter++;
	}
	std::cout << std::endl;
	return out;
}

class OutputStrategy
{
public:
	virtual void display_answer(const Message& answer) = 0;
};

class OutputInFile : public OutputStrategy
{
public:
	virtual void display_answer(const Message& answer) final {
		std::ofstream fs("test_outpu.txt");
		if (!fs)
		{
			std::cerr << "Cannot open the output file." << std::endl;
		}
		else
		{
			fs << answer;
		}
	}
};

class OutputInStdout : public OutputStrategy
{
public:
	virtual void display_answer(const Message& answer) final {
		std::cout << "RESULT: " << answer;
	}
};

class OutputInMessageBox : public OutputStrategy
{
public:
	virtual void display_answer(const Message& answer) final {
		std::wstring_convert<std::codecvt_utf8<wchar_t>, wchar_t> converter;
		std::wstring wstr = converter.from_bytes(answer.data(), answer.data() + answer.size());
		MessageBoxW(HWND_DESKTOP, wstr.c_str(), L"", MB_OK | MB_ICONQUESTION);
	}
};

int main(int argc, char* argv[]) {
	// Setup utf-8 format
	SetConsoleOutputCP(CP_UTF8);
	setvbuf(stdout, nullptr, _IOFBF, 1000);
	WSADATA WSAData;
	const int wsa_startup_status_code = WSAStartup(MAKEWORD(2, 0), &WSAData);
	
	if (wsa_startup_status_code != 0) {
		std::cerr << "WSAStartup finished with not zero status code: " << wsa_startup_status_code << std::endl;
	}

	const char* IP = "127.0.0.1";
	const int PORT = 5555;

	OutputStrategy* output_object = NULL;

	auto a = argv[1];
	std::cout << a << (a == "-message_box") << strcmp(a, "-message_box")  << std::endl;

	if (argc != 1) {
		if (argv[1] == "-message_box") {
			output_object = new OutputInMessageBox();
		}
		else if (argv[1] == "-file") {
			output_object = new OutputInFile();
		}
		else
		{
			output_object = new OutputInStdout();
		}
	}
	else
	{
		output_object = new OutputInStdout();
	}


	MySocket my_socket;

	try {
		my_socket.connect_to(IP, PORT);
		std::cout << "Connected" << std::endl;
	}
	catch (std::runtime_error& ex)
	{
		std::cerr << ex.what() << std::endl;
		return -1;
	}
	catch (std::exception& ex) {
		std::cerr << "Unexpected exception" << ex.what() << std::endl;
		return -1;
	}
	const int MESSAGE_SIZE = 100;
	Message recvbuf(MESSAGE_SIZE+1);
	while(true)
	{ 
		int text_len = 0;
		std::string user_input;

		getline(std::cin, user_input);
		if (user_input == "")
			continue;
		try
		{
			text_len = my_socket.send_message(user_input.c_str(), user_input.size(), 0);
			std::cout << "Sent " << text_len << " bytes\n";
		}
		catch (const std::exception& ex)
		{
			std::cerr << ex.what() << std::endl;
		}

		//Cyrillic are encoded using 2 bytes

		try
		{
			text_len = my_socket.receive_message(recvbuf.data(), MESSAGE_SIZE, 0);
			output_object->display_answer(recvbuf);
		}
		catch (const std::exception& ex)
		{
			std::cerr << ex.what() << std::endl;
		}

		if (text_len > 0) {
			std::cout << "Recived " << text_len << " bytes\n";
			recvbuf[text_len] = 0; // END of the recived message
		}
		else if (text_len == 0) {
			std::cout << "Connection closed\n";
		}
		else {
			std::cerr << "Failed to receive\n";
		}

		std::cout << "RESULT: " << recvbuf;
	}
	WSACleanup();
}