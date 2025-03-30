#include "game_action/implemented/tcp/game_action__tcp_begin_connect.h"
#include "defines.h"
#include "defines_weak.h"
#include "game.h"
#include "game_action/game_action.h"
#include "game_action/game_action_logic_entry.h"
#include "game_action/game_action_logic_table.h"
#include "multiplayer/tcp_socket.h"
#include "multiplayer/tcp_socket_manager.h"
#include "process/process.h"
#include "serialization/serialization_header.h"
#include "game_action/implemented/tcp/game_action__tcp_connect.h"

void m_process__game_action__tcp_connect__begin(
        Process *p_this_process,
        Game *p_game) {
    /// p_process_data is now the tcp_socket

    TCP_Socket *p_tcp_socket =
        (TCP_Socket*)p_this_process->p_process_data;
    switch (get_state_of__tcp_socket(p_tcp_socket)) {
        default:
            break;
        case TCP_Socket_State__Authenticated:
            debug_info("m_process__game_action__tcp_connect__begin: authenticated!!!"); 
            set_tcp_socket_as__automatically_driven(p_tcp_socket);
            complete_process(p_this_process);
            break;
        case TCP_Socket_State__Authenticating:
            debug_info("m_process__game_action__tcp_connect__begin: authenticating...");
            if (!receive_bytes_over__tcp_socket(
                        p_tcp_socket)) {
                break;
            }
            // TODO: timeout on silence or non-sense packets
            TCP_DELIVERY(Game_Action, ga_response) delivery;

            get_latest__delivery_from__tcp_socket(
                    p_tcp_socket, 
                    &delivery.tcp_packet);
            switch (get_kind_of__game_action(&delivery.ga_response)) {
                default:
                    break;
                case Game_Action_Kind__TCP_Connect__Reject:
                    debug_error("m_process__game_action__tcp_connect__begin: failed to connect. (reject)");
                    close_socket_on__tcp_socket_manager__ipv4(
                            get_p_tcp_socket_manager_from__game(p_game), 
                            p_tcp_socket);
                    fail_process(p_this_process);
                    break;
                case Game_Action_Kind__TCP_Connect__Accept:
                    debug_info("m_process__game_action__tcp_connect__begin: connected."); 
                    set_state_of__tcp_socket(
                            p_tcp_socket, 
                            TCP_Socket_State__Authenticated);
                    set_tcp_socket_as__automatically_driven(p_tcp_socket);
                    complete_process(p_this_process);
                    break;
            }
            break;
        case TCP_Socket_State__Connected:
            debug_info("m_process__game_action__tcp_connect__begin: connecting...");
            dispatch_game_action__connect(
                    p_game, 
                    123); // TODO: give session_token
            set_state_of__tcp_socket(
                    p_tcp_socket, 
                    TCP_Socket_State__Authenticating);
            break;
        case TCP_Socket_State__Disconnected:
        case TCP_Socket_State__Unknown:
            debug_error("m_process__game_action__tcp_connect__begin: failed to connect. (bad state)");
            close_socket_on__tcp_socket_manager__ipv4(
                    get_p_tcp_socket_manager_from__game(p_game), 
                    p_tcp_socket);
            fail_process(p_this_process);
            break;
    }
}

void m_process__game_action__tcp_connect__begin__init(
        Process *p_this_process,
        Game *p_game) {
    Client *p_client =
        get_p_client_by__index_from__game(
                p_game, 
                0);
    Game_Action *p_game_action =
        (Game_Action*)p_this_process->p_process_data;
    TCP_Socket *p_tcp_socket =
        open_socket_on__tcp_socket_manager__ipv4(
                get_p_tcp_socket_manager_from__game(p_game), 
                p_game_action
                ->ga_kind__tcp_connect__begin__ipv4_address, 
                GET_UUID_P(p_client));
    p_this_process->p_process_data =
        p_tcp_socket;

    set_tcp_socket_as__manually_driven(p_tcp_socket);

    p_this_process->m_process_run__handler =
        m_process__game_action__tcp_connect__begin;
}

void register_game_action__tcp_connect__begin(
        Game_Action_Logic_Table *p_game_action_logic_table) {
    initialize_game_action_logic_entry(
            get_p_game_action_logic_entry_by__game_action_kind(
                p_game_action_logic_table, 
                Game_Action_Kind__TCP_Connect__Begin), 
            GAME_ACTION_FLAGS__OUTBOUND_SANITIZE
            | GAME_ACTION_FLAGS__BIT_IS_WITH_PROCESS
            | GAME_ACTION_FLAGS__BIT_IS_PROCESSED_ON_INVOCATION_OR_RESPONSE
            | GAME_ACTION_FLAGS__BIT_IS_LOCAL,
            GAME_ACTION_FLAG_MASK__OUTBOUND_SANITIZE,
            GAME_ACTION_FLAGS__INBOUND_SANITIZE,
            GAME_ACTION_FLAG_MASK__INBOUND_SANITIZE,
            m_process__game_action__tcp_connect__begin__init, 
            PROCESS_FLAGS__NONE,
            0,
            0);
}

void initialize_game_action_for__tcp_connect__begin(
        Game_Action *p_game_action,
        IPv4_Address ipv4_address) {
    initialize_game_action(p_game_action);
    set_the_kind_of__game_action(
            p_game_action, 
            Game_Action_Kind__TCP_Connect__Begin);
    p_game_action->ga_kind__tcp_connect__begin__ipv4_address =
        ipv4_address;
}
