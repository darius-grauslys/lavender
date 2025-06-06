#ifndef GAME_ACTION_LOGIC_TABLE_H
#define GAME_ACTION_LOGIC_TABLE_H

#include "defines.h"
#include "defines_weak.h"
#include "game_action/game_action.h"
#include "game_action/game_action_logic_entry.h"
#include "types/implemented/game_action_kind.h"

static inline
Game_Action_Logic_Entry *get_p_game_action_logic_entry_by__game_action_kind(
        Game_Action_Logic_Table *p_game_action_logic_table,
        Game_Action_Kind the_kind_of__game_action) {
    if (the_kind_of__game_action >= Game_Action_Kind__Unknown) {
        return 0;
    }
    return &p_game_action_logic_table->game_action_logic_entries[
        the_kind_of__game_action];
}

void initialize_game_action_logic_table(
        Game_Action_Logic_Table *p_game_action_logic_table);

Process *dispatch_game_action_process(
        Process_Manager *p_process_manager,
        Game_Action *p_game_action,
        m_Process m_process__game_action,
        Process_Flags__u8 process_flags__u8);

Process *dispatch_game_action_process__outbound(
        Game_Action_Logic_Table *p_game_action_logic_table,
        Process_Manager *p_process_manager,
        Game_Action *p_game_action);

Process *dispatch_game_action_process__inbound(
        Game_Action_Logic_Table *p_game_action_logic_table,
        Process_Manager *p_process_manager,
        Game_Action *p_game_action);

m_Process get_m_process__outbound_for__this_game_action_kind(
        Game_Action_Logic_Table *p_game_action_logic_table,
        Game_Action_Kind the_kind_of__game_action);

m_Process get_m_process__inbound_for__this_game_action_kind(
        Game_Action_Logic_Table *p_game_action_logic_table,
        Game_Action_Kind the_kind_of__game_action);

#endif
