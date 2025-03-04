#include "game_action/implemented/global_space/game_action__global_space__request.h"
#include "defines.h"
#include "defines_weak.h"
#include "game.h"
#include "game_action/game_action.h"
#include "game_action/game_action_logic_entry.h"
#include "game_action/game_action_logic_table.h"
#include "multiplayer/tcp_socket.h"
#include "multiplayer/tcp_socket_manager.h"
#include "platform.h"
#include "world/world.h"
#include "world/global_space_manager.h"
#include "world/global_space.h"
#include "process/game_action_process.h"

void m_process__game_action__global_space__request__inbound_server(
        Process *p_this_process,
        Game *p_game) {
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
        // TODO: relay failure to client somehow
        //
        //       the client is requesting a global_space
        //       for a region that isn't loaded, which
        //       means the client has lost track of their
        //       true position relative to the server's state.
        debug_error("m_process__game_action__global_space__request__inbound_server, bad request.");
        fail_game_action_process(
                p_game, 
                p_this_process);
        return;
    }

    if (is_global_space__deconstructing(
                p_global_space)) {
        // TODO: relay failure to client somehow
        //
        //       the client is requesting a global_space
        //       for a region that is BEING unloaded, which
        //       means either one of two things:
        //          1) the client has lost track of their
        //          true position relative to the server's state.
        //          2) the client's request is outdated
        //          and no longer needs to be processed.
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
                p_game_action, 
                (u8*)p_global_space->p_chunk, 
                sizeof(Chunk), 
                p_game_action
                    ->ga_kind__global_space__request__chunk_payload_bitmap, 
                (u16)TCP_PAYLOAD_BITMAP__QUANTITY_OF_BITS(Chunk))) {
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

    complete_game_action_process(
            p_game, 
            p_this_process);
}

///
/// Only defined for client, poll for the completion of
/// the global_space.
///
void m_process__game_action__global_space__request__outbound_client(
        Process *p_this_process,
        Game *p_game) {
    Serialization_Request *p_serialization_request =
        (Serialization_Request*)p_this_process->p_process_data;

    switch (poll_game_action_process__tcp_receive(
                p_game, 
                p_this_process)) {
        case PLATFORM_Read_File_Error__End_Of_File:
            break;
        case PLATFORM_Read_File_Error__System_Busy:
            // TODO: handle timeout
            return;
        default:
            debug_error("m_process__game_action__global_space__request__outbound_client, reception failed.");
            fail_game_action_process_for__tcp(
                    p_game, 
                    p_this_process);
            return;
    }

    Game_Action *p_game_action =
        (Game_Action*)p_serialization_request->p_data;

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
}

void m_process__game_action__global_space__request__outbound_client__init(
        Process *p_this_process,
        Game *p_game) {
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

    bool is_process__mutation_successful =
        set_game_action_process_as__tcp_payload_receiver(
                p_game, 
                p_this_process, 
                (u8*)p_global_space->p_chunk, 
                sizeof(Chunk));
    if (!is_process__mutation_successful) {
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
            m_process__game_action__global_space__request__outbound_client, 
            PROCESS_FLAG__IS_CRITICAL);
}

void register_game_action__global_space__request_for__server(
        Game_Action_Logic_Table *p_game_action_logic_table) {
    initialize_game_action_logic_entry_as__process__in(
            get_p_game_action_logic_entry_by__game_action_kind(
                p_game_action_logic_table, 
                Game_Action_Kind__Global_Space__Request), 
            m_process__game_action__global_space__request__inbound_server, 
            PROCESS_FLAG__IS_CRITICAL);
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
}
