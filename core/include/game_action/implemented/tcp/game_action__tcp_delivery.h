#ifndef GAME_ACTION__TCP_DELIVER_H
#define GAME_ACTION__TCP_DELIVER_H

#include "defines.h"
#include "defines_weak.h"
#include "game.h"
#include "platform.h"

void register_game_action__tcp_delivery(
        Game_Action_Logic_Table *p_game_action_logic_table);

void initialize_game_action_for__tcp_delivery(
        Game_Action *p_game_action,
        Identifier__u32 uuid_of__client_to__send_to,
        Identifier__u32 uuid_to__respond,
        u8 *p_payload,
        u32 quantity_of__bytes_in__payload,
        Index__u16 index_of__payload);

static inline
void dispatch_game_action__tcp_delivery(
        Game *p_game,
        Identifier__u32 uuid_of__client_to__send_to,
        Identifier__u32 uuid_to__respond,
        u8 *p_payload,
        u32 quantity_of__bytes_in__payload,
        Index__u16 index_of__payload) {
    Game_Action ga_delivery;
    initialize_game_action_for__tcp_delivery(
            &ga_delivery,
            uuid_of__client_to__send_to,
            uuid_to__respond,
            p_payload,
            quantity_of__bytes_in__payload,
            index_of__payload);
    dispatch_game_action(
            p_game, 
            &ga_delivery);
}

#endif
