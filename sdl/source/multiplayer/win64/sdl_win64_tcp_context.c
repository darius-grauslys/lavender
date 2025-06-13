#ifdef _WIN32
#include "multiplayer/sdl_tcp_context.h"
#include "game.h"
#include <winsock2.h>
#include <ws2tcpip.h>

WSADATA __SDL_wsa_data;

PLATFORM_TCP_Context *PLATFORM_tcp_begin(
        Game *p_game) {
    if (!WSAStartup(MAKEWORD(2,2), &__SDL_wsa_data)) {
        debug_error("SDL::WIN32::PLATFORM_tcp_begin, failed on WSAStartup.");
        return 0;
    }
    PLATFORM_TCP_Context *pM_PLATFORM_tcp_context =
        malloc(sizeof(PLATFORM_TCP_Context));
    if (!pM_PLATFORM_tcp_context) {
        debug_error("SDL::PLATFORM_tcp_being, failed to allocate pM_PLATFORM_tcp_context.");
        return 0;
    }
    SDL_initialize_PLATFORM_tcp_context(
            pM_PLATFORM_tcp_context);

    return pM_PLATFORM_tcp_context;
}

void PLATFORM_tcp_end(
        Game *p_game) {
    if (!p_game->pM_tcp_socket_manager)
        return;

    WSACleanup();

    PLATFORM_TCP_Context *p_PLATFORM_tcp_context =
        get_p_PLATFORM_tcp_context_from__game(p_game);

    p_game->pM_tcp_socket_manager->p_PLATFORM_tcp_context = 0;

    free(p_PLATFORM_tcp_context);
}

#endif //_WIN32
