#include "game_action/core/entity/game_action__entity__get.h"
#include "defines.h"
#include "defines_weak.h"
#include "entity/entity.h"
#include "entity/entity_manager.h"
#include "game.h"
#include "game_action/core/game_action__bad_request.h"
#include "game_action/game_action.h"
#include "game_action/game_action_logic_entry.h"
#include "game_action/game_action_logic_table.h"
#include "process/game_action_process.h"
#include "process/process.h"
#include "process/tcp_game_action_process.h"
#include "types/implemented/entity_data.h"
#include "types/implemented/game_action_kind.h"
#include "world/world.h"

void m_process__game_action__entity__get__inbound_server(
        Process *p_this_process,
        Game *p_game) {
    Game_Action *p_game_action =
        (Game_Action*)p_this_process->p_process_data;
    Entity *p_entity =
        get_p_entity_by__uuid_from__entity_manager(
                get_p_entity_manager_from__game(p_game), 
                p_game_action->ga_kind__entity__uuid);

    if (!p_entity) {
        dispatch_game_action__bad_request(
                p_game, 
                p_game_action, 
                0); // TODO code
        debug_error("m_process__game_action__entity__get__inbound_server, p_entity == 0.");
        fail_process(p_this_process);
        return;
    }

    switch (poll_game_action_process__tcp_delivery(
                p_game, 
                p_game_action->uuid_of__client__u32,
                p_game_action->_serialiation_header.uuid, 
                (u8*)&p_entity->entity_data, 
                sizeof(Entity_Data), 
                p_game_action
                    ->ga_kind__entity__get__entity_data_payload_bitmap, 
                (u16)TCP_PAYLOAD_BITMAP__QUANTITY_OF__PAYLOADS(Entity_Data))) {
        case PLATFORM_Write_File_Error__Max_Size_Reached:
            break;
        case PLATFORM_Write_File_Error__System_Busy:
            return;
        default:
            debug_error("m_process__game_action__entity__get__inbound_server, failed to send packets.");
            fail_process(p_this_process);
            return;
    }

    debug_info("m_process__game_action__entity__get__inbound_client, sent entity");
    complete_process(p_this_process);
}

void m_process__game_action__entity__get__inbound_server__init(
        Process *p_this_process,
        Game *p_game) {
    Game_Action *p_game_action =
        (Game_Action*)p_this_process->p_process_data;

    memset(
            p_game_action
            ->ga_kind__entity__get__entity_data_payload_bitmap,
            0,
            sizeof(p_game_action
                ->ga_kind__entity__get__entity_data_payload_bitmap));

    p_this_process->m_process_run__handler =
        m_process__game_action__entity__get__inbound_server;
}

void m_process__game_action__entity__get__outbound_client(
        Process *p_this_process,
        Game *p_game) {
    Serialization_Request *p_serialization_request =
        (Serialization_Request*)p_this_process->p_process_data;
    Game_Action *p_game_action =
        (Game_Action*)p_serialization_request->p_data;
    Entity *p_entity =
        get_p_entity_by__uuid_from__entity_manager(
                get_p_entity_manager_from__game(p_game), 
                p_game_action->ga_kind__entity__uuid);

    if (!p_entity) {
        debug_error("m_process__game_action__entity__get__outbound_client, p_entity == 0.");
        fail_process(p_this_process);
        return;
    }

    switch (poll_game_action_process__tcp_delivery(
                p_game, 
                p_game_action->uuid_of__client__u32,
                p_game_action->_serialiation_header.uuid, 
                (u8*)&p_entity->entity_data, 
                sizeof(Entity_Data), 
                p_game_action
                    ->ga_kind__entity__get__entity_data_payload_bitmap, 
                (u16)TCP_PAYLOAD_BITMAP__QUANTITY_OF__PAYLOADS(Entity_Data))) {
        case PLATFORM_Write_File_Error__Max_Size_Reached:
            break;
        case PLATFORM_Write_File_Error__System_Busy:
            return;
        default:
            debug_error("m_process__game_action__entity__get__outbound_client, failed to get packets.");
            fail_process(p_this_process);
            return;
    }

    debug_info("m_process__game_action__entity__get__inbound_client, got entity");
    set_entity_as__enabled(p_entity);
    complete_process(p_this_process);
}

void m_process__game_action__entity__get__outbound_client__init(
        Process *p_this_process,
        Game *p_game) {
    Game_Action *p_game_action =
        (Game_Action*)p_this_process->p_process_data;
    Identifier__u32 uuid__u32 =
        p_game_action->ga_kind__entity__uuid;
    Entity *p_entity =
        get_p_entity_by__uuid_from__entity_manager(
                get_p_entity_manager_from__game(p_game), 
                uuid__u32);
    if (!p_entity) {
        p_entity = allocate_entity_with__this_uuid_in__entity_manager(
                p_game, 
                get_p_world_from__game(p_game), 
                get_p_entity_manager_from__game(p_game), 
                Entity_Kind__None, 
                uuid__u32);
        if (!p_entity) {
            debug_error("m_process__game_action__entity__get__outbound_client__init, failed to allocate entity.");
            fail_process(p_this_process);
            return;
        }
    }

    set_entity_as__disabled(p_entity);

    bool is_process__mutation_successful =
        set_game_action_process_as__tcp_payload_receiver(
                p_game, 
                p_this_process, 
                (u8 *)&p_entity->entity_data, 
                sizeof(Entity_Data));
    if (!is_process__mutation_successful) {
        debug_error("m_process__game_action__entity__get__outbound_client, failed to mutate process into tcp receiver.");
        release_entity_from__entity_manager(
                p_game, 
                get_p_world_from__game(p_game), 
                get_p_entity_manager_from__game(p_game), 
                p_entity);
        fail_process(p_this_process);
        return;
    }

    p_this_process->m_process_run__handler =
        m_process__game_action__entity__get__outbound_client;
}

void register_game_action__entity__get_for__server(
        Game_Action_Logic_Table *p_game_action_logic_table) {
    initialize_game_action_logic_entry(
            get_p_game_action_logic_entry_by__game_action_kind(
                p_game_action_logic_table, 
                Game_Action_Kind__Entity__Get), 
            GAME_ACTION_FLAGS__OUTBOUND_SANITIZE,
            GAME_ACTION_FLAG_MASK__OUTBOUND_SANITIZE,
            GAME_ACTION_FLAGS__INBOUND_SANITIZE
            | GAME_ACTION_FLAGS__BIT_IS_WITH_PROCESS
            | GAME_ACTION_FLAGS__BIT_IS_PROCESSED_ON_INVOCATION_OR_RESPONSE,
            GAME_ACTION_FLAG_MASK__INBOUND_SANITIZE,
            PROCESS_PRIORITY__0_MAXIMUM,
            0, 
            0,
            m_process__game_action__entity__get__inbound_server__init, 
            PROCESS_FLAGS__NONE);
}

void register_game_action__entity__get_for__client(
        Game_Action_Logic_Table *p_game_action_logic_table) {
    initialize_game_action_logic_entry(
            get_p_game_action_logic_entry_by__game_action_kind(
                p_game_action_logic_table, 
                Game_Action_Kind__Entity__Get), 
            GAME_ACTION_FLAGS__OUTBOUND_SANITIZE,
            GAME_ACTION_FLAG_MASK__OUTBOUND_SANITIZE,
            GAME_ACTION_FLAGS__INBOUND_SANITIZE
            | GAME_ACTION_FLAGS__BIT_IS_WITH_PROCESS
            | GAME_ACTION_FLAGS__BIT_IS_PROCESSED_ON_INVOCATION_OR_RESPONSE,
            GAME_ACTION_FLAG_MASK__INBOUND_SANITIZE,
            PROCESS_PRIORITY__0_MAXIMUM,
            m_process__game_action__entity__get__outbound_client__init, 
            PROCESS_FLAGS__NONE, 
            0,
            0);
}

void initialize_game_action_for__entity__get(
        Game_Action *p_game_action,
        Identifier__u32 uuid_of__target__u32) {
    initialize_game_action(p_game_action);
    set_the_kind_of__game_action(
            p_game_action, 
            Game_Action_Kind__Entity__Get);
    p_game_action->ga_kind__entity__uuid =
        uuid_of__target__u32;
}
