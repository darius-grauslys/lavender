#ifndef GAME_ACTION__TCP_CONNECT_H
#define GAME_ACTION__TCP_CONNECT_H

#include "defines.h"
#include "defines_weak.h"
#include "game.h"

///
/// This is invoked by the tcp_client, NOT tcp_server.
///
void register_game_action__tcp_connect(
        Game_Action_Logic_Table *p_game_action_logic_table);

void receive_game_action__connect(
        Game *p_game,
        Identifier__u64 session_token);

void initialize_game_action_for__tcp_connect(
        Game_Action *p_game_action,
        Identifier__u64 session_token);

static inline
void dispatch_game_action__connect(
        Game *p_game,
        Identifier__u64 session_token) {
    Game_Action ga_connect;
    initialize_game_action_for__tcp_connect(
            &ga_connect, 
            session_token);
    dispatch_game_action(
            p_game,
            &ga_connect);
}

#endif
