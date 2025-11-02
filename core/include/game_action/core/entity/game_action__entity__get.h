#ifndef GAME_ACTION__ENTITY__GET_H
#define GAME_ACTION__ENTITY__GET_H

#include "defines.h"
#include "game.h"

void register_game_action__entity__get_for__server(
        Game_Action_Logic_Table *p_game_action_logic_table);

void register_game_action__entity__get_for__client(
        Game_Action_Logic_Table *p_game_action_logic_table);

void initialize_game_action_for__entity__get(
        Game_Action *p_game_action,
        Identifier__u32 uuid_of__target__u32);

static inline
bool dispatch_game_action__entity__get(
        Game *p_game,
        Identifier__u32 uuid_of__target__u32) {
    Game_Action ga_resolve;
    initialize_game_action_for__entity__get(
            &ga_resolve,
            uuid_of__target__u32);
    return dispatch_game_action_to__server(
            p_game, 
            &ga_resolve);
}

#endif
