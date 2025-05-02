#include "game_action/core/game_action__bad_request.h"
#include "client.h"
#include "defines_weak.h"
#include "game.h"
#include "game_action/game_action.h"
#include "game_action/game_action_logic_entry.h"
#include "game_action/game_action_logic_table.h"
#include "game_action/game_action_manager.h"
#include "process/game_action_process.h"
#include "serialization/serialization_header.h"

void m_process__game_action__bad_request__inbound(
        Process *p_this_process,
        Game *p_game) {
    Game_Action *p_game_action__bad_request =
        (Game_Action*)p_this_process->p_process_data;
    Client *p_client =
        get_p_client_by__uuid_from__game(
                p_game,
                get_client_uuid_from__game_action(p_game_action__bad_request));
    Game_Action *p_game_action__responding_to =
        get_p_game_action_by__uuid_from__game_action_manager(
                get_p_game_action_manager__outbound_from__client(
                    p_client), 
                p_game_action__bad_request
                ->uuid_of__game_action__responding_to);
    
    if (!p_game_action__responding_to) {
        complete_process(p_this_process);
        return;
    }

    set_game_action_as__bad_request(
            p_game_action__responding_to);

    complete_process(p_this_process);
}

void register_game_action__bad_request(
        Game_Action_Logic_Table *p_game_action_logic_table) {
    initialize_game_action_logic_entry(
            get_p_game_action_logic_entry_by__game_action_kind(
                p_game_action_logic_table, 
                Game_Action_Kind__Bad_Request), 
            GAME_ACTION_FLAGS__OUTBOUND_SANITIZE,
            GAME_ACTION_FLAG_MASK__OUTBOUND_SANITIZE,
            GAME_ACTION_FLAGS__INBOUND_SANITIZE,
            GAME_ACTION_FLAG_MASK__INBOUND_SANITIZE,
            0, 
            PROCESS_FLAGS__NONE,
            m_process__game_action__bad_request__inbound, 
            PROCESS_FLAGS__NONE);
}

void initialize_game_action_for__bad_request(
        Game_Action *p_game_action,
        Game_Action *p_game_action__responding_to,
        u32 bad_request__code__u32) {
    initialize_game_action(p_game_action);
    set_the_kind_of__game_action(
            p_game_action, 
            Game_Action_Kind__Bad_Request);
    p_game_action->uuid_of__client__u32 =
        get_client_uuid_from__game_action(p_game_action__responding_to);
    p_game_action->uuid_of__game_action__responding_to =
        GET_UUID_P(p_game_action__responding_to);
    p_game_action->ga_kind__bad_request__request_error_code =
        bad_request__code__u32;
}
