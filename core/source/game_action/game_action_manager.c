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
    Game_Action *p_game_action =
        (Game_Action*)allocate_serialization_header_with__this_uuid(
                (Serialization_Header*)p_game_action_manager->game_actions, 
                MAX_QUANTITY_OF__GAME_ACTIONS, 
                BRAND_UUID(
                    uuid, 
                    GET_UUID_BRANDING(
                        Lavender_Type__Game_Action, 
                        0)));

    if (!p_game_action) {
        debug_error("allocate_game_action_from__game_action_manager, failed to allocate game action.");
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

Game_Action *allocate_as__copy_of__game_action_with__this_uuid_from__manager(
        Game_Action_Manager *p_game_action_manager,
        Game_Action *p_game_action_to__copy,
        Identifier__u32 uuid) {
    Game_Action *p_game_action =
        allocate_game_action_with__this_uuid_from__game_action_manager(
                p_game_action_manager, 
                uuid);
    if (!p_game_action) {
        debug_error("allocate_as__copy_of__game_action_with__this_uuid_from__manager, p_game_action == 0.");
        return 0;
    }
    initialize_serialization_header(
            &p_game_action->_serialiation_header, 
            uuid, 
            sizeof(Game_Action));
    memcpy(
            ((u8*)p_game_action) + sizeof(Serialization_Header),
            ((u8*)p_game_action_to__copy) + sizeof(Serialization_Header),
            sizeof(Game_Action) - sizeof(Serialization_Header));
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

    initialize_serialization_header_for__deallocated_struct(
            (Serialization_Header*)p_game_action, 
            sizeof(Game_Action));
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
