#include "multiplayer/server__default.h"
#include "client.h"
#include "debug/debug.h"
#include "defines.h"
#include "defines_weak.h"
#include "game.h"
#include "game_action/game_action.h"
#include "multiplayer/tcp_socket.h"
#include "multiplayer/tcp_socket_manager.h"
#include "platform.h"
#include "platform_defaults.h"

void accept_connection__server__default(
        Game *p_game,
        PLATFORM_TCP_Socket *p_PLATFORM_tcp_socket,
        IPv4_Address *p_ipv4,
        Identifier__u32 uuid) {
    TCP_Socket_Manager *p_tcp_socket_manager =
        get_p_tcp_socket_manager_from__game(p_game);

    TCP_Socket *p_tcp_socket =
        accept_socket_on__tcp_socket_manager__ipv4(
                p_tcp_socket_manager, 
                p_PLATFORM_tcp_socket,
                *p_ipv4,
                uuid);

    Game_Action ga_accept;
    initialize_game_action(&ga_accept);
    ga_accept.the_kind_of_game_action__this_action_is =
        Game_Action_Kind__TCP_Connect__Accept;

    debug_info("connection accepted: %d.%d.%d.%d:%hu",
            p_ipv4->ip_bytes[0],
            p_ipv4->ip_bytes[1],
            p_ipv4->ip_bytes[2],
            p_ipv4->ip_bytes[3],
            p_ipv4->port
            );

    send_bytes_over__tcp_socket(
            p_tcp_socket, 
            (u8*)&ga_accept, 
            sizeof(ga_accept));
}

void reject_connection__server__default(
        Game *p_game,
        PLATFORM_TCP_Socket *p_PLATFORM_tcp_socket,
        IPv4_Address *p_ipv4) {
    TCP_Socket_Manager *p_tcp_socket_manager =
        get_p_tcp_socket_manager_from__game(p_game);

    Game_Action ga_reject;
    initialize_game_action(&ga_reject);
    ga_reject.the_kind_of_game_action__this_action_is =
        Game_Action_Kind__TCP_Connect__Reject;

    PLATFORM_tcp_send(
            p_PLATFORM_tcp_socket, 
            (u8*)&ga_reject, 
            sizeof(ga_reject));

    debug_info("connection rejected: %d.%d.%d.%d:%hu",
            p_ipv4->ip_bytes[0],
            p_ipv4->ip_bytes[1],
            p_ipv4->ip_bytes[2],
            p_ipv4->ip_bytes[3],
            p_ipv4->port
            );

    reject_pending_connection(p_tcp_socket_manager);
}

void handle_connection__server__default(
        Game *p_game,
        PLATFORM_TCP_Socket *p_PLATFORM_tcp_socket,
        IPv4_Address *p_ipv4) {
    PLATFORM_TCP_Context *p_PLATFORM_tcp_context =
        get_p_PLATFORM_tcp_context_from__game(p_game);
    TCP_Socket_Manager *p_tcp_socket_manager =
        get_p_tcp_socket_manager_from__game(p_game);

    union {
        Game_Action game_action;
        TCP_Packet tcp_packet;
    } delivery;

    i32 quantity_received =
        PLATFORM_tcp_recieve(
                p_PLATFORM_tcp_socket, 
                delivery.tcp_packet.tcp_packet_bytes, 
                MAX_SIZE_OF__TCP_PACKET);

    switch (quantity_received) {
        case TCP_ERROR__DESTINATION_OVERFLOW:
            reject_connection__server__default(
                    p_game, 
                    p_PLATFORM_tcp_socket, 
                    p_ipv4);
            return;
        default:
            break;
    }

    switch (get_kind_of__game_action(&delivery.game_action)) {
        case Game_Action_Kind__TCP_Connect:
            break;
        default:
            reject_connection__server__default(
                    p_game, 
                    p_PLATFORM_tcp_socket, 
                    p_ipv4);
            return;
    }

    // check if player is already connected.
    // TODO: use uuid_64
    TCP_Socket *p_tcp_socket =
        get_p_tcp_socket_for__this_uuid(
                p_tcp_socket_manager, 
                delivery.game_action.ga_kind__tcp_connect__uuid);

    if (p_tcp_socket) {
        reject_connection__server__default(
                p_game, 
                p_PLATFORM_tcp_socket, 
                p_ipv4);
        return;
    }

    accept_connection__server__default(
            p_game, 
            p_PLATFORM_tcp_socket, 
            p_ipv4, 
            delivery.game_action.ga_kind__tcp_connect__uuid);
}

void m_poll_tcp_socket_manager_as__server__default(
        TCP_Socket_Manager *p_tcp_socket_manager,
        Game *p_game) {
#ifdef IS_SERVER
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
        handle_connection__server__default(
                p_game, 
                p_PLATFORM_tcp_socket,
                &ipv4);
    }

    TCP_Socket **p_ptr_tcp_socket__client =
        &p_tcp_socket_manager->ptr_array_of__tcp_sockets[1];

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
            receive_game_action(
                    p_game,
                    &delivery.game_action);
        }
    }

#endif
}
