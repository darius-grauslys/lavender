#include "multiplayer/client__default.h"
#include "client.h"
#include "debug/debug.h"
#include "defines_weak.h"
#include "game.h"
#include "game_action/game_action.h"
#include "multiplayer/tcp_socket.h"
#include "multiplayer/tcp_socket_manager.h"

void m_poll_tcp_socket_manager_as__client__default(
        TCP_Socket_Manager *p_tcp_socket_manager,
        Game *p_game) {
//#ifndef IS_SERVER
#if 1
    Client *p_client =
        get_p_client_by__index_from__game(
                p_game, 
                0);
    TCP_Socket *p_tcp_socket_to__server =
        &p_tcp_socket_manager->tcp_sockets[0];

    union {
        Game_Action game_action;
        TCP_Packet tcp_packet;
    } delivery;

    switch (poll_tcp_socket_for__connection(p_tcp_socket_to__server)) {
        default:
            // wait for tcp_socket to be closed externally.
            break;
        case TCP_Socket_State__Connected:
        case TCP_Socket_State__Authenticated:
            if (!receive_bytes_over__tcp_socket(
                        p_tcp_socket_to__server)) {
                break;
            }
            get_latest__delivery_from__tcp_socket(
                    p_tcp_socket_to__server, 
                    &delivery.tcp_packet);
            delivery.game_action.uuid_of__client__u32 = 0;

            receive_game_action(
                    p_game,
                    GET_UUID_P(p_client),
                    &delivery.game_action);
            break;
    }
#endif
}
