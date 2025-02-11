#ifndef CLIENT_H
#define CLIENT_H

#include "defines.h"
#include "defines_weak.h"

void initialize_client(Client *p_client);

Game_Action *allocate_game_action__inbound(
        Client *p_client);

Game_Action *allocate_game_action__outbound(
        Client *p_client);

void dispatch_game_action(
        Client *p_client,
        Process_Manager *p_process_manager,
        Game_Action *p_game_action);

void release_game_action(
        Client *p_client,
        Game_Action *p_game_action);

#endif
