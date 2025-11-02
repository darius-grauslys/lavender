#ifndef GAME_ACTION__INPUT_H
#define GAME_ACTION__INPUT_H

#include "defines.h"
#include "game.h"

void register_game_action__input_for__server(
        Game_Action_Logic_Table *p_game_action_logic_table);

void register_game_action__input_for__client(
        Game_Action_Logic_Table *p_game_action_logic_table);

static inline
void register_game_action__input_for__offline(
        Game_Action_Logic_Table *p_game_action_logic_table) {
    // no-op.
    // not needed as input is driven locally
    // client register only exists for relaying inputs to server.
    // server drives client struct.
}

void initialize_game_action_for__input(
        Game_Action *p_game_action,
        Input *p_input);

static inline
bool dispatch_game_action__input(
        Game *p_game,
        Input *p_input) {
    Game_Action ga_resolve;
    initialize_game_action_for__input(
            &ga_resolve,
            p_input);
    return dispatch_game_action_to__server(
            p_game, 
            &ga_resolve);
}

#endif
