#ifndef GAME_ACTION__TCP_CONNECT__BEGIN_H
#define GAME_ACTION__TCP_CONNECT__BEGIN_H

#include "defines.h"
#include "defines_weak.h"
#include "game_action/game_action.h"
#include <sys/types.h>

///
/// This is invoked by the tcp_client, NOT tcp_server.
///
void register_game_action__tcp_connect__begin(
        Game_Action_Logic_Table *p_game_action_logic_table);

void initialize_game_action_for__tcp_connect__begin(
        Game_Action *p_game_action,
        IPv4_Address ipv4_address,
        Session_Token session_token);

static inline
void dispatch_game_action__connect__begin(
        Game *p_game,
        IPv4_Address ipv4_address,
        Session_Token session_token) {
    Game_Action ga_connect__begin;
    initialize_game_action_for__tcp_connect__begin(
            &ga_connect__begin,
            ipv4_address,
            session_token);
    dispatch_game_action(
            p_game, 
            0, // TODO: this may be incorrect to do
               // however, we don't know what uuid the server will
               // determine for us. Ultimately this likely doesn't matter.
            &ga_connect__begin);
}

#endif
