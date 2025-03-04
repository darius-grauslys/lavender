#include "defines_weak.h"
#include "game_action/game_action_logic_entry.h"
#include "game_action/game_action_logic_table.h"
#include "game_action/implemented/global_space/game_action__global_space__request.h"
#include "process/game_action_process.h"

void m_process__game_action__global_space__request__outbound_offline(
        Process *p_this_process,
        Game *p_game) {
    Game_Action *p_game_action =
        (Game_Action*)p_this_process->p_process_data;
    dispatch_game_action__global_space__request(
            p_game, 
            p_game_action->ga_kind__global_space__request__gsv_3i32);
    complete_game_action_process(
            p_game,
            p_this_process);
}

void register_game_action__global_space__request_for__offline(
        Game_Action_Logic_Table *p_game_action_logic_table) {
    initialize_game_action_logic_entry_as__process__out(
            get_p_game_action_logic_entry_by__game_action_kind(
                p_game_action_logic_table, 
                Game_Action_Kind__Global_Space__Request), 
            m_process__game_action__global_space__request__outbound_offline, 
            PROCESS_FLAG__IS_CRITICAL);
}
