#ifndef SDL_WIN64_DEFINES_H
#define SDL_WIN64_DEFINES_H

#ifdef _WIN32

#include <winsock2.h>
#include <ws2tcpip.h>

typedef SOCKET Socket_Handle_t;

typedef struct socket_struct_t {
    struct sockaddr_in addr_in;
    SOCKET socket_handle;
} socket_struct;

#endif //_WIN32

#endif
