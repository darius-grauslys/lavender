#ifdef _WIN32

#include "debug/debug.h"
#include "multiplayer/sdl_tcp_defines.h"
#include "multiplayer/sdl_tcp_socket.h"

bool SDL_tcp_open_socket(
        int domain,
        int type,
        int protocol,
        SDL_Socket_Handle_t *p_OUT_socket) {
    *p_OUT_socket =
        socket(domain, type, protocol);
    return *p_OUT_socket == INVALID_SOCKET;
}

bool SDL_tcp_close_socket(
        Socket_Handle_t socket_handle) {
    if (closesocket(socket_handle)) {
        debug_error("SDL::WIN64::SDL_tcp_close_socket, failed to close socket.");
        return true;
    }
    return false;
}

bool PLATFORM_tcp_close_socket(
        PLATFORM_TCP_Context *p_PLATFORM_tcp_context,
        PLATFORM_TCP_Socket *p_PLATFORM_tcp_socket) {
    if (SDL_tcp_close_socket(p_PLATFORM_tcp_socket->socket_handle)) {
        debug_error("SDL::WIN64::SDL_tcp_close_socket, failed to close socket.");
        return true;
    }
    SDL_initialize_PLATFORM_tcp_socket_as__inactive(
            p_PLATFORM_tcp_socket);

    return false;
}

#endif
