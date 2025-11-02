#include "game_action/core/entity/game_action__entity__spawn.h"
#include "defines.h"
#include "entity/entity.h"
#include "game_action/core/entity/game_action__entity__get.h"
#include "defines_weak.h"
#include "entity/entity_manager.h"
#include "game.h"
#include "game_action/game_action.h"
#include "game_action/game_action_logic_entry.h"
#include "game_action/game_action_logic_table.h"
#include "process/process.h"
#include "types/implemented/game_action_kind.h"

void m_process__game_action__entity__spawn__inbound_client(
        Process *p_this_process,
        Game *p_game) {
    Game_Action *p_game_action =
       (Game_Action*)p_this_process->p_process_data;
    Entity *p_entity =
       get_p_entity_by__uuid_from__entity_manager(
               get_p_entity_manager_from__game(p_game), 
               p_game_action->ga_kind__entity__uuid);

    if (p_entity) {
        // assume the local entity data got corrupted
        release_entity_from__entity_manager(
                p_game, 
                get_p_world_from__game(p_game), 
                get_p_entity_manager_from__game(p_game), 
                p_entity);
    }

    dispatch_game_action__entity__get(
            p_game,
            p_game_action->ga_kind__entity__uuid);
    complete_process(p_this_process);
}

void m_process__game_action__entity__spawn__outbound_server(
        Process *p_this_process,
        Game *p_game) {
    Game_Action *p_game_action =
       (Game_Action*)p_this_process->p_process_data;
    Entity *p_entity =
       get_p_entity_by__uuid_from__entity_manager(
               get_p_entity_manager_from__game(p_game), 
               p_game_action->ga_kind__entity__uuid);

    if (p_entity) {
        debug_error("m_process__game_action__entity__spawn__outbound_server, p_entity already allocated for this uuid.");
        fail_process(p_this_process);
        return;
    }

    p_entity =
        allocate_entity_in__entity_manager(
                p_game, 
                get_p_world_from__game(p_game), 
                get_p_entity_manager_from__game(p_game), 
                p_game_action->ga_kind__entity__the_kind_of__entity);

    if (!p_entity) {
        debug_error("m_process__game_action__entity__spawn__outbound_server, failed to allocate entity.");
        fail_process(p_this_process);
        return;
    }

    complete_process(p_this_process);
}

void register_game_action__entity__spawn_for__server(
        Game_Action_Logic_Table *p_game_action_logic_table) {
    initialize_game_action_logic_entry_as__broadcast__server(
            get_p_game_action_logic_entry_by__game_action_kind(
                p_game_action_logic_table, 
                Game_Action_Kind__Entity__Spawn),
            PROCESS_PRIORITY__0_MAXIMUM,
            m_process__game_action__entity__spawn__outbound_server,
            PROCESS_FLAGS__NONE);
}

void register_game_action__entity__spawn_for__client(
        Game_Action_Logic_Table *p_game_action_logic_table) {
    initialize_game_action_logic_entry(
            get_p_game_action_logic_entry_by__game_action_kind(
                p_game_action_logic_table, 
                Game_Action_Kind__Entity__Spawn), 
            GAME_ACTION_FLAGS__OUTBOUND_SANITIZE,
            GAME_ACTION_FLAG_MASK__OUTBOUND_SANITIZE,
            GAME_ACTION_FLAGS__INBOUND_SANITIZE
            | GAME_ACTION_FLAGS__BIT_IS_WITH_PROCESS
            | GAME_ACTION_FLAGS__BIT_IS_PROCESSED_ON_INVOCATION_OR_RESPONSE
            | GAME_ACTION_FLAGS__BIT_IS_LOCAL,
            GAME_ACTION_FLAG_MASK__INBOUND_SANITIZE,
            PROCESS_PRIORITY__0_MAXIMUM,
            0,
            0,
            m_process__game_action__entity__spawn__inbound_client, 
            PROCESS_FLAGS__NONE);
}

void initialize_game_action_for__entity__spawn(
        Game_Action *p_game_action,
        Identifier__u32 uuid_of__target__u32,
        Entity_Kind the_kind_of__entity) {
    initialize_game_action(p_game_action);
    set_the_kind_of__game_action(
            p_game_action, 
            Game_Action_Kind__Entity__Spawn);
    p_game_action->ga_kind__entity__uuid = uuid_of__target__u32;
    p_game_action->ga_kind__entity__the_kind_of__entity = the_kind_of__entity;
}

