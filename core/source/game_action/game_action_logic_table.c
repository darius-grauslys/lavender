#include "game_action/game_action_logic_table.h"
#include "defines.h"
#include "defines_weak.h"
#include "process/process_manager.h"

void initialize_game_action_logic_table(
        Game_Action_Logic_Table *p_game_action_logic_table) {
    memset(p_game_action_logic_table,
            0,
            sizeof(Game_Action_Logic_Table));
}

Process *dispatch_game_action_process(
        Game_Action_Logic_Table *p_game_action_logic_table,
        Process_Manager *p_process_manager,
        Game_Action *p_game_action) {
    Game_Action_Kind the_kind_of__game_action = 
        p_game_action->the_kind_of_game_action__this_action_is;
    if ((u32)the_kind_of__game_action > Game_Action_Kind__Unknown) {
        debug_error("dispatch_game_action_process, invalid game action kind.");
        return 0;
    }

    Game_Action_Logic_Entry *p_game_action_logic_entry =
        get_p_game_action_logic_entry_by__game_action_kind(
                p_game_action_logic_table, 
                the_kind_of__game_action);

    Process *p_process = run_process_with__uuid(
            p_process_manager, 
            p_game_action_logic_entry->m_process_of__game_action, 
            p_game_action->_serialiation_header.uuid,
            p_game_action_logic_entry->process_flags__u8);

    if (!p_process) {
        debug_error("dispatch_game_action_process, failed to allocate p_process.");
        return 0;
    }
    
    p_process->p_process_data = p_game_action;

    return p_process;
}

m_Process get_m_process_for__this_game_action_kind(
        Game_Action_Logic_Table *p_game_action_logic_table,
        Game_Action_Kind the_kind_of__game_action) {
    Game_Action_Logic_Entry *p_game_action_logic_entry =
        get_p_game_action_logic_entry_by__game_action_kind(
                p_game_action_logic_table, 
                the_kind_of__game_action);

    return p_game_action_logic_entry->m_process_of__game_action;
}
