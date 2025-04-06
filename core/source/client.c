#include "client.h"
#include "defines.h"
#include "defines_weak.h"
#include "game.h"
#include "game_action/game_action.h"
#include "game_action/game_action_logic_entry.h"
#include "game_action/game_action_logic_table.h"
#include "game_action/game_action_manager.h"
#include "multiplayer/tcp_socket.h"
#include "multiplayer/tcp_socket_manager.h"
#include "process/process.h"
#include "process/process_manager.h"
#include "serialization/hashing.h"
#include "serialization/serialization_header.h"
#include "serialization/serialized_field.h"
#include "world/local_space_manager.h"

static inline
Serialized_Field *get_ps_entity_of__client(
        Client *p_client) {
    return &p_client->s_entity_of__client;
}

void initialize_client(
        Client *p_client,
        Identifier__u32 uuid__u32,
        Global_Space_Vector__3i32 global_space_vector__3i32) {
    initialize_serialization_header(
            &p_client->_serialization_header, 
            uuid__u32, 
            sizeof(Client));

    initialize_game_action_manager(
            get_p_game_action_manager__inbound_from__client(
                p_client));
    initialize_game_action_manager(
            get_p_game_action_manager__outbound_from__client(
                p_client));

    initialize_local_space_manager(
            get_p_local_space_manager_from__client(p_client), 
            global_space_vector__3i32);

    initialize_serialized_field_as__unassigned(
            get_ps_entity_of__client(p_client));
}

bool release_game_action_from__client(
        Client *p_client,
        Game_Action *p_game_action) {
    if (is_game_action__inbound(p_game_action)) {
        return release_game_action_from__game_action_manager(
                get_p_game_action_manager__inbound_from__client(p_client), 
                p_game_action);
    } 

    return release_game_action_from__game_action_manager(
            get_p_game_action_manager__outbound_from__client(p_client), 
            p_game_action);
}

void set_entity_of__client(
        Client *p_client,
        Entity *p_entity) {
    initialize_serialized_field(
            get_ps_entity_of__client(p_client), 
            p_entity, 
            p_entity->_serialization_header.uuid);
}

bool receive_game_action_for__client(
        Client *p_client,
        Game *p_game,
        Game_Action *p_game_action) {

    Process_Manager *p_process_manager =
        get_p_process_manager_from__game(p_game);
    Game_Action_Logic_Table *p_game_action_logic_table =
        get_p_game_action_logic_table_from__game(p_game);

    Game_Action_Logic_Entry *p_game_action_logic_entry =
        get_p_game_action_logic_entry_by__game_action_kind(
                p_game_action_logic_table, 
                get_kind_of__game_action(p_game_action));
    if (!p_game_action_logic_entry) {
        debug_error("receive_game_action_for__client, unsupported game action.");
        return false;
    }

    p_game_action->uuid_of__client__u32 =
        GET_UUID_P(p_client);

    santize_game_action__inbound(
            p_game_action_logic_entry, 
            p_game_action);

    Game_Action_Manager *p_game_action_manager__outbound =
        get_p_game_action_manager__outbound_from__client(p_client);

    // responding game actions are --NEVER-- allocated a process.
    if (is_game_action__responding_to_another__game_action(
                p_game_action)) {
        Process process;
        initialize_process_as__empty_process(
                &process);

        Game_Action *p_game_action__responded_to =
            get_p_game_action_by__uuid_from__game_action_manager(
                    p_game_action_manager__outbound, 
                    p_game_action->uuid_of__game_action__responding_to);

        if (!p_game_action__responded_to) {
            debug_error("receive_game_action_for__client, failed to find responding action.");
            return false;
        }

        // TODO: make process of responded game action, if it's flag is set to do so.
        //      however, is it needed? Can't we just make the process on invocation and wait?

        process.p_process_data = p_game_action;

        m_Process m_process_of__game_action =
            get_m_process__inbound_for__this_game_action_kind(
                    p_game_action_logic_table, 
                    p_game_action->the_kind_of_game_action__this_action_is);

        if (m_process_of__game_action)
            m_process_of__game_action(&process, p_game);
        return false;
    }

    if (is_game_action__with_process(p_game_action)) {
        Game_Action *p_game_action__allocated = 0;
        if (!is_game_action__allocated(p_game_action)) {
            p_game_action__allocated =
                allocate_as__copy_of__game_action_with__this_uuid_from__manager(
                        get_p_game_action_manager__inbound_from__client(
                            p_client),
                        p_game_action,
                        GET_UUID_P(p_game_action));
            if (!p_game_action__allocated) {
                debug_error("receive_game_action_for__client, failed to copy p_game_action.");
                return false;
            }
            p_game_action = p_game_action__allocated;
        }
        Process *p_process = dispatch_game_action_process__inbound(
                p_game_action_logic_table, 
                p_process_manager, 
                p_game_action__allocated);

        if (!p_process) {
            debug_error("receive_game_action_for__client, failed to allocate p_process.");
            (void)release_game_action_from__game_action_manager(
                    get_p_game_action_manager__inbound_from__client(p_client), 
                    p_game_action__allocated);
            return false;
        }
        return true;
    }

    if (get_m_process__inbound_of__game_action_logic_entry(
                p_game_action_logic_entry)) {
        Process process;
        initialize_process_as__empty_process(&process);
        process.p_process_data = p_game_action;

        m_Process m_process_of__game_action =
            get_m_process__inbound_for__this_game_action_kind(
                    p_game_action_logic_table, 
                    p_game_action
                        ->the_kind_of_game_action__this_action_is);

        if (m_process_of__game_action)
            m_process_of__game_action(
                    &process, p_game);
    }
    return true;
}

bool dispatch_game_action_for__client(
        Client *p_client,
        Game *p_game,
        TCP_Socket_Manager *p_tcp_socket_manager,
        Game_Action *p_game_action) {

    Process_Manager *p_process_manager =
        get_p_process_manager_from__game(p_game);
    Game_Action_Logic_Table *p_game_action_logic_table =
        get_p_game_action_logic_table_from__game(p_game);

    if (!p_game_action) {
        debug_error("dispatch_game_action_for__client, p_game_action is null.");
        return false;
    }

    Game_Action_Logic_Entry *p_game_action_logic_entry =
        get_p_game_action_logic_entry_by__game_action_kind(
                p_game_action_logic_table, 
                get_kind_of__game_action(p_game_action));

    if (!p_game_action_logic_entry) {
        debug_error("dispatch_game_action_for__client, unsupported game action.");
        return false;
    }

    santize_game_action__outbound(
            p_game_action_logic_entry, 
            p_game_action);

    p_game_action->uuid_of__client__u32 =
        GET_UUID_P(p_client);

    if (is_game_action__with_process(p_game_action)) {
        Game_Action *p_game_action__allocated = 0;
        if (!is_game_action__allocated(p_game_action)) {
            p_game_action__allocated =
                allocate_as__copy_of__game_action_from__game_action_manager(
                        get_p_game_action_manager__outbound_from__client(
                            p_client),
                        p_game_action);
            if (!p_game_action__allocated) {
                debug_error("dispatch_game_action_for__client, failed to copy p_game_action.");
                return false;
            }
            p_game_action = p_game_action__allocated;
        }
        if (is_game_action__processed_on__invocation_or__respose(p_game_action)) {
            Process *p_process =
                dispatch_game_action_process__outbound(
                        p_game_action_logic_table, 
                        p_process_manager, 
                        p_game_action__allocated);

            if (!p_process) {
                debug_error("dispatch_game_action_for__client, failed to allocate process.");
                release_game_action_from__game_action_manager(
                        get_p_game_action_manager__outbound_from__client(p_client), 
                        p_game_action__allocated);
                return false;
            }
        }
    } else if (
            get_m_process__outbound_of__game_action_logic_entry(
                p_game_action_logic_entry)) {
        Process process;
        initialize_process_as__empty_process(&process);
        process.p_process_data = p_game_action;

        m_Process m_process_of__game_action =
            get_m_process__outbound_for__this_game_action_kind(
                    p_game_action_logic_table, 
                    p_game_action
                        ->the_kind_of_game_action__this_action_is);

        if (m_process_of__game_action)
            m_process_of__game_action(
                    &process, p_game);
    } 

    if (!p_tcp_socket_manager
            || is_game_action__local(p_game_action)) {
        return true;
    }

    TCP_Socket *p_tcp_socket =
        get_p_tcp_socket_for__this_uuid(
                p_tcp_socket_manager, 
                p_client->_serialization_header.uuid);

    if (!p_tcp_socket) {
        debug_abort("dispatch_game_action_for__client, p_tcp_socket == 0.");
        return false;
    }

    send_bytes_over__tcp_socket(
            p_tcp_socket, 
            (u8*)p_game_action, 
            sizeof(Game_Action));
    return true;
}

