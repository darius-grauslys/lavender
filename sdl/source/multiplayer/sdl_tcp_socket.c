#include "multiplayer/sdl_tcp_socket.h"

void SDL_initialize_PLATFORM_tcp_socket(
        PLATFORM_TCP_Socket *p_PLATFORM_tcp_socket,
        u32 socket_handle) {
    p_PLATFORM_tcp_socket->socket_handle = socket_handle;
}
