#ifndef GAME_ACTION_MANAGER_H
#define GAME_ACTION_MANAGER_H

#include "defines.h"
#include "defines_weak.h"

void initialize_game_action_manager(
        Game_Action_Manager *p_game_action_manager);

Game_Action *allocate_game_action_from__game_action_manager(
        Game_Action_Manager *p_game_action_manager);

void release_game_action_from__game_action_manager(
        Game_Action_Manager *p_game_action_manager,
        Game_Action *p_game_action);

#endif
