#include "game_action/game_action_manager.h"
#include "defines.h"
#include "defines_weak.h"
#include "game_action/game_action.h"
#include "numerics.h"
#include "random.h"
#include "serialization/hashing.h"
#include "serialization/identifiers.h"
#include "serialization/serialization_header.h"
#include "util/bitmap/bitmap.h"

static inline
Game_Action *get_p_game_action_by__index_from__game_action_manager(
        Game_Action_Manager *p_game_action_manager,
        Index__u32 index_of__game_action) {
    return &p_game_action_manager->game_actions[
        index_of__game_action];
}

void initialize_game_action_manager(
        Game_Action_Manager *p_game_action_manager) {
    initialize_serialization_header__contiguous_array(
            (Serialization_Header*)p_game_action_manager->game_actions, 
            MAX_QUANTITY_OF__GAME_ACTIONS, 
            sizeof(Game_Action));
    initialize_repeatable_psuedo_random(
            &p_game_action_manager->repeatable_pseudo_random, 
            (u32)(uint64_t)p_game_action_manager);
}

Game_Action *allocate_game_action_with__this_uuid_from__game_action_manager(
        Game_Action_Manager *p_game_action_manager,
        Identifier__u32 uuid) {
    if (is_identifier_u32__invalid(uuid)) {
        debug_warning("allocate_game_action_from__game_action_manager, invalid uuid. New uuid assigned.");
        uuid =
            get_next_available__random_uuid_in__contiguous_array(
                    (Serialization_Header*)p_game_action_manager
                    ->game_actions, 
                    MAX_QUANTITY_OF__GAME_ACTIONS, 
                    &p_game_action_manager->repeatable_pseudo_random);
    }

    Game_Action *p_game_action =
        (Game_Action*)dehash_identitier_u32_in__contigious_array(
                (Serialization_Header*)p_game_action_manager
                    ->game_actions, 
                MAX_QUANTITY_OF__GAME_ACTIONS, 
                uuid);
    if (!IS_DEALLOCATED_P(p_game_action)) {
        debug_error("allocate_game_action_from__game_action_manager, uuid already in use.");
        return 0;
    }
    initialize_game_action(p_game_action);
    initialize_serialization_header(
            &p_game_action->_serialiation_header, 
            uuid, 
            sizeof(Game_Action));
    set_game_action_as__allocated(p_game_action);

    return p_game_action;
}

bool release_game_action_from__game_action_manager(
        Game_Action_Manager *p_game_action_manager,
        Game_Action *p_game_action) {
#ifndef NDEBUG
    u32 index =  
        p_game_action
        - p_game_action_manager->game_actions
        ;
    if (index >= MAX_QUANTITY_OF__GAME_ACTIONS) {
        debug_error("release_game_action_from__game_action_manager, p_game_action was not allocated with this manager.");
        return false;
    }
#endif

    initialize_game_action(p_game_action);
    return true;
}

Game_Action *get_p_game_action_by__uuid_from__game_action_manager(
        Game_Action_Manager *p_game_action_manager,
        Identifier__u32 uuid) {
    Game_Action *p_game_action__responded_to =
        (Game_Action*)dehash_identitier_u32_in__contigious_array(
                (Serialization_Header*)
                p_game_action_manager->game_actions, 
                MAX_QUANTITY_OF__GAME_ACTIONS, 
                uuid);

    if (!p_game_action__responded_to
            || is_serialized_struct__deallocated(
                (Serialization_Header*)p_game_action__responded_to)) {
        return 0;
    }

    return p_game_action__responded_to;
}
