#ifndef GAME_ACTION__HITBOX_H
#define GAME_ACTION__HITBOX_H

#include "defines.h"
#include "defines_weak.h"
#include "game.h"

void register_game_action__hitbox_for__server(
        Game_Action_Logic_Table *p_game_action_logic_table);

static inline
void register_game_action__hitbox_for__offline(
        Game_Action_Logic_Table *p_game_action_logic_table) {
    register_game_action__hitbox_for__server(
            p_game_action_logic_table);
}

void register_game_action__hitbox_for__client(
        Game_Action_Logic_Table *p_game_action_logic_table);

void initialize_game_action_for__hitbox(
        Game_Action *p_game_action,
        Identifier__u32 uuid_of__target__u32,
        Vector__3i32F4 position__3i32F4,
        Vector__3i32F4 velocity__3i32F4,
        Vector__3i16F8 acceleration__3i16F8);

static inline
bool dispatch_game_action__hitbox(
        Game *p_game,
        Identifier__u32 uuid_of__target__u32,
        Vector__3i32F4 position__3i32F4,
        Vector__3i32F4 velocity__3i32F4,
        Vector__3i16F8 acceleration__3i16F8) {
    Game_Action ga_resolve;
    initialize_game_action_for__hitbox(
            &ga_resolve,
            uuid_of__target__u32,
            position__3i32F4,
            velocity__3i32F4,
            acceleration__3i16F8);
    return dispatch_game_action_to__server(
            p_game, 
            &ga_resolve);
}

#endif
