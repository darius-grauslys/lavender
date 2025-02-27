#include "multiplayer/server__default.h"
#include "client.h"
#include "debug/debug.h"
#include "defines.h"
#include "defines_weak.h"
#include "game.h"
#include "game_action/game_action.h"
#include "multiplayer/tcp_socket.h"
#include "platform.h"
#include "platform_defaults.h"

void m_poll_tcp_socket_manager_as__server(
        TCP_Socket_Manager *p_tcp_socket_manager,
        Game *p_game) {
#ifdef IS_SERVER
    TCP_Socket *p_tcp_socket__server = 
        p_tcp_socket_manager->ptr_array_of__tcp_sockets[0];
    TCP_Socket *p_tcp_socket__auth = 
        p_tcp_socket_manager->ptr_array_of__tcp_sockets[1];

    if (!p_tcp_socket__server
            || !p_tcp_socket__auth) {
        debug_abort("m_poll_tcp_socket_manager_as__server, missing server sockets.");
    }

    PLATFORM_tcp_poll_accept(
            p_tcp_socket_manager, 
            p_tcp_socket__server, 
            p_tcp_socket__auth);

    TCP_Socket **p_ptr_tcp_socket__client =
        &p_tcp_socket_manager->ptr_array_of__tcp_sockets[1];

    while ((++p_ptr_tcp_socket__client
                - p_tcp_socket_manager->ptr_array_of__tcp_sockets
                < MAX_QUANTITY_OF__TCP_SOCKETS)
            && *p_ptr_tcp_socket__client) {
        union {
            Game_Action game_action;
            TCP_Packet tcp_packet;
        } deliver;

        Client *p_client =
            get_p_client_by__uuid_from__game(
                    p_game, 
                    (*p_ptr_tcp_socket__client)
                    ->_serialization_header.uuid);
        while (get_latest__delivery_from__tcp_socket(
                *p_ptr_tcp_socket__client, 
                &deliver.tcp_packet)) {
            set_game_action_as__deallocated(
                    &deliver.game_action);
            set_game_action_as__inbound(
                    &deliver.game_action);

            receive_game_action_for__client(
                    p_client, 
                    p_game, 
                    &deliver.game_action);
        }
    }

#endif
}
