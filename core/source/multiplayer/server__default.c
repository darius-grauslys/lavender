#include "multiplayer/server__default.h"
#include "client.h"
#include "debug/debug.h"
#include "defines.h"
#include "defines_weak.h"
#include "game.h"
#include "game_action/game_action.h"
#include "game_action/implemented/tcp/game_action__tcp_connect.h"
#include "multiplayer/tcp_socket.h"
#include "multiplayer/tcp_socket_manager.h"
#include "platform.h"
#include "platform_defaults.h"

void handle_pending_connection(
        Game *p_game,
        PLATFORM_TCP_Socket *p_PLATFORM_tcp_socket) {
    TCP_DELIVERY(Game_Action, ga_connect) delivery;
    i32 quantity_received = 0;
    if (p_PLATFORM_tcp_socket) {
        quantity_received = 
            PLATFORM_tcp_recieve(
                p_PLATFORM_tcp_socket, 
                (u8*)&delivery, 
                sizeof(delivery));
    }

    if (!quantity_received) {
        return;
    }

    switch (get_kind_of__game_action(&delivery.ga_connect)) {
        default:
            // TODO: timeout
            break;
        case Game_Action_Kind__TCP_Connect:
            receive_game_action__connect(
                    p_game, 
                    delivery
                    .ga_connect
                    .ga_kind__tcp_connect__session_token);
            break;
    }
}

void m_poll_tcp_socket_manager_as__server__default(
        TCP_Socket_Manager *p_tcp_socket_manager,
        Game *p_game) {
// #ifdef IS_SERVER
#if 1
    TCP_Socket *p_tcp_socket__server = 
        p_tcp_socket_manager->ptr_array_of__tcp_sockets[0];
    TCP_Socket *p_tcp_socket__auth = 
        p_tcp_socket_manager->ptr_array_of__tcp_sockets[1];

#ifndef NDEBUG
    if (!p_tcp_socket__server
            ){ //|| !p_tcp_socket__auth) {
        debug_abort("m_poll_tcp_socket_manager_as__server, missing server sockets.");
        return;
    }
#endif

    IPv4_Address ipv4;
    PLATFORM_TCP_Socket *p_PLATFORM_tcp_socket =
        poll_tcp_socket_manager_for__pending_connections(
                p_tcp_socket_manager, 
                p_tcp_socket__server,
                &ipv4);

    if (p_PLATFORM_tcp_socket) {
        handle_pending_connection(
                p_game, 
                p_PLATFORM_tcp_socket);
    }

    TCP_Socket **p_ptr_tcp_socket__client =
        p_tcp_socket_manager->ptr_array_of__tcp_sockets;

    while ((++p_ptr_tcp_socket__client
                - p_tcp_socket_manager->ptr_array_of__tcp_sockets
                < MAX_QUANTITY_OF__TCP_SOCKETS)
            && *p_ptr_tcp_socket__client) {
        TCP_Socket *p_tcp_socket__client =
            *p_ptr_tcp_socket__client;
            
        union {
            Game_Action game_action;
            TCP_Packet tcp_packet;
        } deliver;

        Client *p_client =
            get_p_client_by__uuid_from__game(
                    p_game, 
                    p_tcp_socket__client
                    ->_serialization_header.uuid);

        if (!receive_bytes_over__tcp_socket(
                    p_tcp_socket__client)) {
            continue;
        }

        while (get_latest__delivery_from__tcp_socket(
                p_tcp_socket__client, 
                &deliver.tcp_packet)) {
            deliver.game_action.uuid_of__client__u32 =
                GET_UUID_P(p_tcp_socket__client);
            receive_game_action(
                    p_game,
                    GET_UUID_P(p_client),
                    &deliver.game_action);
        }
    }

#endif
}
