#define _WINSOCK_DEPRECATED_NO_WARNINGS
#include "WsaDataWrapper.h"
#include <string> 
#include <iostream> 

WsaDataWrapper::WsaDataWrapper()
{
    const int wsa_startup_status_code = WSAStartup(MAKEWORD(2, 0), &WSAData);

	if (wsa_startup_status_code != 0) {
        std::unique_ptr<LPSTR> messageBuffer = std::make_unique<LPSTR>();

        //Ask Win32 to give us the string version of that wsa_startup_status_code.
        //The parameters we pass in, tell Win32 to create the buffer that holds the message for us (because we don't yet know how long the message string will be).
        FormatMessageA(FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM | FORMAT_MESSAGE_IGNORE_INSERTS,
            NULL, wsa_startup_status_code, MAKELANGID(LANG_ENGLISH, SUBLANG_ENGLISH_US), (LPSTR)messageBuffer.get(), 0, NULL);
		throw std::runtime_error(*messageBuffer.get());
	}
}

WsaDataWrapper::~WsaDataWrapper()
{
	WSACleanup();
}