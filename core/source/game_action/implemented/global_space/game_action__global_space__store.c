#include "game_action/implemented/global_space/game_action__global_space__store.h"
#include "collisions/collision_node_pool.h"
#include "defines_weak.h"
#include "game_action/game_action.h"
#include "game_action/game_action_logic_entry.h"
#include "game_action/game_action_logic_table.h"
#include "process/game_action_process.h"
#include "world/chunk_pool.h"
#include "world/global_space.h"
#include "world/global_space_manager.h"

void m_process__game_action__global_space__store(
        Process *p_this_process,
        Game *p_game) {
    // TODO: handle local file IO.
    Game_Action *p_game_action =
        (Game_Action*)p_this_process->p_process_data;

    Global_Space_Vector__3i32 gsv__3i32 =
        p_game_action
        ->ga_kind__global_space__store__gsv__3i32;

    World *p_world = get_p_world_from__game(p_game);
    Process_Manager *p_process_manager =
        get_p_process_manager_from__game(p_game);
    Global_Space_Manager *p_global_space_manager =
        get_p_global_space_manager_from__world(p_world);
    Chunk_Pool *p_chunk_pool =
        get_p_chunk_pool_from__world(p_world);
    Collision_Node_Pool *p_collision_node_pool =
        get_p_collision_node_pool_from__world(p_world);

    Global_Space *p_global_space =
        get_p_global_space_from__global_space_manager(
                p_global_space_manager, 
                gsv__3i32);

    if (!p_global_space) {
        debug_error("m_process__game_action__global_space__store, p_global_space == 0.");
        fail_game_action_process(
                p_game, 
                p_this_process);
        return;
    }
    
    Chunk *p_chunk =
        get_p_chunk_from__global_space(p_global_space);

    if (p_chunk) {
        release_chunk_from__chunk_pool(
                p_chunk_pool, 
                p_chunk);
        set_chunk_for__global_space(
                p_global_space, 
                0);
    }

    Collision_Node *p_collision_node =
        get_p_collision_node_from__global_space(p_global_space);

    if (p_collision_node) {
        release_collision_node_from__collision_node_pool(
                p_collision_node_pool, 
                p_collision_node);
        set_collision_node_for__global_space(
                p_global_space, 
                0);
    }

    release_global_space_in__global_space_manager(
            p_global_space_manager, 
            p_global_space);

    complete_game_action_process(
            p_game,
            p_this_process);
}

void register_game_action__global_space__store(
        Game_Action_Logic_Table *p_game_action_logic_table) {
    initialize_game_action_logic_entry(
            get_p_game_action_logic_entry_by__game_action_kind(
                p_game_action_logic_table, 
                Game_Action_Kind__Global_Space__Store), 
            GAME_ACTION_FLAGS__OUTBOUND_SANITIZE
            | GAME_ACTION_FLAGS__BIT_IS_WITH_PROCESS
            | GAME_ACTION_FLAGS__BIT_IS_PROCESSED_ON_INVOCATION_OR_RESPONSE
            | GAME_ACTION_FLAGS__BIT_IS_LOCAL,
            GAME_ACTION_FLAG_MASK__OUTBOUND_SANITIZE,
            GAME_ACTION_FLAGS__INBOUND_SANITIZE,
            GAME_ACTION_FLAG_MASK__INBOUND_SANITIZE,
            m_process__game_action__global_space__store, 
            PROCESS_FLAG__IS_CRITICAL,
            0,
            0);
}

void initialize_game_action_for__global_space__store(
        Game_Action *p_game_action,
        Global_Space_Vector__3i32 global_space_vector__3i32) {
    initialize_game_action(p_game_action);
    set_the_kind_of__game_action(
            p_game_action, 
            Game_Action_Kind__Global_Space__Store);
    p_game_action
        ->ga_kind__global_space__store__gsv__3i32=
        global_space_vector__3i32;
}
