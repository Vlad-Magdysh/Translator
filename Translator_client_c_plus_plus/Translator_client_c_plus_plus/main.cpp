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
		out << *iter++;
	}
	return out;
}

class OutputStrategy
{
public:
	virtual void display_answer(const Message& answer, const size_t answer_size) = 0;
};

class OutputInFile : public OutputStrategy
{
private:
	std::string file_destination;

public:
	OutputInFile(const std::string& dest) {
		file_destination = dest;
	}
	virtual void display_answer(const Message& answer, const size_t answer_size) final {
		std::ofstream fs(file_destination, std::ios::app);
		if (!fs)
		{
			std::cerr << "Cannot open the output file." << std::endl;
		}
		else
		{
			fs << answer << "\n";
		}
	}
};

class OutputInStdout : public OutputStrategy
{
public:
	virtual void display_answer(const Message& answer, const size_t answer_size) final {
		std::cout << "RESULT: " << answer;
	}
};

class OutputInMessageBox : public OutputStrategy
{
public:
	virtual void display_answer(const Message& answer, const size_t answer_size ) final {
		std::wstring_convert<std::codecvt_utf8<wchar_t>, wchar_t> converter;
		std::wstring wstr = converter.from_bytes(answer.data(), answer.data() + answer_size);
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


	if (argc > 1) {
		std::string user_choise = argv[1];
		if (user_choise == "-message_box") {
			output_object = new OutputInMessageBox();
		}
		else if (user_choise == "-file") {
			std::string file_path;
			if (argc > 2)
			{
				file_path = argv[2];
			}
			else {
				file_path = argv[0];
				file_path.erase(file_path.find_last_of('\\') + 1);
				file_path += "default_file.txt";
			}
			output_object = new OutputInFile(file_path);
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

	std::cout << "Client is running with configured" << typeid(output_object).name() << std::endl;

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
		output_object->display_answer(recvbuf, text_len);
	}
	WSACleanup();
}