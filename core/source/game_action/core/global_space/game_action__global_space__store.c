#include "game_action/core/global_space/game_action__global_space__store.h"
#include "collisions/collision_node_pool.h"
#include "defines_weak.h"
#include "game.h"
#include "game_action/game_action.h"
#include "game_action/game_action_logic_entry.h"
#include "game_action/game_action_logic_table.h"
#include "process/game_action_process.h"
#include "process/process.h"
#include "world/chunk_pool.h"
#include "world/global_space.h"
#include "world/global_space_manager.h"
#include "world/serialization/world_directory.h"

void m_process__game_action__global_space__store(
        Process *p_this_process,
        Game *p_game) {
    // TODO: handle local file IO.
    Game_Action *p_game_action =
        (Game_Action*)p_this_process->p_process_data;

    Global_Space *p_global_space =
        get_p_global_space_from__global_space_manager(
                get_p_global_space_manager_from__game(p_game), 
                p_game_action->ga_kind__global_space__store__gsv__3i32);
    
    if (!p_global_space) {
        debug_error("m_process__game_action__global_space__store [%p], p_global_space == 0.",
                p_this_process);
        fail_process(p_this_process);
        return;
    }

    if (!is_global_space__allocated(p_global_space)) {
        complete_process(p_this_process);
        return;
    }

    debug_info__verbose("m_process__game_action__global_space__store [%p], (%d,%d,%d)",
            p_this_process,
            p_global_space->chunk_vector__3i32.x__i32,
            p_global_space->chunk_vector__3i32.y__i32,
            p_global_space->chunk_vector__3i32.z__i32);

    IO_path path;
    stat_chunk_file__tiles(
            get_p_PLATFORM_file_system_context_from__game(p_game), 
            get_p_world_from__game(p_game), 
            p_global_space, 
            path);
    Process *p_process =
        dispatch_process__serialize_global_space(
                p_game,
                p_global_space);

    if (!p_process) {
        debug_error("m_process__game_action__global_space__store, failed to dispatch deserialization process.");
        fail_process(p_this_process);
        return;
    }

    complete_process(p_this_process);
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
            PROCESS_PRIORITY__0_MAXIMUM,
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
