#ifndef GAME_ACTION_PROCESS_H
#define GAME_ACTION_PROCESS_H

#include "defines.h"
#include "defines_weak.h"
#include "game.h"
#include "process/process.h"

///
/// NOTE: This is only valid to call if
/// p_process->p_process_data is to the
/// associated persisted game_action.
///
/// If this is not the case, call
/// finish_process(...) instead.
///
static inline
void complete_game_action_process(
        Game *p_game,
        Process *p_process) {
    Game_Action *p_game_action =
        (Game_Action*)p_process->p_process_data;
    resolve_game_action(
            p_game, 
            p_game_action);
    complete_process(p_process);
}

///
/// NOTE: This is only valid to call if
/// p_process->p_process_data is to the
/// associated persisted game_action.
///
/// If this is not the case, call
/// fail_process(...) instead.
///
static inline
void fail_game_action_process(
        Game *p_game,
        Process *p_process) {
    Game_Action *p_game_action =
        (Game_Action*)p_process->p_process_data;
    resolve_game_action(
            p_game, 
            p_game_action);
    fail_process(p_process);
}
#endif
