#ifndef GAME_ACTION__GLOBAL_SPACE__STORE_H
#define GAME_ACTION__GLOBAL_SPACE__STORE_H

#include "defines.h"
#include "game.h"

void register_game_action__global_space__store(
        Game_Action_Logic_Table *p_game_action_logic_table);

void initialize_game_action_for__global_space__store(
        Game_Action *p_game_action,
        Global_Space_Vector__3i32 global_space_vector__3i32);

static inline
bool dispatch_game_action__global_space__store(
        Game *p_game,
        Global_Space_Vector__3i32 global_space_vector__3i32) {
    Game_Action ga_store;
    initialize_game_action_for__global_space__store(
            &ga_store,
            global_space_vector__3i32);
    return dispatch_game_action_to__server(
            p_game, 
            &ga_store);
}

#endif
