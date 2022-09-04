#pragma once
#include <iostream> 
#include <cstdio> 
#include <winsock2.h> 

class WsaDataWrapper
{
public:
	WsaDataWrapper();
	~WsaDataWrapper();

private:
	WSADATA WSAData;
};
