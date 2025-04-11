#ifndef GAME_ACTION__TCP_CONNECT__ACCEPT_H
#define GAME_ACTION__TCP_CONNECT__ACCEPT_H

#include "defines.h"
#include "defines_weak.h"
#include "game.h"

///
/// This is invoked by the tcp_server, NOT tcp_client.
///
void register_game_action__tcp_connect__accept(
        Game_Action_Logic_Table *p_game_action_logic_table);

void initialize_game_action_for__tcp_connect__accept(
        Game_Action *p_game_action,
        Client *p_client);

static inline
void dispatch_game_action__connect__accept(
        Game *p_game,
        Client *p_client) {
    Game_Action ga_accept;
    initialize_game_action_for__tcp_connect__accept(
            &ga_accept,
            p_client);
    dispatch_game_action(
            p_game,
            GET_UUID_P(p_client),
            &ga_accept);
}

#endif
