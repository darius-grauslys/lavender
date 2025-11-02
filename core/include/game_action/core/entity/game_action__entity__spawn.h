#ifndef GAME_ACTION__ENTITY__SPAWN_H
#define GAME_ACTION__ENTITY__SPAWN_H

#include "defines.h"
#include "game.h"
#include "game_action/game_action.h"
#include "types/implemented/entity_kind.h"
#include "vectors.h"

void register_game_action__entity__spawn_for__server(
        Game_Action_Logic_Table *p_game_action_logic_table);

void register_game_action__entity__spawn_for__client(
        Game_Action_Logic_Table *p_game_action_logic_table);

void initialize_game_action_for__entity__spawn(
        Game_Action *p_game_action,
        Identifier__u32 uuid_of__target__u32,
        Entity_Kind the_kind_of__entity);

static inline
bool dispatch_game_action__entity__spawn(
        Game *p_game,
        Identifier__u32 uuid_of__target__u32,
        Entity_Kind the_kind_of__entity) {
    Game_Action ga_resolve;
    initialize_game_action_for__entity__spawn(
            &ga_resolve,
            uuid_of__target__u32,
            the_kind_of__entity);
    return dispatch_game_action_to__server(
            p_game, 
            &ga_resolve);
}

///
/// Set broadcast_point to VECTOR__3i32F4__OUT_OF_BOUNDS
/// to send globally.
///
static inline
bool broadcast_game_action__entity__spawn(
        Game *p_game,
        Identifier__u32 uuid_of__target__u32,
        Entity_Kind the_kind_of__entity,
        Vector__3i32F4 broadcast_point) {
    Game_Action ga_resolve;
    initialize_game_action_for__entity__spawn(
            &ga_resolve,
            uuid_of__target__u32,
            the_kind_of__entity);
    ga_resolve.vector_3i32F4__broadcast_point = broadcast_point;
    set_game_action_as__broadcasted(&ga_resolve);
    return dispatch_game_action_to__server(
            p_game, 
            &ga_resolve);
}

#endif
