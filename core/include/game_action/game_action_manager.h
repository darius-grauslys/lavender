#ifndef GAME_ACTION_MANAGER_H
#define GAME_ACTION_MANAGER_H

#include "defines.h"
#include "defines_weak.h"
#include "serialization/hashing.h"

void initialize_game_action_manager(
        Game_Action_Manager *p_game_action_manager);

Game_Action *allocate_game_action_with__this_uuid_from__game_action_manager(
        Game_Action_Manager *p_game_action_manager,
        Identifier__u32 uuid);

Game_Action *allocate_as__copy_of__game_action_with__this_uuid_from__manager(
        Game_Action_Manager *p_game_action_manager,
        Game_Action *p_game_action_to__copy,
        Identifier__u32 uuid);

bool release_game_action_from__game_action_manager(
        Game_Action_Manager *p_game_action_manager,
        Game_Action *p_game_action);

Game_Action *get_p_game_action_by__uuid_from__game_action_manager(
        Game_Action_Manager *p_game_action_manager,
        Identifier__u32 uuid);

static inline
Game_Action *allocate_game_action_from__game_action_manager(
        Game_Action_Manager *p_game_action_manager) {
    Identifier__u32 uuid =
        get_next_available__random_uuid_in__contiguous_array(
                (Serialization_Header*)p_game_action_manager
                ->game_actions, 
                MAX_QUANTITY_OF__GAME_ACTIONS, 
                &p_game_action_manager->repeatable_pseudo_random);
    return allocate_game_action_with__this_uuid_from__game_action_manager(
            p_game_action_manager, 
            uuid);
}

static inline
Game_Action *allocate_as__copy_of__game_action_from__game_action_manager(
        Game_Action_Manager *p_game_action_manager,
        Game_Action *p_game_action) {
    Identifier__u32 uuid =
        get_next_available__random_uuid_in__contiguous_array(
                (Serialization_Header*)p_game_action_manager
                ->game_actions, 
                MAX_QUANTITY_OF__GAME_ACTIONS, 
                &p_game_action_manager->repeatable_pseudo_random);
    return allocate_as__copy_of__game_action_with__this_uuid_from__manager(
            p_game_action_manager, 
            p_game_action,
            uuid);
}

#endif
