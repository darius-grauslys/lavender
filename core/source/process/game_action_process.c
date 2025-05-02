#include "process/game_action_process.h"
#include "game_action/game_action.h"
#include "defines.h"
#include "defines_weak.h"
#include "game.h"
#include "game_action/core/tcp/game_action__tcp_delivery.h"
#include "platform.h"
#include "process/process.h"
#include "serialization/serialization_request.h"

void m_process__dispose_handler__game_action__default(
        Process *p_process,
        Game *p_game) {
    Game_Action *p_game_action =
        (Game_Action*)p_process->p_process_data;
    if (p_game_action) {
        resolve_game_action(
                p_game, 
                GA_UUID_SOURCE(p_process->p_process_data),
                p_game_action);
    }
}

void initialize_process_as__game_action_process(
        Process *p_process,
        Game_Action *p_game_action) {
    set_process__dispose_handler(
            p_process, 
            m_process__dispose_handler__game_action__default);
    p_process->p_process_data = p_game_action;
}

