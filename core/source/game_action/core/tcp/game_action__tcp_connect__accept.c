#include "game_action/core/tcp/game_action__tcp_connect__accept.h"
#include "defines_weak.h"
#include "game_action/game_action.h"
#include "game_action/game_action_logic_entry.h"
#include "game_action/game_action_logic_table.h"

void register_game_action__tcp_connect__accept(
        Game_Action_Logic_Table *p_game_action_logic_table) {
    initialize_game_action_logic_entry_as__message(
            get_p_game_action_logic_entry_by__game_action_kind(
                p_game_action_logic_table, 
                Game_Action_Kind__TCP_Connect__Accept));
}

void initialize_game_action_for__tcp_connect__accept(
        Game_Action *p_game_action,
        Client *p_client) {
    initialize_game_action(p_game_action);
    set_the_kind_of__game_action(
            p_game_action, 
            Game_Action_Kind__TCP_Connect__Accept);
    p_game_action->uuid_of__client__u32 =
        GET_UUID_P(p_client);
}
