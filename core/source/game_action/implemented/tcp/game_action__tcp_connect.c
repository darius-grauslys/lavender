#include "game_action/implemented/tcp/game_action__tcp_connect.h"
#include "defines.h"
#include "defines_weak.h"
#include "game.h"
#include "game_action/game_action.h"
#include "game_action/game_action_logic_entry.h"
#include "game_action/game_action_logic_table.h"
#include "game_action/implemented/tcp/game_action__tcp_connect__accept.h"
#include "game_action/implemented/tcp/game_action__tcp_connect__reject.h"
#include "multiplayer/tcp_socket.h"
#include "multiplayer/tcp_socket_manager.h"
#include "platform.h"
#include "process/game_action_process.h"
#include "process/process.h"

///
/// inbound - proccessed by server.
///
void m_process__game_action__tcp_connect__inbound(
        Process *p_this_process,
        Game *p_game) {
    // TODO: session_token authentication happens here
    Game_Action *p_game_action =
        (Game_Action*)p_this_process->p_process_data;

    IPv4_Address ipv4;
    PLATFORM_TCP_Socket *p_PLATFORM_tcp_socket =
        poll_tcp_socket_manager_for__pending_connections(
                get_p_tcp_socket_manager_from__game(p_game), 
                &get_p_tcp_socket_manager_from__game(p_game)->tcp_sockets[0], 
                &ipv4);

    if (!p_PLATFORM_tcp_socket) {
        debug_error("m_process__game_action__tcp_connect__inbound__init, p_PLATFORM_tcp_socket == 0.");
        fail_game_action_process(
                p_game, 
                p_this_process);
        return;
    }

    Identifier__u64 session_token =
        p_game_action->ga_kind__tcp_connect__session_token;

    // TODO: use authentication result to get user uuid,
    // then with user uuid determine local server uuid.

    // TODO: this is to be changed:
    Identifier__u32 uuid__u32 = session_token;

    // verify connection not already existing:
    Client *p_client =
        get_p_client_by__uuid_from__game(
                p_game, 
                uuid__u32);

    if (p_client) {
        goto reject;
    }

    TCP_Socket *p_tcp_socket =
        accept_pending_connection(
                get_p_tcp_socket_manager_from__game(p_game), 
                uuid__u32);

    if (!p_tcp_socket) {
        goto reject;
    }

    Client *p_client__new =
        allocate_client_from__game(
                p_game, 
                uuid__u32);

    if (!p_client__new) {
        goto reject;
    }

    debug_info("game_action__tcp_connect: accept");

    dispatch_game_action__connect__accept(
            p_game, 
            p_client__new);
    complete_game_action_process(
            p_game, 
            p_this_process);
    return;
reject:
    debug_info("game_action__tcp_connect: reject");

    Game_Action ga_reject;
    initialize_game_action_for__tcp_connect__reject(
            &ga_reject, 
            0);
    PLATFORM_tcp_send(
            p_PLATFORM_tcp_socket, 
            (u8*)&ga_reject, 
            sizeof(ga_reject));
    reject_pending_connection(
            get_p_tcp_socket_manager_from__game(p_game));
    fail_game_action_process(
            p_game, 
            p_this_process);
}

void register_game_action__tcp_connect(
        Game_Action_Logic_Table *p_game_action_logic_table) {
    initialize_game_action_logic_entry(
            get_p_game_action_logic_entry_by__game_action_kind(
                p_game_action_logic_table, 
                Game_Action_Kind__TCP_Connect), 
            GAME_ACTION_FLAGS__OUTBOUND_SANITIZE,
            GAME_ACTION_FLAG_MASK__OUTBOUND_SANITIZE,
            GAME_ACTION_FLAGS__INBOUND_SANITIZE
            | GAME_ACTION_FLAGS__BIT_IS_WITH_PROCESS
            | GAME_ACTION_FLAGS__BIT_IS_PROCESSED_ON_INVOCATION_OR_RESPONSE
            | GAME_ACTION_FLAGS__BIT_IS_LOCAL,
            GAME_ACTION_FLAG_MASK__INBOUND_SANITIZE,
            0,
            0,
            m_process__game_action__tcp_connect__inbound, 
            PROCESS_FLAGS__NONE);
}

void receive_game_action__connect(
        Game *p_game,
        Identifier__u64 session_token) {
    Game_Action ga_connect;
    initialize_game_action(&ga_connect);
    set_the_kind_of__game_action(
            &ga_connect, 
            Game_Action_Kind__TCP_Connect);
    ga_connect.ga_kind__tcp_connect__session_token =
        session_token;

    receive_game_action(
            p_game,
            &ga_connect);
}

void initialize_game_action_for__tcp_connect(
        Game_Action *p_game_action,
        Identifier__u64 session_token) {
    initialize_game_action(p_game_action);
    set_the_kind_of__game_action(
            p_game_action, 
            Game_Action_Kind__TCP_Connect);
    p_game_action->ga_kind__tcp_connect__session_token =
        session_token;
}
