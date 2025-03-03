#include "client.h"
#include "defines.h"
#include "defines_weak.h"
#include "game_action/game_action.h"
#include "game_action/game_action_logic_table.h"
#include "game_action/implemented/game_action__registrar.h"
#include "inventory/inventory_manager.h"
#include "inventory/item_manager.h"
#include "log/log.h"
#include "multiplayer/tcp_socket_manager.h"
#include "platform.h"
#include "platform_defaults.h"
#include "platform_defines.h"
#include "process/process_manager.h"
#include "rendering/aliased_texture_manager.h"
#include "rendering/sprite_gfx_allocator_manager.h"
#include "scene/implemented/scene__test.h"
#include "scene/implemented/scene_registrar.h"
#include "scene/scene.h"
#include "scene/scene_manager.h"
#include "serialization/hashing.h"
#include "serialization/serialization_header.h"
#include "sort/sort_list/sort_list_manager.h"
#include "vectors.h"
#include "world/local_space_manager.h"
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

void m_game_action_handler__dispatch__singleplayer(
        Game *p_game,
        Game_Action *p_game_action);
void m_game_action_handler__dispatch__multiplayer(
        Game *p_game,
        Game_Action *p_game_action);

void m_game_action_handler__receive__singleplayer(
        Game *p_game,
        Game_Action *p_game_action);
void m_game_action_handler__receive__multiplayer(
        Game *p_game,
        Game_Action *p_game_action);

void m_game_action_handler__resolve__singleplayer(
        Game *p_game,
        Game_Action *p_game_action);
void m_game_action_handler__resolve__multiplayer(
        Game *p_game,
        Game_Action *p_game_action);

void initialize_game(
        Game *p_game) {
    initialize_scene_manager(get_p_scene_manager_from__game(p_game));
    register_scenes(get_p_scene_manager_from__game(p_game));
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

    p_game->pM_clients = 0;
    p_game->pM_ptr_array_of__clients = 0;
    p_game->pM_tcp_socket_manager = 0;

    initialize_timer_u32(
            &p_game->time__seconds__u32, 
            (u32)-1);
    initialize_timer_u32(
            &p_game->time__nanoseconds__u32, 
            999999999);
    p_game->tick_accumilator__i32F20 = 0;

    p_game->is_world__initialized = false;

    p_game->m_game_action_handler__dispatch =
        m_game_action_handler__dispatch__singleplayer;
    p_game->m_game_action_handler__receive =
        m_game_action_handler__receive__singleplayer;
    p_game->m_game_action_handler__resolve =
        m_game_action_handler__resolve__singleplayer;

    initialize_game_action_logic_table(
            get_p_game_action_logic_table_from__game(p_game));
    register_game_actions__offline(
            get_p_game_action_logic_table_from__game(p_game));
}

void allocate_client_pool_for__game(
        Game *p_game,
        Quantity__u32 quantity_of__clients) {
    if (quantity_of__clients > MAX_QUANTITY_OF__TCP_SOCKETS) {
        debug_error("allocate_client_pool_for__game, quantity_of__clients > MAX_QUANTITY_OF__TCP_SOCKETS");
        quantity_of__clients = MAX_QUANTITY_OF__TCP_SOCKETS;
    }
    p_game->pM_clients = malloc(sizeof(Client) * quantity_of__clients);

    p_game->max_quantity_of__clients = quantity_of__clients;
    initialize_serialization_header__contiguous_array(
            (Serialization_Header*)p_game->pM_clients, 
            p_game->max_quantity_of__clients, 
            sizeof(Client));

    p_game->pM_ptr_array_of__clients = malloc(sizeof(Client*) 
            * quantity_of__clients);
    memset(
            p_game->pM_ptr_array_of__clients,
            0,
            p_game->max_quantity_of__clients);
    p_game->quantity_of__clients = 0;
}

void release_clients_from__game(
        Game *p_game) {
    debug_error("release_clients_from__game, impl.");
}

void begin_multiplayer_for__game(
        Game *p_game,
        m_Poll_TCP_Socket_Manager m_poll_tcp_socket_manager) {
    if (sizeof(Game_Action) > sizeof(TCP_Packet)) {
        debug_abort("begin_multiplayer_for__game, sizeof(Game_Action) > sizeof(TCP_Packet)");
        return;
    }
    p_game->pM_tcp_socket_manager = malloc(sizeof(TCP_Socket_Manager));
    if (!p_game->pM_tcp_socket_manager) {
        debug_abort("begin_multiplayer_for__game, failed to alloc pM_tcp_socket_manager.");
        return;
    }
    initialize_tcp_socket_manager(
            p_game->pM_tcp_socket_manager, 
            m_poll_tcp_socket_manager);
    get_p_tcp_socket_manager_from__game(p_game)
        ->p_PLATFORM_tcp_context = PLATFORM_tcp_begin(p_game);
    if (!get_p_PLATFORM_tcp_context_from__game(p_game)) {
        debug_abort("begin_multiplayer_for__game, failed to get PLATFORM_TCP_Context.");
        stop_multiplayer_for__game(p_game);
        return;
    }

    p_game->m_game_action_handler__dispatch =
        m_game_action_handler__dispatch__multiplayer;
    p_game->m_game_action_handler__receive =
        m_game_action_handler__receive__multiplayer;
    p_game->m_game_action_handler__resolve =
        m_game_action_handler__resolve__multiplayer;

    if (p_game->max_quantity_of__clients == 1) {
        register_game_actions__client(
                get_p_game_action_logic_table_from__game(p_game));
    } else {
        register_game_actions__server(
                get_p_game_action_logic_table_from__game(p_game));
    }
}

void stop_multiplayer_for__game(
        Game *p_game) {
    if (p_game->pM_tcp_socket_manager) {
        PLATFORM_tcp_end(p_game);
        free(p_game->pM_tcp_socket_manager);
    }
}

Client *allocate_client_from__game(
        Game *p_game,
        Identifier__u32 uuid__u32) {
    Client *p_client = 
        (Client*)dehash_identitier_u32_in__contigious_array(
                (Serialization_Header*)p_game->pM_clients, 
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

    p_game->pM_ptr_array_of__clients[
        p_game->quantity_of__clients] = p_client;

    p_game->quantity_of__clients++;

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
    Client *p_client = 
        (Client*)dehash_identitier_u32_in__contigious_array(
            (Serialization_Header *)p_game->pM_clients, 
            p_game->max_quantity_of__clients, 
            uuid__u32);
    if (IS_DEALLOCATED_P(p_client))
        return 0;
    return p_client;
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
        p_game->tick_accumilator__i32F20
        & ~MASK(14);
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

void m_game_action_handler__dispatch__singleplayer(
        Game *p_game,
        Game_Action *p_game_action) {
    Client *p_client =
        get_p_client_by__index_from__game(
                p_game, 
                0);
    dispatch_game_action_for__client(
            p_client, 
            p_game, 
            0,
            p_game_action);
}

void m_game_action_handler__dispatch__multiplayer(
        Game *p_game,
        Game_Action *p_game_action) {
    if (is_game_action__local(p_game_action)) {
        m_game_action_handler__dispatch__singleplayer(
                p_game, 
                p_game_action);
        return;
    }

    if (is_game_action__broadcasted(p_game_action)) {
        bool is_local =
            !is_vectors_3i32F4__out_of_bounds(
                    p_game_action
                    ->vector_3i32F4__broadcast_point);
        for (Index__u32 index_of__client = 0;
                index_of__client
                < get_quantity_of__clients_connect_to__game(p_game);
                index_of__client++) {
            Client *p_client = get_p_client_by__index_from__game(
                    p_game, 
                    index_of__client);

            if (is_local
                     && !is_vector_3i32F4_within__local_space_manager(
                        get_p_local_space_manager_from__client(p_client), 
                        p_game_action->vector_3i32F4__broadcast_point)) {
                continue;
            }

            dispatch_game_action_for__client(
                    p_client, 
                    p_game, 
                    get_p_tcp_socket_manager_from__game(p_game), 
                    p_game_action);
        }
        return;
    }

    Client *p_client =
        get_p_client_by__uuid_from__game(
                p_game, 
                get_client_uuid_from__game_action(p_game_action));
    if (!p_client) {
        resolve_game_action(
                p_game, 
                p_game_action);
        return;
    }

    dispatch_game_action_for__client(
            p_client, 
            p_game, 
            get_p_tcp_socket_manager_from__game(p_game), 
            p_game_action);
}

void m_game_action_handler__receive__singleplayer(
        Game *p_game,
        Game_Action *p_game_action) {
    Client *p_client =
        get_p_client_by__index_from__game(
                p_game, 
                0);
    receive_game_action_for__client(
            p_client, 
            p_game, 
            p_game_action);
}

void m_game_action_handler__receive__multiplayer(
        Game *p_game,
        Game_Action *p_game_action) {
    if (is_game_action__local(p_game_action)) {
        m_game_action_handler__receive__singleplayer(
                p_game, 
                p_game_action);
        return;
    }

    if (is_game_action__broadcasted(p_game_action)) {
        bool is_local =
            !is_vectors_3i32F4__out_of_bounds(
                    p_game_action
                    ->vector_3i32F4__broadcast_point);
        for (Index__u32 index_of__client = 0;
                index_of__client
                < get_quantity_of__clients_connect_to__game(p_game);
                index_of__client++) {
            Client *p_client = get_p_client_by__index_from__game(
                    p_game, 
                    index_of__client);

            if (is_local
                     && !is_vector_3i32F4_within__local_space_manager(
                        get_p_local_space_manager_from__client(p_client), 
                        p_game_action->vector_3i32F4__broadcast_point)) {
                continue;
            }

            receive_game_action_for__client(
                    p_client, 
                    p_game, 
                    p_game_action);
        }
        return;
    }

    Client *p_client =
        get_p_client_by__uuid_from__game(
                p_game, 
                get_client_uuid_from__game_action(p_game_action));
    if (!p_client) {
        resolve_game_action(
                p_game, 
                p_game_action);
        return;
    }

    receive_game_action_for__client(
            p_client, 
            p_game, 
            p_game_action);
}

void m_game_action_handler__resolve__singleplayer(
        Game *p_game,
        Game_Action *p_game_action) {
    if (!is_game_action__allocated(p_game_action))
        return;

    Client *p_client =
        get_p_client_by__index_from__game(
                p_game, 
                0);

    release_game_action_from__client(
            p_client, 
            p_game_action);
}

void m_game_action_handler__resolve__multiplayer(
        Game *p_game,
        Game_Action *p_game_action) {
    if (!is_game_action__allocated(p_game_action))
        return;
    if (is_game_action__local(p_game_action)) {
        m_game_action_handler__resolve__singleplayer(
                p_game, 
                p_game_action);
        return;
    }

    Client *p_client =
        get_p_client_by__uuid_from__game(
                p_game, 
                get_client_uuid_from__game_action(p_game_action));
    if (!p_client) {
        resolve_game_action(
                p_game, 
                p_game_action);
        return;
    }
}
