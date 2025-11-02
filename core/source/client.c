#include "client.h"
#include "collisions/collision_node.h"
#include "collisions/hitbox_aabb.h"
#include "collisions/hitbox_aabb_manager.h"
#include "defines.h"
#include "defines_weak.h"
#include "game.h"
#include "game_action/game_action.h"
#include "game_action/game_action_logic_entry.h"
#include "game_action/game_action_logic_table.h"
#include "game_action/game_action_manager.h"
#include "multiplayer/tcp_socket.h"
#include "multiplayer/tcp_socket_manager.h"
#include "platform.h"
#include "process/process.h"
#include "process/process_manager.h"
#include "serialization/hashing.h"
#include "serialization/serialization_header.h"
#include "serialization/serialized_field.h"
#include "world/chunk_vectors.h"
#include "world/global_space_manager.h"
#include "world/local_space.h"
#include "world/local_space_manager.h"
#include "world/world.h"

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
}

void m_process__teleport_client(
        Process *p_this_process,
        Game *p_game) {
    Client *p_client = 
        get_p_client_by__uuid_from__game(
                p_game, 
                p_this_process->process_valueA__i32);

    if (!p_client) {
        debug_warning("note, the following error results in the client hitbox being removed from world space:");
        debug_error("m_process__teleport_client, p_client == 0.");
        fail_process(p_this_process);
        return;
    }

    Hitbox_AABB *p_hitbox_of__client =
        get_p_hitbox_aabb_by__uuid_u32_from__hitbox_aabb_manager(
                get_p_hitbox_aabb_manager_from__game(p_game), 
                GET_UUID_P(p_client));

    if (!p_hitbox_of__client) {
        debug_warning("note, the following error results in the client hitbox being removed from world space:");
        debug_error("m_process__teleport_client, p_hitbox_of__client == 0.");
        fail_process(p_this_process);
        return;
    }

    Local_Space *p_local_space =
        get_p_local_space_by__3i32F4_from__local_space_manager(
                get_p_local_space_manager_from__client(p_client), 
                get_position_3i32F4_of__hitbox_aabb(p_hitbox_of__client));

    if (!p_local_space) {
        debug_warning("note, the following error results in the client hitbox being removed from world space:");
        debug_error("m_process__teleport_client, p_local_space == 0.");
        fail_process(p_this_process);
        return;
    }

    if (!is_local_space__active(p_local_space)) {
        return;
    }

    bool success =
        add_entry_to__collision_node(
            get_p_collision_node_pool_from__world(
                get_p_world_from__game(p_game)), 
            get_p_collision_node_from__local_space(p_local_space), 
            p_hitbox_of__client);

    if (success) {
        complete_process(p_this_process);
        return;
    }

    debug_warning("note, the following error results in the client hitbox being removed from world space:");
    debug_error("m_process__teleport_client, failed adding client hitbox as collision record.");
    fail_process(p_this_process);
}

Process *teleport_client(
        Game *p_game,
        Client *p_client,
        Vector__3i32F4 position__3i32F4) {
    Hitbox_AABB *p_hitbox_of__client =
        get_p_hitbox_aabb_by__uuid_u32_from__hitbox_aabb_manager(
                get_p_hitbox_aabb_manager_from__game(p_game), 
                GET_UUID_P(p_client));
    
    if (p_hitbox_of__client) {
        Local_Space *p_local_space =
            get_p_local_space_by__3i32F4_from__local_space_manager(
                    get_p_local_space_manager_from__client(p_client), 
                    get_position_3i32F4_of__hitbox_aabb(p_hitbox_of__client));
        if (p_local_space) {
            remove_entry_from__collision_node(
                    get_p_collision_node_pool_from__world(
                        get_p_world_from__game(p_game)),
                    get_p_collision_node_from__local_space(p_local_space), 
                    GET_UUID_P(p_hitbox_of__client));
        } else {
            debug_error("teleport_client, p_hitbox_of__client not found in local space.");
        }
        set_hitbox__position_with__3i32F4(
                p_hitbox_of__client, 
                position__3i32F4);
    }
    set_center_of__local_space_manager(
            get_p_local_space_manager_from__client(
                p_client), 
            p_game, 
            vector_3i32F4_to__chunk_vector_3i32(
                position__3i32F4));

    Process *p_process =
        run_process(
                get_p_process_manager_from__game(p_game), 
                m_process__teleport_client, 
                PROCESS_PRIORITY__0_MAXIMUM,
                PROCESS_FLAG__IS_CRITICAL);

    p_process->process_valueA__i32 =
        GET_UUID_P(p_client);

    return p_process;
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

    // If is server, and p_client is local client - do not send anything over TCP.
    if (is_game__server_or__client(p_game)
            && p_client 
            == get_p_local_client_by__from__game(p_game)) {
        return true; // do not tcp send to self
    }

    TCP_Socket *p_tcp_socket =
        get_p_tcp_socket_for__this_uuid(
                p_tcp_socket_manager, 
                p_client->_serialization_header.uuid);

    if (!p_tcp_socket) {
        debug_error("dispatch_game_action_for__client, p_tcp_socket == 0.");
        return false;
    }

    send_bytes_over__tcp_socket(
            p_tcp_socket, 
            (u8*)p_game_action, 
            sizeof(Game_Action));
    return true;
}

void m_process__deserialize_client__default(
        Process *p_this_process,
        Game *p_game) {
    Serialization_Request *p_serialization_request =
        (Serialization_Request*)p_this_process->p_process_data;
    Client *p_client =
        (Client*)p_serialization_request->p_data;

    Hitbox_AABB *p_hitbox_aabb =
        allocate_hitbox_aabb_from__hitbox_aabb_manager(
                get_p_hitbox_aabb_manager_from__game(
                    p_game), 
                GET_UUID_P(p_client));

    if (!p_hitbox_aabb) {
        debug_error("m_process__deserialize_client__default, failed to allocate p_hitbox_aabb for client.");
        fail_process(p_this_process);
        return;
    }

    Quantity__u32 expected_length_of__read = 0;
    Quantity__u32 length_of__read = 
        (expected_length_of__read = 
            sizeof(
                Hitbox_AABB));

    PLATFORM_Read_File_Error error = 
        PLATFORM_Read_File_Error__None;
    if (p_serialization_request->p_file_handler) {
        PLATFORM_read_file(
                get_p_PLATFORM_file_system_context_from__game(p_game), 
                (u8 *)p_hitbox_aabb, 
                &length_of__read, 
                1, 
                p_serialization_request->p_file_handler);
    } else {
        length_of__read = 0;    
    }

    if (length_of__read != expected_length_of__read) {
        // Assume that this is the first time the player is being loaded
        set_hitbox__position_with__3i32(
                p_hitbox_aabb, 
                VECTOR__3i32__0_0_0);
        error = 0;
    }

    if (error) {
        debug_error("m_process__deserialize_client__default, read file error: %d",
                error);
        fail_process(p_this_process);
        return;
    }

    set_client_as__active(p_client);
    complete_process(p_this_process);
}

void m_process__serialize_client__default(
        Process *p_this_process,
        Game *p_game) {
    Serialization_Request *p_serialization_request =
        (Serialization_Request*)p_this_process->p_process_data;
    Client *p_client =
        (Client*)p_serialization_request->p_data;

    Hitbox_AABB *p_hitbox_aabb =
        get_p_hitbox_aabb_by__uuid_u32_from__hitbox_aabb_manager(
                get_p_hitbox_aabb_manager_from__game(p_game), 
                GET_UUID_P(p_client));

    if (!p_hitbox_aabb) {
        debug_error("m_process__serialize_client__default, client lacks hitbox component.");
        release_client_from__game(
                p_game,
                p_client);
        fail_process(p_this_process);
        return;
    }

    PLATFORM_Write_File_Error error =
        PLATFORM_write_file(
                get_p_PLATFORM_file_system_context_from__game(p_game), 
                (u8*)p_hitbox_aabb, 
                sizeof(Hitbox_AABB), 
                1, 
                p_serialization_request->p_file_handler);

    if (error) {
        debug_error("m_process__serialize_client__default, write error: %d",
                error);
        release_client_from__game(
                p_game,
                p_client);
        fail_process(p_this_process);
        return;
    }
    
    complete_process(p_this_process);
    return;
}
