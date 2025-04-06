#ifndef GAME_ACTION__BAD_REQUEST_H
#define GAME_ACTION__BAD_REQUEST_H

#include "defines.h"
#include "game.h"
#include "game_action/game_action.h"
#include "serialization/serialization_header.h"

void register_game_action__bad_request(
        Game_Action_Logic_Table *p_game_action_logic_table);

void initialize_game_action_for__bad_request(
        Game_Action *p_game_action,
        Game_Action *p_game_action__responding_to,
        u32 bad_request__code__u32);

static inline
bool dispatch_game_action__bad_request(
        Game *p_game,
        Game_Action *p_game_action,
        u32 bad_request__code__u32) {
    Game_Action ga_bad_request;
    initialize_game_action_for__bad_request(
            &ga_bad_request,
            p_game_action,
            bad_request__code__u32);
    return dispatch_game_action(
            p_game, 
            get_client_uuid_from__game_action(p_game_action),
            &ga_bad_request);
}

#endif
