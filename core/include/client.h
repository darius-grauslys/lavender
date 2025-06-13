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
bool dispatch_game_action_for__client(
        Client *p_client,
        Game *p_game,
        TCP_Socket_Manager *p_tcp_socket_manager,
        Game_Action *p_game_action);

void teleport_client(
        Game *p_game,
        Client *p_client,
        Vector__3i32F4 position__3i32F4);

///
/// Logcially handle an inbound allocated game_action.
///
bool receive_game_action_for__client(
        Client *p_client,
        Game *p_game,
        Game_Action *p_game_action);

bool release_game_action_from__client(
        Client *p_client,
        Game_Action *p_game_action);

Game_Action *allocate_game_action_from__client(
        Client *p_client,
        Game_Action_Flags game_action_flags);

void set_entity_of__client(
        Client *p_client,
        Entity *p_entity);

void m_process__deserialize_client__default(
        Process *p_this_process,
        Game *p_game);

void m_process__serialize_client__default(
        Process *p_this_process,
        Game *p_game);

static inline
Game_Action_Manager *get_p_game_action_manager__inbound_from__client(
        Client *p_client) {
    if (!p_client) return 0;
    return &p_client->game_action_manager__inbound;
}

static inline
Game_Action_Manager *get_p_game_action_manager__outbound_from__client(
        Client *p_client) {
    if (!p_client) return 0;
    return &p_client->game_action_manager__outbound;
}

static inline
Local_Space_Manager *get_p_local_space_manager_from__client(
        Client *p_client) {
    if (!p_client) return 0;
    return &p_client->local_space_manager;
}

static inline
bool is_client__loading(
        Client *p_client) {
    return p_client && p_client->client_flags__u16
        & CLIENT_FLAG__IS_LOADING;
}

static inline
void set_client_as__loading(
        Client *p_client) {
    p_client->client_flags__u16 |=
        CLIENT_FLAG__IS_LOADING;
}

static inline
void set_client_as__NOT_loading(
        Client *p_client) {
    p_client->client_flags__u16 &=
        ~CLIENT_FLAG__IS_LOADING;
}

static inline
bool is_client__saving(
        Client *p_client) {
    return p_client && p_client->client_flags__u16
        & CLIENT_FLAG__IS_SAVING;
}

static inline
void set_client_as__saving(
        Client *p_client) {
    p_client->client_flags__u16 |=
        CLIENT_FLAG__IS_SAVING;
}

static inline
void set_client_as__NOT_saving(
        Client *p_client) {
    p_client->client_flags__u16 &=
        ~CLIENT_FLAG__IS_SAVING;
}

static inline
bool is_client__active(
        Client *p_client) {
    return p_client && p_client->client_flags__u16
        & CLIENT_FLAG__IS_ACTIVE;
}

static inline
void set_client_as__active(
        Client *p_client) {
    set_client_as__NOT_loading(p_client);
    set_client_as__NOT_saving(p_client);
    p_client->client_flags__u16 |=
        CLIENT_FLAG__IS_ACTIVE;
}

static inline
void set_client_as__inactive(
        Client *p_client) {
    p_client->client_flags__u16 &=
        ~CLIENT_FLAG__IS_ACTIVE;
}

#endif
