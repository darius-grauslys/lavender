#ifndef GAME_ACTION__REGISTRAR_H
#define GAME_ACTION__REGISTRAR_H

#include "defines.h"

void register_game_actions__offline(
        Game_Action_Logic_Table *p_game_action_logic_table);
void register_game_actions__client(
        Game_Action_Logic_Table *p_game_action_logic_table);
void register_game_actions__server(
        Game_Action_Logic_Table *p_game_action_logic_table);

#endif
