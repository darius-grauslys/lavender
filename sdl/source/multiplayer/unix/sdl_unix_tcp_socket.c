#ifdef __unix__
#include "multiplayer/unix/sdl_unix_tcp_defines.h"
#include "multiplayer/sdl_tcp_defines.h"
#include "multiplayer/sdl_tcp_socket.h"
#include "debug/debug.h"

bool SDL_tcp_open_socket(
        int domain,
        int type,
        int protocol,
        SDL_Socket_Handle_t *p_OUT_socket) {
    *p_OUT_socket =
        socket(domain, type, protocol);
    return *p_OUT_socket == (u32)-1;
}

bool SDL_tcp_close_socket(
        SDL_Socket_Handle_t socket_handle) {
    if (close(socket_handle)) {
        debug_error("SDL::UNIX::SDL_tcp_close_socket, failed to close socket.");
        return true;
    }
    return false;
}

bool PLATFORM_tcp_close_socket(
        PLATFORM_TCP_Context *p_PLATFORM_tcp_context,
        PLATFORM_TCP_Socket *p_PLATFORM_tcp_socket) {
    if (SDL_tcp_close_socket(p_PLATFORM_tcp_socket->socket_handle)) {
        debug_error("SDL::UNIX::PLATFORM_tcp_close_socket, failed to close socket.");
        return true;
    }
    SDL_initialize_PLATFORM_tcp_socket_as__inactive(
            p_PLATFORM_tcp_socket);

    return false;
}

#endif
