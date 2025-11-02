#include "game_action/core/input/game_action__input.h"
#include "client.h"
#include "defines.h"
#include "defines_weak.h"
#include "game.h"
#include "game_action/core/game_action__bad_request.h"
#include "game_action/game_action.h"
#include "game_action/game_action_logic_entry.h"
#include "game_action/game_action_logic_table.h"
#include "process/process.h"
#include "types/implemented/game_action_kind.h"
#include <string.h>

void m_process__game_action__input__inbound_server(
        Process *p_this_process,
        Game *p_game) {
    Game_Action *p_game_action =
        (Game_Action*)p_this_process->p_process_data;

    Client *p_client =
        get_p_client_by__uuid_from__game(
                p_game, 
                get_client_uuid_from__game_action(
                    p_game_action));

    if (!p_client) {
        debug_error("m_process__game_action__input__inbound_server, p_client == 0.");
        dispatch_game_action__bad_request(
                p_game, 
                p_game_action, 
                0); // TODO: bad request code
        fail_process(p_this_process);
        return;
    }

    copy_input_into__client(
            p_client, 
            &p_game_action
            ->ga_kind__input__input);

    complete_process(p_this_process);
}

void register_game_action__input_for__server(
        Game_Action_Logic_Table *p_game_action_logic_table) {
    initialize_game_action_logic_entry(
            get_p_game_action_logic_entry_by__game_action_kind(
                p_game_action_logic_table, 
                Game_Action_Kind__Input), 
            GAME_ACTION_FLAGS__OUTBOUND_SANITIZE
            | GAME_ACTION_FLAGS__BIT_IS_LOCAL,
            GAME_ACTION_FLAG_MASK__OUTBOUND_SANITIZE,
            GAME_ACTION_FLAGS__INBOUND_SANITIZE,
            GAME_ACTION_FLAG_MASK__INBOUND_SANITIZE,
            PROCESS_PRIORITY__0_MAXIMUM,
            0, 
            PROCESS_FLAGS__NONE,
            m_process__game_action__input__inbound_server, 
            PROCESS_FLAGS__NONE);
}

void register_game_action__input_for__client(
        Game_Action_Logic_Table *p_game_action_logic_table) {
    initialize_game_action_logic_entry(
            get_p_game_action_logic_entry_by__game_action_kind(
                p_game_action_logic_table, 
                Game_Action_Kind__Input), 
            GAME_ACTION_FLAGS__OUTBOUND_SANITIZE,
            GAME_ACTION_FLAG_MASK__OUTBOUND_SANITIZE,
            GAME_ACTION_FLAGS__INBOUND_SANITIZE,
            GAME_ACTION_FLAG_MASK__INBOUND_SANITIZE,
            PROCESS_PRIORITY__0_MAXIMUM,
            0, 
            PROCESS_FLAGS__NONE,
            0, 
            PROCESS_FLAGS__NONE);
}

void initialize_game_action_for__input(
        Game_Action *p_game_action,
        Input *p_input) {
    initialize_game_action(p_game_action);
    set_the_kind_of__game_action(
            p_game_action, 
            Game_Action_Kind__Input);
#ifdef SECURITY_0
    ///
    /// Don't relay mouse positions as it can identify
    /// the client's window size.
    ///
    p_game_action->ga_kind__input__input.input_flags__held =
        p_input->input_flags__held;
    p_game_action->ga_kind__input__input.input_flags__held =
        p_input->input_flags__pressed;
    p_game_action->ga_kind__input__input.input_flags__held =
        p_input->input_flags__pressed_old;
    p_game_action->ga_kind__input__input.input_flags__held =
        p_input->input_flags__released;
#else
    p_game_action->ga_kind__input__input =
        *p_input;
#endif
}

