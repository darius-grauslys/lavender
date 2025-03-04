#ifndef GAME_ACTION__GLOBAL_SPACE__REQUEST_H
#define GAME_ACTION__GLOBAL_SPACE__REQUEST_H

#include "defines.h"
#include "game.h"

void register_game_action__global_space__request_for__client(
        Game_Action_Logic_Table *p_game_action_logic_table);

void register_game_action__global_space__request_for__server(
        Game_Action_Logic_Table *p_game_action_logic_table);

void register_game_action__global_space__request_for__offline(
        Game_Action_Logic_Table *p_game_action_logic_table);

void initialize_game_action_for__global_space__request(
        Game_Action *p_game_action,
        Global_Space_Vector__3i32 global_space_vector__3i32);

static inline
void dispatch_game_action__global_space__request(
        Game *p_game,
        Global_Space_Vector__3i32 global_space_vector__3i32) {
    Game_Action ga_request;
    initialize_game_action_for__global_space__request(
            &ga_request,
            global_space_vector__3i32);
    dispatch_game_action(
            p_game, 
            &ga_request);
}

#endif
