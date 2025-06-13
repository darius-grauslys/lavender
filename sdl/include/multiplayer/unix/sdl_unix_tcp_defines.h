#ifndef SDL_UNIX_TCP_DEFINES_H
#define SDL_UNIX_TCP_DEFINES_H

#ifdef __unix__

#include "defines_weak.h"

#include <netinet/in.h>
#include <unistd.h>

typedef u32 SDL_Socket_Handle_t;

typedef struct PLATFORM_TCP_Socket_t {
    struct sockaddr_in addr_in;
    u32 socket_handle;
} PLATFORM_TCP_Socket;

#endif //__unix__

#endif
