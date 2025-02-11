#include "game_action/game_action_manager.h"
#include "defines.h"
#include "defines_weak.h"
#include "game_action/game_action.h"
#include "numerics.h"
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
    memset(p_game_action_manager,
            0,
            sizeof(Game_Action_Manager));
    initialize_bitmap(
            p_game_action_manager
                ->bitmap_and_heap_of__deallocated_game_actions, 
            true, 
            MAX_QUANTITY_OF__GAME_ACTIONS);
}

Game_Action *allocate_game_action_from__game_action_manager(
        Game_Action_Manager *p_game_action_manager) {
    Index__u32 index_of__deallocated_game_action =
        get_index_of__first_set_bit_from__bitmap_and_heap(
                p_game_action_manager
                    ->bitmap_and_heap_of__deallocated_game_actions, 
                MAX_QUANTITY_OF__GAME_ACTIONS);

    if (is_index_u32__out_of_bounds(
                index_of__deallocated_game_action)) {
        debug_error("allocate_game_action_from__game_action_manager, failed to allocate game_action.");
        return 0;
    }

    SET_BIT_IN__BITMAP_AND_HEAP(
            p_game_action_manager
                ->bitmap_and_heap_of__deallocated_game_actions, 
            MAX_QUANTITY_OF__GAME_ACTIONS, 
            index_of__deallocated_game_action, 
            0);

    Game_Action *p_game_action =
        get_p_game_action_by__index_from__game_action_manager(
                p_game_action_manager, 
                index_of__deallocated_game_action);
    initialize_game_action(p_game_action);
    set_game_action_as__allocated(p_game_action);

    return p_game_action;
}

void release_game_action_from__game_action_manager(
        Game_Action_Manager *p_game_action_manager,
        Game_Action *p_game_action) {
#ifndef NDEBUG
    u32 index =  
        p_game_action
        - p_game_action_manager->game_actions
        ;
    if (index >= MAX_QUANTITY_OF__GAME_ACTIONS) {
        debug_error("release_game_action_from__game_action_manager, p_game_action was not allocated with this manager.");
        return;
    }
#endif

    SET_BIT_IN__BITMAP_AND_HEAP(
            p_game_action_manager
                ->bitmap_and_heap_of__deallocated_game_actions, 
            MAX_QUANTITY_OF__GAME_ACTIONS, 
            p_game_action
            - p_game_action_manager->game_actions, 
            1);

    initialize_game_action(p_game_action);
}
