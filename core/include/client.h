#ifndef CLIENT_H
#define CLIENT_H

#include "defines.h"
#include "defines_weak.h"
#include "game_action/game_action_manager.h"
#include "serialization/serialized_field.h"

void initialize_client(
        Client *p_client,
        Identifier__u32 uuid__u32,
        Global_Space_Vector__3i32 global_space_vector__3i32);

///
/// Logically handle an outbound allocated game_action.
///
void dispatch_game_action_for__client(
        Client *p_client,
        Game *p_game,
        Game_Action *p_game_action);

///
/// Logcially handle an inbound allocated game_action.
///
void receive_game_action_for__client(
        Client *p_client,
        Game *p_game,
        Game_Action *p_game_action);

void release_game_action_from__client(
        Client *p_client,
        Game_Action *p_game_action);

Game_Action *allocate_game_action_from__client(
        Client *p_client,
        Game_Action_Flags game_action_flags);

void set_entity_of__client(
        Client *p_client,
        Entity *p_entity);

static inline
Game_Action_Manager *get_p_game_action_manager__inbound_from__client(
        Client *p_client) {
    return &p_client->game_action_manager__inbound;
}

static inline
Game_Action_Manager *get_p_game_action_manager__outbound_from__client(
        Client *p_client) {
    return &p_client->game_action_manager__outbound;
}

static inline
Local_Space_Manager *get_p_local_space_manager_from__client(
        Client *p_client) {
    return &p_client->local_space_manager;
}

#endif
