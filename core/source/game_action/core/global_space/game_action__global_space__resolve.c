#include "game_action/core/global_space/game_action__global_space__resolve.h"
#include "collisions/collision_node_pool.h"
#include "defines.h"
#include "defines_weak.h"
#include "game.h"
#include "game_action/game_action.h"
#include "game_action/game_action_logic_entry.h"
#include "game_action/game_action_logic_table.h"
#include "process/game_action_process.h"
#include "process/process.h"
#include "serialization/serialization_header.h"
#include "types/implemented/tile_kind.h"
#include "world/chunk_generator_table.h"
#include "world/chunk_pool.h"
#include "world/global_space.h"
#include "world/global_space_manager.h"
#include "world/serialization/world_directory.h"
#include "world/world.h"

void m_process__dispose_handler__game_action__global_space__resolve(
        Process *p_this_process,
        Game *p_game) {
    Global_Space *p_global_space = p_this_process->p_process_data;
    p_global_space->p_generation_process = 0;
    set_global_space_as__NOT_constructing(
            p_global_space);
    set_global_space_as__dirty(
            p_global_space);
}

void m_process__game_action__global_space__resolve(
        Process *p_this_process,
        Game *p_game) {
    Game_Action *p_game_action =
        (Game_Action*)p_this_process->p_process_data;

    Global_Space_Vector__3i32 gsv__3i32 =
        p_game_action
        ->ga_kind__global_space__resolve__gsv__3i32;

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

    debug_info__verbose("m_process__game_action__global_space__resolve, resolve: (%d,%d,%d)",
            gsv__3i32.x__i32,
            gsv__3i32.y__i32,
            gsv__3i32.z__i32);

    if (!p_global_space) {
        debug_error("m_process__game_action__global_space__resolve, p_global_space == 0");
        fail_process(p_this_process);
        return;
    }

    if (get_p_chunk_from__global_space(p_global_space)) {
        /// assume that this process is being run after
        /// being dequeued from the deserialization process.
        debug_info__verbose("m_process__game_action__global_space__resolve, COMPLETE: (%d,%d,%d)",
                gsv__3i32.x__i32,
                gsv__3i32.y__i32,
                gsv__3i32.z__i32);

        complete_process(p_this_process);
        return;
    }

    Chunk *p_chunk =
        allocate_chunk_from__chunk_pool(
                p_chunk_pool, 
                GET_UUID_P__u64(p_global_space));

    if (!p_chunk) {
        debug_error("m_process__game_action__global_space__resolve, p_chunk == 0.");
        fail_process(p_this_process);
        drop_global_space_within__global_space_manager(
                p_game,
                gsv__3i32);
        return;
    }

    Collision_Node *p_collision_node =
        allocate_collision_node_from__collision_node_pool(
                p_collision_node_pool,
                GET_UUID_P__u64(p_global_space));

    if (!p_collision_node) {
        debug_error("m_process__game_action__global_space__resolve, p_collision_node == 0.");
        release_chunk_from__chunk_pool(
                p_chunk_pool, 
                p_chunk);
        drop_global_space_within__global_space_manager(
                p_game,
                gsv__3i32);
        fail_process(p_this_process);
        return;
    }

    p_global_space->p_chunk = p_chunk;
    p_global_space->p_collision_node = p_collision_node;

    // TODO: rely on region file for file stat-ing

    IO_path path;
    if (stat_chunk_file__tiles(
                get_p_PLATFORM_file_system_context_from__game(p_game), 
                get_p_world_from__game(p_game), 
                p_global_space, 
                path)) {
        Process *p_process =
            dispatch_process__deserialize_global_space(
                    p_game,
                    p_global_space);

        if (!p_process) {
            debug_error("m_process__game_action__global_space__resolve, failed to dispatch deserialization process.");
            fail_process(p_this_process);
            return;
        }
        enqueue_process(
                p_this_process, 
                p_process);

        return;
    }

    m_Process m_process__chunk_generator =
        get_default_chunk_generator_process(
                get_p_chunk_generation_table_from__game(p_game));
    if (!m_process__chunk_generator) {
        debug_error("null");
        memset(&get_p_chunk_from__global_space(p_global_space)
                ->chunk_data,
                0,
                sizeof(Chunk_Data));
        complete_process(p_this_process);
        return;
    }
    p_this_process->m_process_dispose__handler(
            p_this_process,
            p_game);
    p_global_space->p_generation_process =
        p_this_process;
    // set as non-critical
    p_this_process->process_flags__u8 &=
        ~PROCESS_FLAG__IS_CRITICAL;
    p_this_process->p_process_data = 
        p_global_space;
    p_this_process->m_process_run__handler =
        m_process__chunk_generator;
    p_this_process->m_process_dispose__handler =
        m_process__dispose_handler__game_action__global_space__resolve;
}

void register_game_action__global_space__resolve(
        Game_Action_Logic_Table *p_game_action_logic_table) {
    initialize_game_action_logic_entry(
            get_p_game_action_logic_entry_by__game_action_kind(
                p_game_action_logic_table, 
                Game_Action_Kind__Global_Space__Resolve), 
            GAME_ACTION_FLAGS__OUTBOUND_SANITIZE
            | GAME_ACTION_FLAGS__BIT_IS_WITH_PROCESS
            | GAME_ACTION_FLAGS__BIT_IS_PROCESSED_ON_INVOCATION_OR_RESPONSE
            | GAME_ACTION_FLAGS__BIT_IS_LOCAL,
            GAME_ACTION_FLAG_MASK__OUTBOUND_SANITIZE,
            GAME_ACTION_FLAGS__INBOUND_SANITIZE,
            GAME_ACTION_FLAG_MASK__INBOUND_SANITIZE,
            PROCESS_PRIORITY__0_MAXIMUM,
            m_process__game_action__global_space__resolve, 
            PROCESS_FLAG__IS_CRITICAL,
            0,
            0);
}

void initialize_game_action_for__global_space__resolve(
        Game_Action *p_game_action,
        Global_Space_Vector__3i32 global_space_vector__3i32) {
    initialize_game_action(p_game_action);
    set_the_kind_of__game_action(
            p_game_action, 
            Game_Action_Kind__Global_Space__Resolve);
    p_game_action
        ->ga_kind__global_space__resolve__gsv__3i32=
        global_space_vector__3i32;
}
