#include "game_action/core/world/game_action__world__load_client.h"
#include "client.h"
#include "collisions/hitbox_aabb.h"
#include "collisions/hitbox_aabb_manager.h"
#include "debug/debug.h"
#include "defines.h"
#include "defines_weak.h"
#include "game.h"
#include "game_action/core/game_action__bad_request.h"
#include "game_action/game_action.h"
#include "game_action/game_action_logic_entry.h"
#include "game_action/game_action_logic_table.h"
#include "multiplayer/session_token.h"
#include "process/game_action_process.h"
#include "process/process.h"
#include "process/process_manager.h"
#include "types/implemented/game_action_kind.h"
#include "vectors.h"
#include "world/chunk_vectors.h"
#include "world/local_space_manager.h"
#include "world/serialization/world_directory.h"
#include "world/world.h"

void m_process__game_action__world__load_client__inbound(
        Process *p_this_process,
        Game *p_game) {
    Game_Action *p_game_action =
        (Game_Action*)p_this_process
        ->p_process_data;
    Client *p_client =
        get_p_client_by__uuid_from__game(
                p_game, 
                p_game_action
                ->ga_kind__world__load_world__uuid_of__client__u32);
    if (is_client__active(p_client)) {
        complete_process(p_this_process);
        return;
    }

    // TODO: magic num timeout
    if (p_this_process->process_valueA__i16++ > 16) {
        debug_error("m_process__game_action__world__load_client__inbound, too many attempts.");
        dispatch_game_action__bad_request(
                p_game, 
                p_game_action, 
                0);
        fail_process(p_this_process);
        return;
    }

    if (!dispatch_game_action__world__load_client(
                p_game, 
                p_game_action
                ->ga_kind__world__load_world__uuid_of__client__u32)) {
        debug_error("m_process__game_action__world__load_client__inbound, fail to dispatch game_action load_client.");
        dispatch_game_action__bad_request(
                p_game, 
                p_game_action, 
                1);
        fail_process(p_this_process);
        return;
    }

    Process *p_process =
        get_p_latest_allocated_process_from__process_manager(
                get_p_process_manager_from__game(
                    p_game));

    if (!p_process) {
        debug_error("m_process__game_action__world__load_client__inbound, process for loading client wasn't created.");
        dispatch_game_action__bad_request(
                p_game, 
                p_game_action, 
                1);
        fail_process(p_this_process);
        return;
    }

    enqueue_process(
            p_this_process, 
            p_process);
}

void m_process__game_action__world__load_client__outbound(
        Process *p_this_process,
        Game *p_game) {
    Game_Action *p_game_action =
        (Game_Action*)p_this_process
        ->p_process_data;

    Client *p_client =
        get_p_client_by__uuid_from__game(
                p_game, 
                p_game_action
                ->ga_kind__world__load_world__uuid_of__client__u32);

    if (!p_client) {
        debug_error("m_process__game_action__world__load_client__outbound, p_client == 0.");
        fail_process(p_this_process);
        return;
    }
    if (is_client__loaded(p_client)) {
        Hitbox_AABB *p_hitbox_aabb =
            get_p_hitbox_aabb_by__uuid_u32_from__hitbox_aabb_manager(
                    get_p_hitbox_aabb_manager_from__game(p_game), 
                    GET_UUID_P(p_client));
        if (!p_hitbox_aabb) {
            debug_warning("m_process__game_action__world__load_client__outbound, client missing hitbox, defaulting to world spawn point.");
        }
        Global_Space_Vector__3i32 gsv__3i32 =
            (p_hitbox_aabb)
            ? vector_3i32F4_to__chunk_vector_3i32(
                    get_position_3i32F4_of__hitbox_aabb(p_hitbox_aabb))
            : vector_3i32F4_to__chunk_vector_3i32(
                    get_spawn_point_of__world(get_p_world_from__game(p_game)))
            ;
        if (!is_chunk_vectors_3i32__equal(
                    get_center_of__local_space_manager(get_p_local_space_manager_from__client(p_client)), 
                    gsv__3i32)) {
            // TODO: timeout/retry this code path.
            Process *p_process__teleport_client =
                teleport_client(p_game, p_client, get_position_3i32F4_of__hitbox_aabb(p_hitbox_aabb));
            enqueue_process(
                    p_this_process,
                    p_process__teleport_client);
            return;
        } else {
            if (p_hitbox_aabb)
                set_hitbox_aabb_as__active(p_hitbox_aabb);
            set_client_as__active(p_client);
            complete_process(p_this_process);
            return;
        }
    }

    if (!is_local_space_manager__loaded(
                p_game, 
                get_p_local_space_manager_from__client(p_client))) {
        // Wait for world to be loaded...
        // TODO: timeout
        return;
    }

    // TODO: magic num timeout
    if (p_this_process->process_valueA__i16++ > 16) {
        debug_error("m_process__game_action__world__load_client__outbound, too many attempts.");
        dispatch_game_action__bad_request(
                p_game, 
                p_game_action, 
                3);
        fail_process(p_this_process);
        return;
    }

    IO_path path_to__client;
    memset(path_to__client, 0, sizeof(path_to__client));
    Index__u32 index_of__path_to__base_directory = 0;
    Index__u32 index_of__path =
        stat_client_file(
                get_p_PLATFORM_file_system_context_from__game(p_game), 
                get_p_world_from__game(p_game), 
                path_to__client, 
                p_game_action
                ->ga_kind__world__load_world__uuid_of__client__u32,
                &index_of__path_to__base_directory);

    Process *p_process = 0;
    if (!index_of__path_to__base_directory) {
        // client file does not exist, we can go ahead and generate a new client.
        p_process =
            dispatch_handler_process_to__create_client(
                    p_game, 
                    get_uuid_u32_of__session_token_player_uuid_u64(
                        p_game_action->ga_kind__tcp_connect__begin__session_token));
        return;
    } else {
        p_process =
            dispatch_handler_process_to__load_client(
                p_game, 
                path_to__client,
                p_game_action
                ->ga_kind__world__load_world__uuid_of__client__u32);
    }

    if (!p_process) {
        debug_error("m_process__game_action__world__load_client__outbound, failed to dispatch process.");
        dispatch_game_action__bad_request(
                p_game, 
                p_game_action, 
                1);
        fail_process(p_this_process);
        return;
    }

    enqueue_process(
            p_this_process, 
            p_process);
}

void register_game_action__world__load_client(
        Game_Action_Logic_Table *p_game_action_logic_table) {
    initialize_game_action_logic_entry(
            get_p_game_action_logic_entry_by__game_action_kind(
                p_game_action_logic_table, 
                Game_Action_Kind__World__Load_Client), 
            GAME_ACTION_FLAGS__OUTBOUND_SANITIZE
            | GAME_ACTION_FLAGS__BIT_IS_WITH_PROCESS
            | GAME_ACTION_FLAGS__BIT_IS_PROCESSED_ON_INVOCATION_OR_RESPONSE
            | GAME_ACTION_FLAGS__BIT_IS_LOCAL,
            GAME_ACTION_FLAG_MASK__OUTBOUND_SANITIZE,
            GAME_ACTION_FLAGS__INBOUND_SANITIZE,
            GAME_ACTION_FLAG_MASK__INBOUND_SANITIZE,
            PROCESS_PRIORITY__0_MAXIMUM,
            m_process__game_action__world__load_client__outbound, 
            PROCESS_FLAG__IS_CRITICAL,
            m_process__game_action__world__load_client__inbound, 
            PROCESS_FLAG__IS_CRITICAL);
}

void initialize_game_action_for__world__load_client(
        Game_Action *p_game_action,
        Identifier__u32 uuid_of__client__u32) {
initialize_game_action(p_game_action);
    set_the_kind_of__game_action(
            p_game_action, 
            Game_Action_Kind__World__Load_Client);
    p_game_action
        ->ga_kind__world__load_world__uuid_of__client__u32 =
        uuid_of__client__u32;
}
