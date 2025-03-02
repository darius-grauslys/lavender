#include "game_action/game_action_logic_entry.h"

void santize_game_action__inbound(
        Game_Action_Logic_Entry *p_game_action_logic_entry,
        Game_Action *p_game_action) {
    p_game_action->game_action_flags
        &= ~p_game_action_logic_entry
        ->game_action_flags__inbound_mask
        ;
    p_game_action->game_action_flags
        |= p_game_action_logic_entry
        ->game_action_flags__inbound
        ;
}

void santize_game_action__outbound(
        Game_Action_Logic_Entry *p_game_action_logic_entry,
        Game_Action *p_game_action) {
    p_game_action->game_action_flags
        &= ~p_game_action_logic_entry
        ->game_action_flags__outbound_mask
        ;
    p_game_action->game_action_flags
        |= p_game_action_logic_entry
        ->game_action_flags__outbound
        ;
}
