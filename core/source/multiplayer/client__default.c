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

    switch (get_state_of__tcp_socket(p_tcp_socket_to__server)) {
        case TCP_Socket_State__None:
            ;
            Game_Action connect;
            initialize_game_action(&connect);
            set_game_action_as__outbound(&connect);
            connect.the_kind_of_game_action__this_action_is =
                Game_Action_Kind__TCP_Connect;

            connect.ga_kind__tcp_connect__uuid = 123;

            dispatch_game_action_for__client(
                    get_p_client_by__index_from__game(
                        p_game, 
                        0), 
                    p_game, 
                    p_tcp_socket_manager,
                    &connect);
            debug_info("client: request connect");
            set_state_of__tcp_socket(
                    p_tcp_socket_to__server, 
                    TCP_Socket_State__Connecting);
            break;
        case TCP_Socket_State__Connecting:
            if (!receive_bytes_over__tcp_socket(
                        p_tcp_socket_to__server)) {
                break;
            }
            get_latest__delivery_from__tcp_socket(
                    p_tcp_socket_to__server, 
                    &delivery.tcp_packet);
            switch (get_kind_of__game_action(
                        &delivery.game_action)) {
                default:
                    // TODO: timeout on non-sense
                    break;
                case Game_Action_Kind__TCP_Connect__Accept:
                    debug_info("client: connection accepted");
                    set_state_of__tcp_socket(
                            p_tcp_socket_to__server, 
                            TCP_Socket_State__Connected);
                    break;
                case Game_Action_Kind__TCP_Connect__Reject:
                    debug_info("client: connection rejected");
                    set_state_of__tcp_socket(
                            p_tcp_socket_to__server, 
                            TCP_Socket_State__Disconnected);
                    break;
            }
            break;
        case TCP_Socket_State__Disconnected:
            close_socket_on__tcp_socket_manager__ipv4(
                    p_tcp_socket_manager, 
                    p_tcp_socket_to__server);
            break;
        default:
            if (!receive_bytes_over__tcp_socket(
                        p_tcp_socket_to__server)) {
                break;
            }
            get_latest__delivery_from__tcp_socket(
                    p_tcp_socket_to__server, 
                    &delivery.tcp_packet);

            receive_game_action(
                    p_game,
                    &delivery.game_action);
            break;
    }
#endif
}
