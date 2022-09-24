#pragma once
#include <winsock2.h> 

class WsaDataWrapper
{
public:
	WsaDataWrapper();
	~WsaDataWrapper();

private:
	WSADATA WSAData;
};
