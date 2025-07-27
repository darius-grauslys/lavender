#include "game_action/game_action_logic_entry.h"
#include "defines.h"

void initialize_game_action_logic_entry(
        Game_Action_Logic_Entry *p_game_action_logic_entry,
        Game_Action_Flags game_action_flags__outbound,
        Game_Action_Flags game_action_flags__outbound_mask,
        Game_Action_Flags game_action_flags__inbound,
        Game_Action_Flags game_action_flags__inbound_mask,
        Process_Priority__u8 process_priority__u8,
        m_Process m_process__game_action__outbound,
        Process_Flags__u8 process_flags__outbound,
        m_Process m_process__game_action__inbound,
        Process_Flags__u8 process_flags__inbound) {

    p_game_action_logic_entry
        ->m_process_of__game_action__outbound =
        m_process__game_action__outbound;
    p_game_action_logic_entry
        ->m_process_of__game_action__inbound =
        m_process__game_action__inbound;
    p_game_action_logic_entry->game_action_flags__outbound =
        game_action_flags__outbound;
    p_game_action_logic_entry->game_action_flags__outbound_mask =
        game_action_flags__outbound_mask;
    p_game_action_logic_entry->game_action_flags__inbound =
        game_action_flags__inbound;
    p_game_action_logic_entry->game_action_flags__inbound_mask =
        game_action_flags__inbound_mask;
    p_game_action_logic_entry
        ->process_flags_of__game_action__outbound =
        process_flags__outbound;
    p_game_action_logic_entry
        ->process_flags_of__game_action__inbound =
        process_flags__inbound;
    p_game_action_logic_entry
        ->process_priority__u8 = process_priority__u8;
}

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
