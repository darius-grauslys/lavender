#include "game_action/implemented/game_action__registrar.h"
#include "game_action/implemented/tcp/game_action__tcp_begin_connect.h"
#include "game_action/implemented/tcp/game_action__tcp_connect.h"
#include "game_action/implemented/tcp/game_action__tcp_connect__accept.h"
#include "game_action/implemented/tcp/game_action__tcp_connect__reject.h"
#include "game_action/implemented/tcp/game_action__tcp_delivery.h"

void register_game_actions__offline(
        Game_Action_Logic_Table *p_game_action_logic_table) {
    debug_warning("register_game_actions__offline, impl.");
}

void register_game_actions__client(
        Game_Action_Logic_Table *p_game_action_logic_table) {
    register_game_action__tcp_connect(
            p_game_action_logic_table);
    register_game_action__tcp_connect__begin(
            p_game_action_logic_table);
    register_game_action__tcp_connect__accept(
            p_game_action_logic_table);
    register_game_action__tcp_connect__reject(
            p_game_action_logic_table);
    register_game_action__tcp_delivery(
            p_game_action_logic_table);
    debug_warning("register_game_actions__client, impl.");
}

void register_game_actions__server(
        Game_Action_Logic_Table *p_game_action_logic_table) {
    register_game_action__tcp_connect(
            p_game_action_logic_table);
    register_game_action__tcp_connect__begin(
            p_game_action_logic_table);
    register_game_action__tcp_connect__accept(
            p_game_action_logic_table);
    register_game_action__tcp_connect__reject(
            p_game_action_logic_table);
    register_game_action__tcp_delivery(
            p_game_action_logic_table);
    debug_warning("register_game_actions__server, impl.");
}
