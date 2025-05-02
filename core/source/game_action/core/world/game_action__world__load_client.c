#include "game_action/core/world/game_action__world__load_client.h"
#include "client.h"
#include "defines_weak.h"
#include "game.h"
#include "game_action/core/game_action__bad_request.h"
#include "game_action/game_action.h"
#include "game_action/game_action_logic_entry.h"
#include "game_action/game_action_logic_table.h"
#include "process/game_action_process.h"
#include "process/process.h"
#include "process/process_manager.h"
#include "types/implemented/game_action_kind.h"
#include "world/serialization/world_directory.h"

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

    if (is_client__active(p_client)) {
        complete_process(p_this_process);
        return;
    }

    set_client_as__loading(p_client);

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

    if (!index_of__path_to__base_directory) {
        debug_error("m_process__game_action__world__load_client__outbound, failed to find client file.");
        dispatch_game_action__bad_request(
                p_game, 
                p_game_action, 
                0);
        fail_process(p_this_process);
        return;
    }

    Process *p_process =
        dispatch_handler_process_to__load_client(
            p_game, 
            path_to__client,
            p_game_action
            ->ga_kind__world__load_world__uuid_of__client__u32);

    if (!p_process) {
        debug_error("m_process__game_action__world__load_client__outbound, failed to dispatch deserialization process.");
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
