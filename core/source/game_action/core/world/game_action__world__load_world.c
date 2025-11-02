#include "game_action/core/world/game_action__world__load_world.h"
#include "client.h"
#include "collisions/hitbox_aabb.h"
#include "defines.h"
#include "defines_weak.h"
#include "game.h"
#include "game_action/core/game_action__bad_request.h"
#include "game_action/core/world/game_action__world__load_client.h"
#include "game_action/game_action_logic_entry.h"
#include "game_action/game_action_logic_table.h"
#include "platform_defines.h"
#include "process/game_action_process.h"
#include "process/process.h"
#include "process/process_manager.h"
#include "types/implemented/game_action_kind.h"
#include "world/chunk_vectors.h"
#include "world/local_space_manager.h"
#include "world/serialization/world_directory.h"
#include "collisions/hitbox_aabb_manager.h"

void m_process__game_action__world__load_world(
        Process *p_this_process,
        Game *p_game) {
    Game_Action *p_game_action =
        (Game_Action*)p_this_process->p_process_data;
    Client *p_client =
        get_p_client_by__uuid_from__game(
                p_game, 
                p_game_action
                ->ga_kind__world__load_world__uuid_of__client__u32);
    if (!p_client) {
        debug_error("m_process__game_action__world__load_world, p_client == 0.");
        dispatch_game_action__bad_request(
                p_game, 
                p_game_action, 
                0);
        fail_process(p_this_process);
        return;
    }
    switch (p_this_process->process_valueA__i16) {
        default:
            break;
        case 1:
            goto load_world_data;
        case 2:
            goto poll_world_data;
    }
    // TODO: yield process on each IO op
    IO_path path_to__world;
    memset(path_to__world, 0, sizeof(path_to__world));
    Index__u32 index_of__path =
        stat_world_directory(
                get_p_PLATFORM_file_system_context_from__game(p_game), 
                get_p_world_from__game(p_game), 
                path_to__world);
    if (!index_of__path) {
        debug_error("m_process__game_action__world__load_world, failed to stat world directory: %s", path_to__world);
        fail_process(p_this_process);
        return;
    }

    p_this_process->process_valueA__i16 = 1;
    return;
load_world_data:
    ;
    Hitbox_AABB *p_hitbox_aabb =
        get_p_hitbox_aabb_by__uuid_u32_from__hitbox_aabb_manager(
                get_p_hitbox_aabb_manager_from__game(
                    p_game),
                GET_UUID_P(p_client));

    if (!p_hitbox_aabb) {
        debug_error("m_process__game_action__world__load_world, p_client lacks hitbox component. Cannot determine location to load.");
        fail_process(p_this_process);
        return;
    }

    Chunk_Vector__3i32 gsv__3i32 =
        vector_3i32F4_to__chunk_vector_3i32(
                get_position_3i32F4_of__hitbox_aabb(
                    p_hitbox_aabb));

    load_local_space_manager_at__global_space_vector__3i32(
            get_p_local_space_manager_from__client(p_client), 
            p_game, 
            gsv__3i32);

    p_this_process->process_valueA__i16 = 2;
    return;
poll_world_data:

    if (!is_local_space_manager__loaded(
                p_game, 
                get_p_local_space_manager_from__client(p_client))) {
        // TODO: timeout
        return;
    }

    complete_process(p_this_process);
}

void register_game_action__world__load_world(
        Game_Action_Logic_Table *p_game_action_logic_table) {
    initialize_game_action_logic_entry(
            get_p_game_action_logic_entry_by__game_action_kind(
                p_game_action_logic_table, 
                Game_Action_Kind__World__Load_World), 
            GAME_ACTION_FLAGS__OUTBOUND_SANITIZE
            | GAME_ACTION_FLAGS__BIT_IS_WITH_PROCESS
            | GAME_ACTION_FLAGS__BIT_IS_PROCESSED_ON_INVOCATION_OR_RESPONSE
            | GAME_ACTION_FLAGS__BIT_IS_LOCAL,
            GAME_ACTION_FLAG_MASK__OUTBOUND_SANITIZE,
            GAME_ACTION_FLAGS__INBOUND_SANITIZE,
            GAME_ACTION_FLAG_MASK__INBOUND_SANITIZE,
            PROCESS_PRIORITY__0_MAXIMUM,
            m_process__game_action__world__load_world, 
            PROCESS_FLAG__IS_CRITICAL,
            0, 
            0);
}

void initialize_game_action_for__world__load_world(
        Game_Action *p_game_action,
        Identifier__u32 uuid_of__client__u32) {
    initialize_game_action(p_game_action);
    set_the_kind_of__game_action(
            p_game_action, 
            Game_Action_Kind__World__Load_World);
    p_game_action
        ->ga_kind__world__load_world__uuid_of__client__u32 =
        uuid_of__client__u32;
}
