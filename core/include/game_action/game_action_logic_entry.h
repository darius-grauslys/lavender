#ifndef GAME_ACTION_LOGIC_ENTRY_H
#define GAME_ACTION_LOGIC_ENTRY_H

#include "defines.h"

void santize_game_action__inbound(
        Game_Action_Logic_Entry *p_game_action_logic_entry,
        Game_Action *p_game_action);

void santize_game_action__outbound(
        Game_Action_Logic_Entry *p_game_action_logic_entry,
        Game_Action *p_game_action);

#endif
