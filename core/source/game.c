#include "client.h"
#include "defines.h"
#include "defines_weak.h"
#include "inventory/inventory_manager.h"
#include "inventory/item_manager.h"
#include "log/log.h"
#include "platform.h"
#include "platform_defaults.h"
#include "platform_defines.h"
#include "process/process_manager.h"
#include "rendering/aliased_texture_manager.h"
#include "rendering/sprite_gfx_allocator_manager.h"
#include "scene/implemented/scene__test.h"
#include "scene/scene.h"
#include "scene/scene_manager.h"
#include "serialization/hashing.h"
#include "sort/sort_list/sort_list_manager.h"
#include "vectors.h"
#include "world/tile_logic_manager.h"
#include <game.h>
#include <entity/entity.h>
#include <entity/entity_manager.h>
#include <debug/debug.h>
#include <input/input.h>
#include <world/world.h>
#include <timer.h>

#include <collisions/hitbox_aabb.h>

#include <world/chunk.h>
#include <world/tile.h>

#include <ui/ui_manager.h>

void initialize_game(
        Game *p_game,
        m_Game_Action_Handler m_game_action_handler) {
    initialize_scene_manager(&p_game->scene_manager);
    register_scene__test(&p_game->scene_manager);
    initialize_process_manager(
            get_p_process_manager_from__game(p_game));
    initialize_sort_list_manager(
            get_p_sort_list_manager_from__game(p_game));
    initialize_inventory_manager(
            get_p_inventory_manager_from__game(p_game));
    initialize_item_manager(
            get_p_item_manager_from__game(p_game));
    register_core_items_into__item_manager(
            get_p_item_manager_from__game(p_game));

    initialize_sprite_gfx_allocator_manager(
            get_p_sprite_gfx_allocation_manager_from__game(p_game));
    register_sprite_gfx_allocators_in__sprite_gfx_allocator_manager(
            get_p_sprite_gfx_allocation_manager_from__game(p_game));

    initialize_aliased_texture_manager(
            get_p_aliased_texture_manager_from__game(p_game));

    initialize_log(get_p_log__global_from__game(p_game));
    initialize_log(get_p_log__local_from__game(p_game));
    initialize_log(get_p_log__system_from__game(p_game));

    initialize_timer_u32(
            &p_game->time__seconds__u32, 
            (u32)-1);
    initialize_timer_u32(
            &p_game->time__nanoseconds__u32, 
            999999999);
    p_game->tick_accumilator__i32F20 = 0;

    p_game->is_world__initialized = false;
    p_game->m_game_action_handler = m_game_action_handler;
}

void allocate_client_pool_for__game(
        Game *p_game,
        Quantity__u32 quantity_of__clients) {
    if (quantity_of__clients > MAX_QUANTITY_OF__TCP_SOCKETS) {
        debug_error("allocate_client_pool_for__game, quantity_of__clients > MAX_QUANTITY_OF__TCP_SOCKETS");
        quantity_of__clients = MAX_QUANTITY_OF__TCP_SOCKETS;
    }
    p_game->pM_clients = malloc(sizeof(Client) * quantity_of__clients);
    p_game->pM_ptr_array_of__clients = malloc(sizeof(Client*) 
            * quantity_of__clients);
    p_game->max_quantity_of__clients = quantity_of__clients;
    p_game->quantity_of__clients = 0;
}

void release_clients_from__game(
        Game *p_game) {
    debug_error("release_clients_from__game, impl.");
}

void begin_multiplayer_for__game(
        Game *p_game) {
    if (sizeof(Game_Action) > sizeof(TCP_Packet)) {
        debug_abort("begin_multiplayer_for__game, sizeof(Game_Action) > sizeof(TCP_Packet)");
        return;
    }
    p_game->pM_tcp_socket_manager = malloc(sizeof(TCP_Socket_Manager));
}

void stop_multiplayer_for__game(
        Game *p_game) {
    if (p_game->pM_tcp_socket_manager) {
        free(p_game->pM_tcp_socket_manager);
    }
}

Client *allocate_client_from__game(
        Game *p_game,
        Identifier__u32 uuid__u32) {
    Client *p_client = 
        (Client*)dehash_identitier_u32_in__contigious_array(
                (Serialization_Header*)&p_game->pM_clients, 
                p_game->max_quantity_of__clients, 
                uuid__u32);
    if (!p_client) {
        debug_error("allocate_client_from__game, failed to allocate p_client.");
        return 0;
    }

    initialize_client(
            p_client, 
            uuid__u32, 
            VECTOR__3i32__0_0_0);

    p_game->quantity_of__clients++;

    p_game->pM_ptr_array_of__clients[
        p_game->quantity_of__clients] = p_client;

    return p_client;
}

Client *get_p_client_by__uuid_from__game(
        Game *p_game,
        Identifier__u32 uuid__u32) {
    if (!p_game->pM_clients) {
        debug_warning("Did you forget to allocate the client pool?");
        debug_error("get_p_client_by__uuid_from__game, pM_clients == 0.");
        return 0;
    }
    return (Client*)dehash_identitier_u32_in__contigious_array(
            (Serialization_Header *)p_game->pM_clients, 
            p_game->max_quantity_of__clients, 
            uuid__u32);
}

void release_client_from__game(
        Game *p_game,
        Client *p_client) {
    debug_abort("release_client_from__game, impl.");
}

///
/// Sends this game action to all clients that
/// have the given area loaded.
///
void broadcast_game_action(
        Game *p_game,
        Game_Action *p_game_action,
        Global_Space_Vector__3i32 global_space__vector__3i32) {
    debug_abort("broadcast_game_action, impl.");
}

void poll_multiplayer(Game *p_game) {
    if (!p_game->pM_tcp_socket_manager) {
        return;
    }

    p_game->pM_tcp_socket_manager->m_poll_tcp_socket_manager(
            p_game->pM_tcp_socket_manager,
            p_game);
}

i32F20 get_elapsed_time__i32F20_of__game(
        Game *p_game) {
    p_game->time_elapsed__i32F20 =
        PLATFORM_get_time_elapsed(
                &p_game->time__seconds__u32, 
                &p_game->time__nanoseconds__u32);
    p_game->tick_accumilator__i32F20 +=
        p_game->time_elapsed__i32F20;
    return p_game->time_elapsed__i32F20;
}

Quantity__u32 poll__game_tick_timer(Game *p_game) {
    (void)get_elapsed_time__i32F20_of__game(p_game);
    if (p_game->tick_accumilator__i32F20
            >= BIT(14)) {
        return p_game->tick_accumilator__i32F20 >> 14;
    }
    return 0;
}

void reset__game_tick_timer(Game *p_game) {
    p_game->tick_accumilator__i32F20 -=
        p_game->tick_accumilator__i32F20 >> 14;
}

bool print_log__global(Game *p_game, char *cstr) {
    bool result = put_cstr_into__message(
            get_next_p_message_in__log(
                get_p_log__global_from__game(p_game)), 
            cstr);
    PLATFORM_update_log__global(p_game);
    flush_message_into__log(get_p_log__global_from__game(p_game));
    return result;
}

bool print_log__local(Game *p_game, char *cstr) {
    bool result = put_cstr_into__message(
            get_next_p_message_in__log(
                get_p_log__local_from__game(p_game)), 
            cstr);
    PLATFORM_update_log__local(p_game);
    flush_message_into__log(get_p_log__local_from__game(p_game));
    return result;
}

bool print_log__system(Game *p_game, char *cstr) {
    bool result = put_cstr_into__message(
            get_next_p_message_in__log(
                get_p_log__system_from__game(p_game)), 
            cstr);
    PLATFORM_update_log__system(p_game);
    flush_message_into__log(get_p_log__system_from__game(p_game));
    return result;
}

int run_game(Game *p_game) {
    if (!p_game->scene_manager.p_active_scene) {
        Scene *p_scene =
            get_p_scene_from__scene_manager(
                    &p_game->scene_manager, Scene_Kind__None);
        if (!is_scene__valid(p_scene)) {
            debug_warning("Did you forget to assign a Scene_Kind to Scene_Kind__None?");
            debug_abort("Active scene not established.");
            return -1;
        }

        set_p_active_scene_for__scene_manager(
                &p_game->scene_manager, 
                Scene_Kind__None);
    }
    Scene_Manager *p_scene_manager =
        &p_game->scene_manager;
    Scene *p_active_scene;
    while ((p_active_scene =
            get_p_active_scene_from__scene_manager(
                p_scene_manager))) {
        debug_info("TRANSITION p_active_scene -> %p",
                p_active_scene);
        p_active_scene =
            p_game->scene_manager.p_active_scene;
        debug_info("loading scene.");
        if (p_active_scene->m_load_scene_handler)
            p_active_scene->m_load_scene_handler(
                    p_active_scene,
                    p_game);
        debug_info("entering scene.");
        if (!p_active_scene->m_enter_scene_handler) {
            debug_error("p_active_scene->m_enter_scene_handler is null.");
            set_p_active_scene_for__scene_manager(
                    p_scene_manager, 
                    SCENE_IDENTIFIER__MAIN_MENU);
            continue;
        }
        p_active_scene->m_enter_scene_handler(
                p_active_scene,
                p_game);
        debug_info("unloading scene.");
        if (p_active_scene->m_unload_scene_handler)
            p_active_scene->m_unload_scene_handler(
                    p_active_scene,
                    p_game);
    }
    debug_info("p_active_scene == 0");
    debug_info("Game stopping...");
    while (PLATFORM_get_quantity_of__active_serialization_requests(
                get_p_PLATFORM_file_system_context_from__game(p_game))) {
        loop_timer_u32(&p_game->tick__timer_u32);
        poll_process_manager(
                get_p_process_manager_from__game(p_game), 
                p_game);
    }
    debug_info("Game stopped.");
    return 0;
}

void manage_game__pre_render(Game *p_game) {
    PLATFORM_pre_render(p_game);
}

void manage_game__post_render(Game *p_game) {
    reset__game_tick_timer(p_game);
    PLATFORM_poll_input(
            p_game,
            get_p_input_from__game(p_game));
    poll_process_manager(
            get_p_process_manager_from__game(p_game), p_game);
    PLATFORM_poll_audio_effects(
            get_p_PLATFORM_audio_context_from__game(p_game));

#warning TODO: resolve update_ui
    // PLATFORM_update_ui(p_game);
    PLATFORM_post_render(p_game);
    loop_timer_u32(&p_game->tick__timer_u32);
}
