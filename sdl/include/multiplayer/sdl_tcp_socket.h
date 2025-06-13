#ifndef SDL_TCP_SOCKET_H
#define SDL_TCP_SOCKET_H

#include "defines_weak.h"
#include "sdl_defines.h"

void SDL_initialize_PLATFORM_tcp_socket(
        PLATFORM_TCP_Socket *p_PLATFORM_tcp_socket,
        u32 socket_handle);

bool SDL_tcp_close_socket(
        SDL_Socket_Handle_t socket_handle);

///
/// Returns true if any errors occured.
///
bool SDL_tcp_open_socket(
        int domain,
        int type,
        int protocol,
        SDL_Socket_Handle_t *p_OUT_socket);

static inline
void SDL_initialize_PLATFORM_tcp_socket_as__inactive(
        PLATFORM_TCP_Socket *p_PLATFORM_tcp_socket) {
    SDL_initialize_PLATFORM_tcp_socket(
            p_PLATFORM_tcp_socket, 
            0);
}

static inline
bool SDL_is_PLATFORM_tcp_socket__in_use(
        PLATFORM_TCP_Socket *p_PLATFORM_socket) {
    return p_PLATFORM_socket->socket_handle;
}
#endif
