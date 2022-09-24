#define _WINSOCK_DEPRECATED_NO_WARNINGS
#define _CRT_SECURE_NO_WARNINGS
#pragma comment(lib, "WS2_32.lib")

#include <iostream> 
#include <cstdio> 
#include <memory>
#include <fstream>
#include <codecvt>
#include <locale>
#include <string>

#include "MySocket.h"
#include "WsaDataWrapper.h"
#include "OutputStrategies.h"

int main(int argc, char* argv[]) {
	// Setup utf-8 format
	SetConsoleOutputCP(CP_UTF8);

	std::unique_ptr<WsaDataWrapper> wsa_data;
	try
	{
		wsa_data = std::make_unique<WsaDataWrapper>();
	}
	catch (const std::exception& ex)
	{
		std::cerr << ex.what() << std::endl;
		return -1;
	}

	const char* IP = "127.0.0.1";
	const int PORT = 5555;

	std::unique_ptr<OutputStrategy> output_object;

	if (argc > 1) {
		std::string user_choise = argv[1];
		if (user_choise == "-message_box") {
			output_object = std::make_unique<OutputInMessageBox>();
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
			output_object = std::make_unique<OutputInFile>(file_path);
		}
		else
		{
			output_object = std::make_unique<OutputInStdout>();
		}
	}
	else
	{
		output_object = std::make_unique<OutputInStdout>();
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
}