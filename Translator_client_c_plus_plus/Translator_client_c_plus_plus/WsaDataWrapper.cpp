#define _WINSOCK_DEPRECATED_NO_WARNINGS
#include "WsaDataWrapper.h"


WsaDataWrapper::WsaDataWrapper()
{
	const int wsa_startup_status_code = WSAStartup(MAKEWORD(2, 0), &WSAData);

	if (wsa_startup_status_code != 0) {
		std::cerr << "WSAStartup finished with not zero status code: " << wsa_startup_status_code << std::endl;
	}
}

WsaDataWrapper::~WsaDataWrapper()
{
	WSACleanup();
}