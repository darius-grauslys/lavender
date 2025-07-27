#include "game_action/game_action_logic_table.h"
#include "defines.h"
#include "defines_weak.h"
#include "game_action/game_action_logic_entry.h"
#include "process/game_action_process.h"
#include "process/process_manager.h"

void initialize_game_action_logic_table(
        Game_Action_Logic_Table *p_game_action_logic_table) {
    memset(p_game_action_logic_table,
            0,
            sizeof(Game_Action_Logic_Table));
}

Process *dispatch_game_action_process(
        Process_Manager *p_process_manager,
        Game_Action *p_game_action,
        m_Process m_process__game_action,
        Process_Priority__u8 process_priority__u8,
        Process_Flags__u8 process_flags__u8) {
    if (!m_process__game_action) {
        debug_error("dispatch_game_action_process, m_process__game_action == 0.");
        return 0;
    }

    Process *p_process = run_process_with__uuid(
            p_process_manager, 
            m_process__game_action, 
            p_game_action->_serialiation_header.uuid,
            process_priority__u8,
            process_flags__u8);

    if (!p_process) {
        debug_error("dispatch_game_action_process, failed to allocate p_process.");
        return 0;
    }
    
    initialize_process_as__game_action_process(
            p_process,
            p_game_action);

    return p_process;
}

Process *dispatch_game_action_process__outbound(
        Game_Action_Logic_Table *p_game_action_logic_table,
        Process_Manager *p_process_manager,
        Game_Action *p_game_action) {
    Game_Action_Logic_Entry *p_game_action_logic_entry =
        get_p_game_action_logic_entry_by__game_action_kind(
                p_game_action_logic_table, 
                get_kind_of__game_action(p_game_action));
    if (!p_game_action_logic_entry) {
        debug_error("dispatch_game_action_process__outbound, invalid game_action_kind.");
        return 0;
    }
    return dispatch_game_action_process(
            p_process_manager, 
            p_game_action, 
            get_m_process__outbound_of__game_action_logic_entry(
                p_game_action_logic_entry),
            get_process_priority__game_action_logic_entry(
                p_game_action_logic_entry),
            get_process_flags__outbound_of__game_action_logic_entry(
                p_game_action_logic_entry)
            );
}

Process *dispatch_game_action_process__inbound(
        Game_Action_Logic_Table *p_game_action_logic_table,
        Process_Manager *p_process_manager,
        Game_Action *p_game_action) {
    Game_Action_Logic_Entry *p_game_action_logic_entry =
        get_p_game_action_logic_entry_by__game_action_kind(
                p_game_action_logic_table, 
                get_kind_of__game_action(p_game_action));
    if (!p_game_action_logic_entry) {
        debug_error("dispatch_game_action_process__inbound, invalid game_action_kind.");
        return 0;
    }
    return dispatch_game_action_process(
            p_process_manager, 
            p_game_action, 
            get_m_process__inbound_of__game_action_logic_entry(
                p_game_action_logic_entry),
            get_process_priority__game_action_logic_entry(
                p_game_action_logic_entry),
            get_process_flags__inbound_of__game_action_logic_entry(
                p_game_action_logic_entry));
}

m_Process get_m_process__outbound_for__this_game_action_kind(
        Game_Action_Logic_Table *p_game_action_logic_table,
        Game_Action_Kind the_kind_of__game_action) {
    Game_Action_Logic_Entry *p_game_action_logic_entry =
        get_p_game_action_logic_entry_by__game_action_kind(
                p_game_action_logic_table, 
                the_kind_of__game_action);

    if (!p_game_action_logic_entry) {
        debug_error("get_m_process__outbound_for__this_game_action_kind, invalid game_action_kind.");
        return 0;
    }

    return get_m_process__outbound_of__game_action_logic_entry(
            p_game_action_logic_entry);
}

m_Process get_m_process__inbound_for__this_game_action_kind(
        Game_Action_Logic_Table *p_game_action_logic_table,
        Game_Action_Kind the_kind_of__game_action) {
    Game_Action_Logic_Entry *p_game_action_logic_entry =
        get_p_game_action_logic_entry_by__game_action_kind(
                p_game_action_logic_table, 
                the_kind_of__game_action);

    if (!p_game_action_logic_entry) {
        debug_error("get_m_process__inbound_for__this_game_action_kind, invalid game_action_kind.");
        return 0;
    }

    return get_m_process__inbound_of__game_action_logic_entry(
            p_game_action_logic_entry);
}
