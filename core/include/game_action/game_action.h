#ifndef GAME_ACTION_H
#define GAME_ACTION_H

#include "defines_weak.h"
#include "game.h"
#include <defines.h>

void initialize_game_action(
        Game_Action *p_game_action);

static inline
Game_Action_Kind get_kind_of__game_action(
        Game_Action *p_game_action) {
    return p_game_action->the_kind_of_game_action__this_action_is;
}

static inline
bool is_game_action__allocated(Game_Action *p_game_action) {
    return p_game_action->game_action_flags
        & GAME_ACTION_FLAGS__BIT_IS_ALLOCATED
        ;
}

static inline
void set_game_action_as__allocated(Game_Action *p_game_action) {
    p_game_action->game_action_flags |=
        GAME_ACTION_FLAGS__BIT_IS_ALLOCATED
        ;
}

static inline
void set_game_action_as__deallocated(Game_Action *p_game_action) {
    p_game_action->game_action_flags &=
        ~GAME_ACTION_FLAGS__BIT_IS_ALLOCATED
        ;
}

static inline
bool is_game_action__inbound(Game_Action *p_game_action) {
    return p_game_action->game_action_flags
        & GAME_ACTION_FLAGS__BIT_IS_OUT_OR__IN_BOUND
        ;
}

static inline
void set_game_action_as__inbound(Game_Action *p_game_action) {
    p_game_action->game_action_flags |=
        GAME_ACTION_FLAGS__BIT_IS_OUT_OR__IN_BOUND
        ;
}

static inline
void set_game_action_as__outbound(Game_Action *p_game_action) {
    p_game_action->game_action_flags &=
        ~GAME_ACTION_FLAGS__BIT_IS_OUT_OR__IN_BOUND
        ;
}

static inline
bool is_game_action__fire_and__forget(
        Game_Action *p_game_action) {
    return p_game_action->game_action_flags
        & GAME_ACTION_FLAGS__BIT_IS_FIRE_AND_FORGET
        ;
}

static inline
bool is_game_action__with_process(
        Game_Action *p_game_action) {
    return p_game_action->game_action_flags
        & GAME_ACTION_FLAGS__BIT_IS_WITH_PROCESS
        ;
}

static inline
bool is_game_action__processed_on__invocation_or__respose(
        Game_Action *p_game_action) {
    return p_game_action->game_action_flags
        & GAME_ACTION_FLAGS__BIT_IS_PROCESSED_ON_INVOCATION_OR_RESPONSE
        ;
}

static inline
bool is_game_action__responding_to_another__game_action(
        Game_Action *p_game_action) {
    return p_game_action->game_action_flags
        & GAME_ACTION_FLAGS__BIT_IS_RESPONSE
        ;
}

static inline
Game_Action_State get_state_of__game_action(Game_Action *p_game_action) {
    return p_game_action->state_of__game_action;
}

static inline
void set_state_of__game_action(
        Game_Action *p_game_action,
        Game_Action_State state_of__game_action) {
    p_game_action->state_of__game_action =
        state_of__game_action;
}

#endif
