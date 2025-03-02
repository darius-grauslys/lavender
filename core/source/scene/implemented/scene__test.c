#include "scene/implemented/scene__test.h"
#include "client.h"
#include "collisions/collision_node_pool.h"
#include "defines.h"
#include "defines_weak.h"
#include "game.h"
#include "input/input.h"
#include "multiplayer/server__default.h"
#include "multiplayer/client__default.h"
#include "multiplayer/tcp_socket_manager.h"
#include "platform.h"
#include "platform_defaults.h"
#include "platform_defines.h"
#include "process/process.h"
#include "rendering/aliased_texture_manager.h"
#include "rendering/graphics_window.h"
#include "rendering/graphics_window_manager.h"
#include "scene/scene_manager.h"
#include "rendering/gfx_context.h"
#include "serialization/serialization_header.h"
#include "vectors.h"
#include "world/camera.h"
#include "world/chunk.h"
#include "world/chunk_pool.h"
#include "world/chunk_vectors.h"
#include "world/global_space.h"
#include "world/global_space_manager.h"
#include "world/local_space.h"
#include "world/local_space_manager.h"
#include "world/world.h"

void m_load_scene__test(
        Scene *p_this_scene,
        Game *p_game);
void m_enter_scene__test(
        Scene *p_this_scene,
        Game *p_game);

void register_scene__test(Scene_Manager *p_scene_manager) {
    register_scene_into__scene_manager(
            p_scene_manager, 
            Scene_Kind__Test, 
            m_load_scene__test, 
            m_enter_scene__test, 
            0);
}

void m_load_scene__test(
        Scene *p_this_scene,
        Game *p_game) {
#ifdef IS_SERVER
    allocate_client_pool_for__game(p_game, MAX_QUANTITY_OF__TCP_SOCKETS-2);
    begin_multiplayer_for__game(
            p_game,
            m_poll_tcp_socket_manager_as__server__default);
    open_server_socket_on__tcp_socket_manager__ipv4(
            get_p_tcp_socket_manager_from__game(p_game), 
            0, 
            55566);
#else
    allocate_client_pool_for__game(p_game, 1);
    begin_multiplayer_for__game(
            p_game,
            m_poll_tcp_socket_manager_as__client__default);
    Client *p_client = allocate_client_from__game(
            p_game, 
            0);
    IPv4_Address addr;
    addr.ip_bytes[0] = 127;
    addr.ip_bytes[1] = 0;
    addr.ip_bytes[2] = 0;
    addr.ip_bytes[3] = 1;
    addr.port = 55566;
    open_socket_on__tcp_socket_manager__ipv4(
            get_p_tcp_socket_manager_from__game(p_game), 
            addr, 
            p_client->_serialization_header.uuid);
    load_p_PLATFORM_texture_from__path_with__alias(
            get_p_PLATFORM_gfx_context_from__game(p_game), 
            0, 
            get_p_aliased_texture_manager_from__game(p_game), 
            "ground", 
            TEXTURE_FLAGS(
                TEXTURE_FLAG__SIZE_256x256,
                TEXTURE_FLAG__RENDER_METHOD__0,
                TEXTURE_FLAG__FORMAT__2),
            "../../../AncientsGame/core/assets/world/tilesheet_ground.png");
    load_p_PLATFORM_texture_from__path_with__alias(
            get_p_PLATFORM_gfx_context_from__game(p_game), 
            0, 
            get_p_aliased_texture_manager_from__game(p_game), 
            "cover", 
            TEXTURE_FLAGS(
                TEXTURE_FLAG__SIZE_256x256,
                TEXTURE_FLAG__RENDER_METHOD__0,
                TEXTURE_FLAG__FORMAT__2),
            "../../../AncientsGame/core/assets/world/tilesheet_cover.png");
#endif
}

void f_chunk_generator(
        Game *p_game,
        Global_Space *p_global_space) {
    i32 random = 
        get_pseudo_random_i32__intrusively(
                get_p_repeatable_psuedo_random_from__world(
                    get_p_world_from__game(p_game)));

    Tile_Kind the_kind_of__tile =
        (random % 2)
        ? Tile_Kind__One
        : Tile_Kind__Two
        ;

    Chunk *p_chunk =
        get_p_chunk_from__global_space(p_global_space);

    for (Index__u32 index_of__tile = 0;
            index_of__tile <
            sizeof(
                p_chunk
                ->tiles) / sizeof(Tile);
            index_of__tile++) {
        p_chunk
            ->tiles[
                index_of__tile].the_kind_of_tile__this_tile_is =
                    the_kind_of__tile;
    }
}

void f_tile_render_kernel(
        Local_Space *p_local_space,
        Tile_Render_Kernel_Result *p_tile_kernel_render_results,
        Quantity__u32 quantity_of__tile_kernel_render_results,
        u8 x__local,
        u8 y__local,
        u8 z__local) {
    Chunk *p_chunk =
        get_p_chunk_from__local_space(
                p_local_space);

    if (!p_chunk) {
        for (Index__u32 index_of__tile_render_kernel_result = 0;
                index_of__tile_render_kernel_result 
                < quantity_of__tile_kernel_render_results;
                index_of__tile_render_kernel_result++) {
            Tile_Render_Kernel_Result *p_result =
                &p_tile_kernel_render_results[
                    index_of__tile_render_kernel_result];
            p_result->index_of__texture = 0;
        }
        return;
    }

    Tile *p_tile =
        get_p_tile_from__chunk_using__u8(
                p_chunk,
                x__local, 
                y__local, 
                z__local);

    for (Index__u32 index_of__tile_render_kernel_result = 0;
            index_of__tile_render_kernel_result 
            < quantity_of__tile_kernel_render_results;
            index_of__tile_render_kernel_result++) {
        Tile_Render_Kernel_Result *p_result =
            &p_tile_kernel_render_results[
                index_of__tile_render_kernel_result];
        switch (index_of__tile_render_kernel_result) {
            case 0:
                p_result->index_of__texture =
                    p_tile->the_kind_of_tile__this_tile_is;
                p_result->is_flipped__x = 0;
                p_result->is_flipped__y = 0;
                break;
            case 1:
                p_result->index_of__texture =
                    Tile_Kind__None;
                p_result->is_flipped__x = 0;
                p_result->is_flipped__y = 0;
                break;
        }
    }
}

void m_process__construct_global_node(
        Process *p_this_process,
        Game *p_game) {
    Global_Space *p_global_space =
        (Global_Space*)p_this_process->p_process_data;

    World *p_world = get_p_world_from__game(p_game);
    Process_Manager *p_process_manager =
        get_p_process_manager_from__game(p_game);
    Global_Space_Manager *p_global_space_manager =
        get_p_global_space_manager_from__world(p_world);
    Chunk_Pool *p_chunk_pool =
        get_p_chunk_pool_from__world(p_world);
    Collision_Node_Pool *p_collision_node_pool =
        get_p_collision_node_pool_from__world(p_world);

    Chunk *p_chunk =
        allocate_chunk_from__chunk_pool(
                p_chunk_pool, 
                GET_UUID_P(p_global_space));

    if (!p_chunk) {
        fail_process(p_this_process);
        drop_global_space_within__global_space_manager(
                p_global_space_manager,
                p_process_manager,
                p_global_space);
        return;
    }

    Collision_Node *p_collision_node =
        allocate_collision_node_from__collision_node_pool(
                p_collision_node_pool,
                GET_UUID_P(p_global_space));

    if (!p_collision_node) {
        release_chunk_from__chunk_pool(
                p_chunk_pool, 
                p_chunk);
        fail_process(p_this_process);
        drop_global_space_within__global_space_manager(
                p_global_space_manager, 
                p_process_manager,
                p_global_space);
        return;
    }

    p_global_space->p_chunk = p_chunk;
    p_global_space->p_collision_node = p_collision_node;
    f_Chunk_Generator f_chunk_generator =
        get_p_world_parameters_from__world(p_world)
        ->f_chunk_generator;
    f_chunk_generator(
            p_game,
            p_global_space);
    complete_process(p_this_process);
}

void m_process__deconstruct_global_node(
        Process *p_this_process,
        Game *p_game) {
    Global_Space *p_global_space =
        (Global_Space*)p_this_process->p_process_data;

    World *p_world = get_p_world_from__game(p_game);
    Process_Manager *p_process_manager =
        get_p_process_manager_from__game(p_game);
    Global_Space_Manager *p_global_space_manager =
        get_p_global_space_manager_from__world(p_world);
    Chunk_Pool *p_chunk_pool =
        get_p_chunk_pool_from__world(p_world);
    Collision_Node_Pool *p_collision_node_pool =
        get_p_collision_node_pool_from__world(p_world);
    
    Chunk *p_chunk =
        get_p_chunk_from__global_space(p_global_space);

    if (p_chunk) {
        release_chunk_from__chunk_pool(
                p_chunk_pool, 
                p_chunk);
    }

    Collision_Node *p_collision_node =
        get_p_collision_node_from__global_space(p_global_space);

    if (p_collision_node) {
        release_collision_node_from__collision_node_pool(
                p_collision_node_pool, 
                p_collision_node);
    }

    release_global_space_in__global_space_manager(
            p_global_space_manager, 
            p_global_space);

    complete_process(p_this_process);
}

void m_enter_scene__test(
        Scene *p_this_scene,
        Game *p_game) {
    Scene_Manager *p_scene_manager =
        get_p_scene_manager_from__game(p_game);

    Client *p_client =
        get_p_client_by__uuid_from__game(
                p_game, 
                0);

#ifndef IS_SERVER
    Graphics_Window *p_gfx_window__world =
        allocate_graphics_window_with__graphics_window_manager(
                get_p_gfx_context_from__game(p_game), 
                get_p_graphics_window_manager_from__gfx_context(
                    get_p_gfx_context_from__game(p_game)), 
                TEXTURE_FLAG__SIZE_256x256);

    Graphics_Window *p_gfx_window__world_cover =
        allocate_graphics_window_with__graphics_window_manager(
                get_p_gfx_context_from__game(p_game), 
                get_p_graphics_window_manager_from__gfx_context(
                    get_p_gfx_context_from__game(p_game)), 
                TEXTURE_FLAG__SIZE_256x256);

    set_graphics_window_as__rendering_world(
            p_gfx_window__world);
#else
    Graphics_Window *p_gfx_window__world = 0;
#endif

    initialize_world(
            p_game,
            get_p_world_from__game(p_game),
            m_process__construct_global_node,
            m_process__deconstruct_global_node,
            f_chunk_generator);

    Camera camera;

    initialize_camera(
            &camera,
            get_vector__3i32F4_using__i32(
                0, 0, 0),
            0, //nullptr handler
            CAMERA_FULCRUM__WIDTH,
            CAMERA_FULCRUM__WIDTH,
            -BIT(18),
            i32_to__i32F20(100)
            );

#ifndef IS_SERVER
    set_p_camera_of__graphics_window(
            p_gfx_window__world, 
            &camera);
    set_p_camera_of__graphics_window(
            p_gfx_window__world_cover, 
            &camera);

    PLATFORM_Texture *p_PLATFORM_texture_of__ground =
        get_p_PLATFORM_texture_by__alias(
                get_p_aliased_texture_manager_from__game(p_game), 
                "ground");
    PLATFORM_Texture *p_PLATFORM_texture_of__ground_cover =
        get_p_PLATFORM_texture_by__alias(
                get_p_aliased_texture_manager_from__game(p_game), 
                "cover");

    Graphics_Window *p_ptr_array_of__world_windows[] = {
        p_gfx_window__world,
        p_gfx_window__world_cover
    };

    PLATFORM_Texture *p_ptr_array_of__PLATFORM_textures[] = {
        p_PLATFORM_texture_of__ground,
        p_PLATFORM_texture_of__ground_cover
    };
#endif

    set_center_of__local_space_manager(
            get_p_global_space_manager_from__world(
                get_p_world_from__game(p_game)), 
            get_p_process_manager_from__game(p_game), 
            get_p_local_space_manager_from__client(p_client), 
            VECTOR__3i32__0_0_0);
    
    while (
            is_p_scene_the__active_scene_in__scene_manager(
                p_scene_manager, 
                p_this_scene)) {
        manage_game__pre_render(p_game);

        manage_world(
                p_game,
                p_gfx_window__world);

        poll_multiplayer(p_game);

#ifndef IS_SERVER
        if (is_input__forward_held(get_p_input_from__game(p_game))) {
            p_gfx_window__world
                ->p_camera
                ->position
                .y__i32F4 += 0b1000;
        }
        if (is_input__backward_held(get_p_input_from__game(p_game))) {
            p_gfx_window__world
                ->p_camera
                ->position
                .y__i32F4 -= 0b1000;
        }
        if (is_input__right_held(get_p_input_from__game(p_game))) {
            p_gfx_window__world
                ->p_camera
                ->position
                .x__i32F4 += 0b1000;
        }
        if (is_input__left_held(get_p_input_from__game(p_game))) {
            p_gfx_window__world
                ->p_camera
                ->position
                .x__i32F4 -= 0b1000;
        }
        
        PLATFORM_compose_world(
                get_p_gfx_context_from__game(p_game), 
                p_ptr_array_of__world_windows, 
                get_p_local_space_manager_from__client(p_client),
                p_ptr_array_of__PLATFORM_textures, 
                2, 
                f_tile_render_kernel);
#endif

        render_graphic_windows_in__graphics_window_manager(
                p_game);

        manage_game__post_render(p_game);
    }
}

void m_unload_scene__test(
        Scene *p_this_scene,
        Game *p_game) {

}
