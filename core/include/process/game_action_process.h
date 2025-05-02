#ifndef GAME_ACTION_PROCESS_H
#define GAME_ACTION_PROCESS_H

#include "defines.h"
#include "defines_weak.h"
#include "game.h"
#include "platform.h"
#include "process/process.h"
#include "game_action/game_action.h"

void initialize_process_as__game_action_process(
        Process *p_process,
        Game_Action *p_game_action);

bool set_game_action_process_as__tcp_payload_receiver(
        Game *p_game,
        Process *p_process,
        u8 *p_payload_destination,
        Quantity__u16 quantity_of__bytes_in__payload_destination);

void m_process__dispose_handler__game_action__default(
        Process *p_process,
        Game *p_game);

#endif
