#ifndef GAME_H
#define GAME_H

///
/// This entire file is not implemented in core.
/// You will need to compile with a backend.
///

#include "defines_weak.h"
#include "log/log.h"
#include "log/message.h"
#include "multiplayer/tcp_socket_manager.h"
#include "platform.h"
#include "random.h"
#include "timer.h"
#include <defines.h>
#include <world/world.h>

void initialize_game(Game *p_game);
int run_game(Game *p_game);

u32F20 poll_elapsed_time__u32F20_of__game(
        Game *p_game);

///
/// Returns the number of elapsed game ticks
/// since manage_game__post_render.
///
Quantity__u32 poll__game_tick_timer(Game *p_game);

///
/// This is called after each instance of
/// manage_game__post_render.
///
void reset__game_tick_timer(Game *p_game);

void manage_game(Game *p_game);

void manage_game__pre_render(Game *p_game);
void manage_game__post_render(Game *p_game);

void begin_multiplayer_for__game(
        Game *p_game,
        m_Poll_TCP_Socket_Manager m_poll_tcp_socket_manager);
void stop_multiplayer_for__game(
        Game *p_game);
void poll_multiplayer(Game *p_game);

void allocate_client_pool_for__game(
        Game *p_game,
        Identifier__u32 uuid_of__local_client_or__server__u32,
        Quantity__u32 quantity_of__clients);

Client *allocate_client_from__game(
        Game *p_game,
        Identifier__u32 uuid__u32);

Client *get_p_client_by__uuid_from__game(
        Game *p_game,
        Identifier__u32 uuid__u32);

static inline
Client *get_p_local_client_by__from__game(
        Game *p_game) {
    if (!p_game->pM_ptr_array_of__clients)
        return 0;
    return p_game->pM_ptr_array_of__clients[0];
}

/// TODO: obsolete, and inaccurate
static inline
Quantity__u32 get_ticks_elapsed__game(Game *p_game) {
    return get_time_elapsed_from__timer_u32(&p_game->tick__timer_u32);
}

static inline
Log *get_p_log__global_from__game(Game *p_game) {
    return &p_game->log__global;
}

static inline
void clear_log__global(Game *p_game) {
    clear_log(get_p_log__global_from__game(p_game));
    PLATFORM_clear_log__global(p_game);
}

static inline
Log *get_p_log__local_from__game(Game *p_game) {
    return &p_game->log__local;
}

static inline
void clear_log__local(Game *p_game) {
    clear_log(get_p_log__local_from__game(p_game));
    PLATFORM_clear_log__local(p_game);
}

static inline
Log *get_p_log__system_from__game(Game *p_game) {
    return &p_game->log__system;
}

bool print_log__global(Game *p_game, char *cstr);
bool print_log__local(Game *p_game, char *cstr);
bool print_log__system(Game *p_game, char *cstr);

static inline
void clear_log__system(Game *p_game) {
    clear_log(get_p_log__system_from__game(p_game));
    PLATFORM_clear_log__system(p_game);
}

static inline 
World *get_p_world_from__game(Game *p_game) {
    return &p_game->world;
}

static inline
Hitbox_AABB_Manager *get_p_hitbox_aabb_manager_from__game(Game *p_game) {
    return get_p_hitbox_aabb_manager_from__world(
            get_p_world_from__game(p_game));
}

static inline 
Global_Space_Manager *get_p_global_space_manager_from__game(Game *p_game) {
    return get_p_global_space_manager_from__world(
            get_p_world_from__game(p_game));
}

static inline 
Sprite_Manager *get_p_sprite_manager_from__game(
        Game *p_game) {
    return &p_game->gfx_context.sprite_manager;
}

static inline 
Aliased_Texture_Manager *get_p_aliased_texture_manager_from__game(Game *p_game) {
    return &p_game->gfx_context.aliased_texture_manager;
}

static inline
Process_Manager *get_p_process_manager_from__game(Game *p_game) {
    return &p_game->process_manager;
}

static inline
Sort_List_Manager *get_p_sort_list_manager_from__game(Game *p_game) {
    return &p_game->sort_list_manager;
}

static inline
Path_List_Manager *get_p_path_list_manager_from__game(Game *p_game) {
    return &p_game->path_list_manager;
}

static inline
Inventory_Manager *get_p_inventory_manager_from__game(Game *p_game) {
    return get_p_inventory_manager_from__world(
            get_p_world_from__game(p_game));
}

static inline
Item_Manager *get_p_item_manager_from__game(Game *p_game) {
    return get_p_item_manager_from__world(
            get_p_world_from__game(p_game));
}

static inline 
Scene_Manager *get_p_scene_manager_from__game(Game *p_game) {
    return &p_game->scene_manager;
}

static inline 
Entity_Manager *get_p_entity_manager_from__game(Game *p_game) {
    return get_p_entity_manager_from__world(&p_game->world);
}

static inline
World_Parameters *get_p_world_parameters_from__game(Game *p_game) {
    return get_p_world_parameters_from__world(
            get_p_world_from__game(p_game));
}

static inline
PLATFORM_File_System_Context *get_p_PLATFORM_file_system_context_from__game(
        Game *p_game) {
    return p_game->p_PLATFORM_file_system_context;
}

static inline
PLATFORM_Audio_Context *get_p_PLATFORM_audio_context_from__game(
        Game *p_game) {
    return p_game->p_PLATFORM_audio_context;
}

static inline
Gfx_Context *get_p_gfx_context_from__game(Game *p_game) {
    return &p_game->gfx_context;
}

static inline
PLATFORM_Gfx_Context *get_p_PLATFORM_gfx_context_from__game(Game *p_game) {
    return p_game->gfx_context.p_PLATFORM_gfx_context;
}

static inline
TCP_Socket_Manager *get_p_tcp_socket_manager_from__game(Game *p_game) {
    return p_game->pM_tcp_socket_manager;
}

static inline
PLATFORM_TCP_Context *get_p_PLATFORM_tcp_context_from__game(Game *p_game) {
    return 
        (p_game->pM_tcp_socket_manager)
        ? get_p_PLATFORM_tcp_context_from__tcp_socket_manager(
                get_p_tcp_socket_manager_from__game(p_game))
        : 0
        ;
}

static inline
Game_Action_Logic_Table *get_p_game_action_logic_table_from__game(Game *p_game) {
    return &p_game->game_action_logic_table;
}

static inline
Input *get_p_input_from__game(Game *p_game) {
    return &p_game->input;
}

static inline
Quantity__u32 get_quantity_of__clients_connect_to__game(
        Game *p_game) {
    return p_game->quantity_of__clients;
}

static inline
Client *get_p_client_by__index_from__game(
        Game *p_game,
        Index__u32 index_of__client) {
#ifndef NDEBUG
    if (!p_game->pM_ptr_array_of__clients) {
        debug_warning("Did you for get to allocate the client pool?");
        debug_abort("get_p_client_by__index_from__game, pM_ptr_array_of__clients == 0.");
        return 0;
    }
    if (index_of__client
            >= get_quantity_of__clients_connect_to__game(p_game)) {
        debug_error("get_p_client_by__index_from__game, index out of bounds: %d/%d",
                index_of__client,
                get_quantity_of__clients_connect_to__game(p_game));
        return 0; 
    }
#endif
    return p_game->pM_ptr_array_of__clients[index_of__client];
}

static inline
bool is_game__multiplayer(Game *p_game) {
    return p_game->pM_tcp_socket_manager;
}

static inline
bool dispatch_game_action(
        Game *p_game,
        Identifier__u32 uuid_of__client__u32,
        Game_Action *p_game_action) {
    return p_game->m_game_action_handler__dispatch(
            p_game,
            get_p_client_by__uuid_from__game(
                p_game, 
                uuid_of__client__u32),
            p_game_action);
}

static inline
bool dispatch_game_action_to__server(
        Game *p_game,
        Game_Action *p_game_action) {
    return p_game->m_game_action_handler__dispatch(
            p_game,
            get_p_local_client_by__from__game(p_game),
            p_game_action);
}

static inline
bool receive_game_action(
        Game *p_game,
        Identifier__u32 uuid_of__client__u32,
        Game_Action *p_game_action) {
    return p_game->m_game_action_handler__receive(
            p_game,
            get_p_client_by__uuid_from__game(
                p_game, 
                uuid_of__client__u32),
            p_game_action);
}

static inline
bool resolve_game_action(
        Game *p_game,
        Identifier__u32 uuid_of__client__u32,
        Game_Action *p_game_action) {
    return p_game->m_game_action_handler__resolve(
            p_game,
            get_p_client_by__uuid_from__game(
                p_game, 
                uuid_of__client__u32),
            p_game_action);
}

static inline
u32F20 get_elapsed_time__u32F20_of__game(
        Game *p_game) {
    return p_game->time_elapsed__u32F20;
}

static inline
u32F20 get_elapsed_ticks__u32F20_of__game(
        Game *p_game) {
    return p_game->tick_accumilator__u32F20 >> 15;
}

#endif
