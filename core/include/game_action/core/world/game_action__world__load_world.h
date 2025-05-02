#ifndef GAME_ACTION__WORLD__LOAD_WORLD_H
#define GAME_ACTION__WORLD__LOAD_WORLD_H

#include "defines.h"
#include "defines_weak.h"
#include "game.h"

void register_game_action__world__load_world(
        Game_Action_Logic_Table *p_game_action_logic_table);

void initialize_game_action_for__world__load_world(
        Game_Action *p_game_action,
        Identifier__u32 uuid_of__client__u32);

static inline
bool dispatch_game_action__world__load_world(
        Game *p_game,
        Identifier__u32 uuid_of__client__u32) {
    Game_Action ga_resolve;
    initialize_game_action_for__world__load_world(
            &ga_resolve,
            uuid_of__client__u32);
    return dispatch_game_action_to__server(
            p_game, 
            &ga_resolve);
}

#endif
