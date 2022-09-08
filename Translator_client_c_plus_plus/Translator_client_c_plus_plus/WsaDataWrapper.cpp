#define _WINSOCK_DEPRECATED_NO_WARNINGS
#include "WsaDataWrapper.h"
#include <string> 
#include <iostream> 
#include <cstdio> 
WsaDataWrapper::WsaDataWrapper()
{
	const int wsa_startup_status_code = WSAStartup(MAKEWORD(2, 0), &WSAData);

	if (wsa_startup_status_code != 0) {
		std::string error_message = "WSAStartup finished with not zero status code: " + std::to_string(wsa_startup_status_code);
		throw std::exception(error_message.c_str());
	}
}

WsaDataWrapper::~WsaDataWrapper()
{
	WSACleanup();
}