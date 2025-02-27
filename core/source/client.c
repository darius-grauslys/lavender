#include "client.h"
#include "defines.h"
#include "defines_weak.h"
#include "game.h"
#include "game_action/game_action.h"
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

void release_game_action_from__client(
        Client *p_client,
        Game_Action *p_game_action) {
    if (is_game_action__inbound(p_game_action)) {
        release_game_action_from__game_action_manager(
                get_p_game_action_manager__inbound_from__client(p_client), 
                p_game_action);
        return;
    } 

    release_game_action_from__game_action_manager(
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

void receive_game_action_for__client(
        Client *p_client,
        Game *p_game,
        Game_Action *p_game_action) {

    Process_Manager *p_process_manager =
        get_p_process_manager_from__game(p_game);
    Game_Action_Logic_Table *p_game_action_logic_table =
        get_p_game_action_logic_table_from__game(p_game);
    // received game actions are --NEVER-- processed.
    if (!is_game_action__responding_to_another__game_action(
                p_game_action)) {
        m_Process m_process_of__game_action =
            get_m_process_for__this_game_action_kind(
                    p_game_action_logic_table, 
                    p_game_action->the_kind_of_game_action__this_action_is);

        if (m_process_of__game_action)
            m_process_of__game_action(0, p_game);
        return;
    }

    Game_Action_Manager *p_game_action_manager__outbound =
        get_p_game_action_manager__outbound_from__client(p_client);

    Game_Action *p_game_action__responded_to =
        (Game_Action*)dehash_identitier_u32_in__contigious_array(
                (Serialization_Header*)
                p_game_action_manager__outbound->game_actions, 
                MAX_QUANTITY_OF__GAME_ACTIONS, 
                p_game_action->_serialiation_header.uuid);

    if (!p_game_action__responded_to) {
        goto cleanup;
    }

    if (is_game_action__with_process(p_game_action)) {
        if (is_game_action__processed_on__invocation_or__respose(
                    p_game_action__responded_to)) {
            Process *p_process = get_p_process_by__uuid(
                    p_process_manager, 
                    p_game_action__responded_to->_serialiation_header.uuid); 
            if (!p_process)
                goto release_response;
            p_process->p_process_data__response =
                p_game_action;
            // keep p_game_action alive.
            return;
        }

        Process *p_process = dispatch_game_action_process(
                p_game_action_logic_table, 
                p_process_manager, 
                p_game_action__responded_to);

        if (!p_process) {
            debug_error("receive_game_action, failed to allocate p_process.");
            goto cleanup;
        }
        p_process->p_process_data__response =
            p_game_action;
        // keep p_game_action alive.
        return;
    } else {
release_response:
        release_game_action_from__game_action_manager(
                get_p_game_action_manager__outbound_from__client(p_client), 
                p_game_action__responded_to);
    }

cleanup:
    if (is_game_action__allocated(p_game_action)) {
        release_game_action_from__game_action_manager(
                get_p_game_action_manager__inbound_from__client(p_client), 
                p_game_action);
    }
}

void dispatch_game_action_for__client(
        Client *p_client,
        Game *p_game,
        Game_Action *p_game_action) {

    Process_Manager *p_process_manager =
        get_p_process_manager_from__game(p_game);
    Game_Action_Logic_Table *p_game_action_logic_table =
        get_p_game_action_logic_table_from__game(p_game);
    TCP_Socket_Manager *p_tcp_socket_manager =
        get_p_tcp_socket_manager_from__game(p_game);

    if (!p_game_action) {
        debug_error("dispatch_game_action, p_game_action is null.");
        return;
    }

    if (is_game_action__with_process(p_game_action)) {
        if (is_game_action__processed_on__invocation_or__respose(p_game_action)) {
            Process *p_process =
                dispatch_game_action_process(
                        p_game_action_logic_table, 
                        p_process_manager, 
                        p_game_action);

            if (!p_process) {
                debug_error("dispatch_game_action, failed to allocate process.");
                release_game_action_from__client(p_client, p_game_action);
                return;
            }
        }
    } else if (!p_tcp_socket_manager) {
        // we are in offline mode, dispatch the process immediately.
        m_Process m_process_of__game_action =
            get_m_process_for__this_game_action_kind(
                    p_game_action_logic_table, 
                    p_game_action
                        ->the_kind_of_game_action__this_action_is);

        if (m_process_of__game_action)
            m_process_of__game_action(
                    0, p_game);
    } 

    if (!p_tcp_socket_manager) {
        return;
    }

    TCP_Socket *p_tcp_socket =
        get_p_tcp_socket_for__this_client(
                p_tcp_socket_manager, 
                p_client);

    if (!p_tcp_socket) {
        debug_abort("dispatch_game_action, p_tcp_socket == 0.");
        return;
    }

    send_bytes_over__tcp_socket(
            p_tcp_socket, 
            (u8*)p_game_action, 
            sizeof(Game_Action));
}

Game_Action *allocate_game_action_from__client(
        Client *p_client,
        Game_Action_Flags game_action_flags) {
    game_action_flags &=
        ~GAME_ACTION_FLAGS__BIT_IS_ALLOCATED;

    Game_Action_Manager *p_game_action_manager =
        (game_action_flags & GAME_ACTION_FLAGS__BIT_IS_OUT_OR__IN_BOUND)
        ? get_p_game_action_manager__outbound_from__client(p_client)
        : get_p_game_action_manager__inbound_from__client(p_client)
        ;

    Game_Action *p_game_action =
        allocate_game_action_from__game_action_manager(
                p_game_action_manager);

    if (p_game_action) {
        p_game_action->game_action_flags = game_action_flags;
        p_game_action->uuid_of__client__u32 =
            p_client->_serialization_header.uuid;
    }

    return p_game_action;
}
