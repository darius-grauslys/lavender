#include "client.h"
#include "collisions/collision_node_pool.h"
#include "game_action/implemented/game_action__bad_request.h"
#include "game_action/implemented/global_space/game_action__global_space__request.h"
#include "defines.h"
#include "defines_weak.h"
#include "game.h"
#include "game_action/game_action.h"
#include "game_action/game_action_logic_entry.h"
#include "game_action/game_action_logic_table.h"
#include "game_action/implemented/global_space/game_action__global_space__resolve.h"
#include "multiplayer/tcp_socket.h"
#include "multiplayer/tcp_socket_manager.h"
#include "platform.h"
#include "serialization/serialization_header.h"
#include "timer.h"
#include "vectors.h"
#include "world/chunk_pool.h"
#include "world/local_space.h"
#include "world/local_space_manager.h"
#include "world/world.h"
#include "world/global_space_manager.h"
#include "world/global_space.h"
#include "process/game_action_process.h"

void m_process__game_action__global_space__request__outbound_server(
        Process *p_this_process,
        Game *p_game) {
    debug_info("m_process__game_action__global_space__request__outbound_server");
    Game_Action *p_game_action =
        (Game_Action*)p_this_process->p_process_data;

    Global_Space_Vector__3i32 *p_gsv__3i32 =
        &p_game_action->ga_kind__global_space__request__gsv_3i32;

    Global_Space_Manager *p_global_space_manager =
        get_p_global_space_manager_from__world(
                get_p_world_from__game(p_game));

    Global_Space *p_global_space =
        get_p_global_space_from__global_space_manager(
                p_global_space_manager, 
                *p_gsv__3i32);

    if (!p_global_space) {
        dispatch_game_action__bad_request(
                p_game, 
                p_game_action, 
                0);
        debug_error("m_process__game_action__global_space__request__outbound_server, bad request.");
        fail_game_action_process(
                p_game, 
                p_this_process);
        return;
    }

    if (is_global_space__deconstructing(
                p_global_space)) {
        dispatch_game_action__bad_request(
                p_game, 
                p_game_action, 
                1);
        debug_error("m_process__game_action__global_space__request__outbound_server, bad request.");
        fail_game_action_process(
                p_game, 
                p_this_process);
        return;
    }

    complete_game_action_process(
            p_game, 
            p_this_process);
    dispatch_game_action__global_space__resolve(
            p_game, 
            p_game_action->ga_kind__global_space__request__gsv_3i32);
}

void m_process__game_action__global_space__request__inbound_server(
        Process *p_this_process,
        Game *p_game) {
    debug_info("m_process__game_action__global_space__request__inbound_server");
    Game_Action *p_game_action =
        (Game_Action*)p_this_process->p_process_data;

    Global_Space_Vector__3i32 *p_gsv__3i32 =
        &p_game_action->ga_kind__global_space__request__gsv_3i32;

    Global_Space_Manager *p_global_space_manager =
        get_p_global_space_manager_from__world(
                get_p_world_from__game(p_game));

    Client *p_client =
        get_p_client_by__uuid_from__game(
                p_game, 
                p_game_action->uuid_of__client__u32);

    Local_Space *p_local_space =
        get_p_local_space_from__local_space_manager(
                get_p_local_space_manager_from__client(p_client),
                *p_gsv__3i32);
    
    Global_Space *p_global_space =
        get_p_global_space_from__local_space(
                p_local_space);

    if (!p_global_space) {
        dispatch_game_action__bad_request(
                p_game, 
                p_game_action, 
                0);
        debug_error("m_process__game_action__global_space__request__inbound_server, bad request.");
        fail_game_action_process(
                p_game, 
                p_this_process);
        return;
    }

    if (is_global_space__deconstructing(
                p_global_space)) {
        dispatch_game_action__bad_request(
                p_game, 
                p_game_action, 
                1);
        debug_error("m_process__game_action__global_space__request__inbound_server, bad request.");
        fail_game_action_process(
                p_game, 
                p_this_process);
        return;
    }

    if (is_global_space__constructing(p_global_space)) {
        return;
    }

    switch (poll_game_action_process__tcp_delivery(
                p_game, 
                p_game_action->uuid_of__client__u32,
                p_game_action->_serialiation_header.uuid, 
                (u8*)&p_global_space->p_chunk->chunk_data, 
                sizeof(Chunk_Data), 
                p_game_action
                    ->ga_kind__global_space__request__chunk_payload_bitmap, 
                (u16)TCP_PAYLOAD_BITMAP__QUANTITY_OF__PAYLOADS(Chunk))) {
        case PLATFORM_Write_File_Error__Max_Size_Reached:
            break;
        case PLATFORM_Write_File_Error__System_Busy:
            return;
        default:
            debug_error("m_process__game_action__global_space__request__inbound_server, failed to send packets.");
            fail_game_action_process(
                    p_game, 
                    p_this_process);
            return;
    }

    debug_info("m_process__game_action__global_space__request__inbound_server, finished.");
    complete_game_action_process(
            p_game, 
            p_this_process);
}

void m_process__game_action__global_space__request__inbound_server__init(
        Process *p_this_process,
        Game *p_game) {
    debug_info("m_process__game_action__global_space__request__inbound_server__init");
    Game_Action *p_game_action =
        (Game_Action*)p_this_process->p_process_data;

    memset(
            p_game_action
            ->ga_kind__global_space__request__chunk_payload_bitmap,
            0,
            sizeof(p_game_action
                ->ga_kind__global_space__request__chunk_payload_bitmap));

    p_this_process->m_process_run__handler =
        m_process__game_action__global_space__request__inbound_server;
}

///
/// Only defined for client, poll for the completion of
/// the global_space.
///
void m_process__game_action__global_space__request__outbound_client(
        Process *p_this_process,
        Game *p_game) {
    debug_info("m_process__game_action__global_space__request__outbound_client");
    Serialization_Request *p_serialization_request =
        (Serialization_Request*)p_this_process->p_process_data;
    Game_Action *p_game_action =
        (Game_Action*)p_serialization_request->p_data;

    if (is_game_action__bad_request(p_game_action)) {
        debug_error("m_process__game_action__global_space__request__outbound_client, bad request.");
        Global_Space_Vector__3i32 *p_gsv__3i32 =
            &p_game_action->ga_kind__global_space__request__gsv_3i32;

        Global_Space_Manager *p_global_space_manager =
            get_p_global_space_manager_from__world(
                    get_p_world_from__game(p_game));

        drop_global_space_within__global_space_manager(
                p_game, 
                *p_gsv__3i32);

        fail_game_action_process_for__tcp(
                p_game, 
                p_this_process);
        return;
    }

    switch (poll_game_action_process__tcp_receive(
                p_game, 
                p_this_process)) {
        case PLATFORM_Read_File_Error__End_Of_File:
            break;
        case PLATFORM_Read_File_Error__System_Busy:
            if (!poll_timer_by__this_duration_u32(
                        &p_game_action
                        ->ga_kind__global_space__request__timeout, 
                        get_elapsed_time__u32F20_of__game(p_game))) {
                return;
            }
            debug_error("m_process__game_action__global_space__request__outbound_client, reception timeout.");
            fail_game_action_process_for__tcp(
                    p_game, 
                    p_this_process);
            return;
        default:
            debug_error("m_process__game_action__global_space__request__outbound_client, reception failed.");
            fail_game_action_process_for__tcp(
                    p_game, 
                    p_this_process);
            return;
    }

    Global_Space_Vector__3i32 *p_gsv__3i32 =
        &p_game_action->ga_kind__global_space__request__gsv_3i32;

    Global_Space_Manager *p_global_space_manager =
        get_p_global_space_manager_from__world(
                get_p_world_from__game(p_game));

    Global_Space *p_global_space =
        get_p_global_space_from__global_space_manager(
                p_global_space_manager, 
                *p_gsv__3i32);

    if (!p_global_space) {
        debug_error("m_process__game_action__global_space__request__outbound_client, p_global_space == 0.");
        fail_game_action_process_for__tcp(
                p_game, 
                p_this_process);
        return;
    }

    set_global_space_as__NOT_constructing(
            p_global_space);

    drop_global_space(p_global_space);
    complete_game_action_process_for__tcp(
            p_game, 
            p_this_process);
    debug_info("m_process__game_action__global_space__request__outbound_client, finished.");
}

void m_process__game_action__global_space__request__outbound_client__init(
        Process *p_this_process,
        Game *p_game) {
    debug_info("m_process__game_action__global_space__request__outbound_client__init");
    Game_Action *p_game_action =
        (Game_Action*)p_this_process->p_process_data;

    Global_Space_Vector__3i32 *p_gsv__3i32 =
        &p_game_action->ga_kind__global_space__request__gsv_3i32;

    Global_Space_Manager *p_global_space_manager =
        get_p_global_space_manager_from__world(
                get_p_world_from__game(p_game));

    Global_Space *p_global_space =
        get_p_global_space_from__global_space_manager(
                p_global_space_manager, 
                *p_gsv__3i32);

    if (!p_global_space) {
        debug_error("m_process__game_action__global_space__request__outbound_client__init, p_global_space == 0.");
        fail_game_action_process(
                p_game, 
                p_this_process);
        return;
    }

    // TODO: make a function to gen these sub structs
    // and bind to p_global_space.
    Chunk *p_chunk =
        allocate_chunk_from__chunk_pool(
                get_p_chunk_pool_from__world(
                    get_p_world_from__game(p_game)), 
                GET_UUID_P__u64(p_global_space));

    if (!p_chunk) {
        debug_error("m_process__game_action__global_space__request__outbound_client__init, failed to allocate chunk.");
        drop_global_space_within__global_space_manager(
                p_game, 
                *p_gsv__3i32);
        fail_game_action_process(
                p_game, 
                p_this_process);
        return;
    }

    Collision_Node *p_collision_node =
        allocate_collision_node_from__collision_node_pool(
                get_p_collision_node_pool_from__world(
                    get_p_world_from__game(p_game)), 
                GET_UUID_P__u64(p_global_space));

    if (!p_collision_node) {
        drop_global_space_within__global_space_manager(
                p_game, 
                *p_gsv__3i32);
        debug_error("m_process__game_action__global_space__request__outbound_client__init, failed to allocate collision_node.");
        fail_game_action_process(
                p_game, 
                p_this_process);
        return;
    }

    p_global_space->p_chunk = p_chunk;
    p_global_space->p_collision_node = p_collision_node;

    bool is_process__mutation_successful =
        set_game_action_process_as__tcp_payload_receiver(
                p_game, 
                p_this_process, 
                (u8*)&p_global_space->p_chunk->chunk_data, 
                sizeof(Chunk_Data));
    if (!is_process__mutation_successful) {
        drop_global_space_within__global_space_manager(
                p_game, 
                *p_gsv__3i32);
        debug_error("m_process__game_action__global_space__request__outbound_client__init, failed to set process as tcp receiver.");
        fail_game_action_process(
                p_game, 
                p_this_process);
        return;
    }

    // doesn't hurt to be redundant here.
    // TODO: does it?
    set_global_space_as__constructing(
            p_global_space);

    hold_global_space(p_global_space);

    p_this_process->m_process_run__handler =
        m_process__game_action__global_space__request__outbound_client;
}

void register_game_action__global_space__request_for__client(
        Game_Action_Logic_Table *p_game_action_logic_table) {
    initialize_game_action_logic_entry_as__process__out(
            get_p_game_action_logic_entry_by__game_action_kind(
                p_game_action_logic_table, 
                Game_Action_Kind__Global_Space__Request), 
            m_process__game_action__global_space__request__outbound_client__init, 
            PROCESS_FLAG__IS_CRITICAL);
}

void register_game_action__global_space__request_for__server(
        Game_Action_Logic_Table *p_game_action_logic_table) {
    initialize_game_action_logic_entry(
            get_p_game_action_logic_entry_by__game_action_kind(
                p_game_action_logic_table, 
                Game_Action_Kind__Global_Space__Request), 
            GAME_ACTION_FLAGS__OUTBOUND_SANITIZE
            | GAME_ACTION_FLAGS__BIT_IS_LOCAL,
            GAME_ACTION_FLAG_MASK__OUTBOUND_SANITIZE,
            GAME_ACTION_FLAGS__INBOUND_SANITIZE
            | GAME_ACTION_FLAGS__BIT_IS_WITH_PROCESS
            | GAME_ACTION_FLAGS__BIT_IS_PROCESSED_ON_INVOCATION_OR_RESPONSE,
            GAME_ACTION_FLAG_MASK__INBOUND_SANITIZE,
            m_process__game_action__global_space__request__outbound_server, 
            PROCESS_FLAGS__NONE,
            m_process__game_action__global_space__request__inbound_server__init, 
            PROCESS_FLAGS__NONE);
}

void initialize_game_action_for__global_space__request(
        Game_Action *p_game_action,
        Global_Space_Vector__3i32 global_space_vector__3i32) {
    initialize_game_action(p_game_action);
    set_the_kind_of__game_action(
            p_game_action, 
            Game_Action_Kind__Global_Space__Request);
    p_game_action
        ->ga_kind__global_space__request__gsv_3i32 =
        global_space_vector__3i32;
    initialize_timer_u32(
            &p_game_action->ga_kind__global_space__request__timeout, 
            GA_KIND__GBLOAL_SPACE__REQUEST__TIMEOUT
            << 20);
}
