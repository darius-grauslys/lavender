#include "scene/implemented/scene__main.h"
#include "client.h"
#include "collisions/core/aabb/hitbox_aabb_manager.h"
#include "defines.h"
#include "debug/opengl/gl_debug_screen.h"
#include "game_action/core/world/game_action__world__load_client.h"
#include "game_action/core/world/game_action__world__load_world.h"
#include "process/process.h"
#include "rendering/aliased_texture_manager.h"
#include "rendering/gfx_context.h"
#include "rendering/graphics_window.h"
#include "rendering/graphics_window_manager.h"
#include <rendering/implemented/aliased_texture_registrar.h>
#include "scene/scene.h"
#include "scene/scene_manager.h"
#include "game.h"
#include "serialization/serialization_header.h"
#include "world/chunk.h"
#include "world/camera.h"
#include "world/implemented/chunk_generator_registrar.h"
#include "world/implemented/tile_logic_table_registrar.h"
#include "world/local_space.h"
#include "world/world.h"
#include "game_action/implemented/game_action_registrar.h"
// GEN-INCLUDE-BEGIN
// GEN-INCLUDE-END

// TUTORIAL NOTE:
// The render region is a FIXED 4x3 chunk band relative to the
// local space manager center:
//   x in [lsm_x-2, lsm_x+1],  y in [lsm_y-3, lsm_y-1]
// So to center the band on a chunk (cx, cy) in pixels:
//   camera = ((cx - 0.5) * 64, (cy - 1.5) * 64)
#define SPAWN_TILE_X 0
#define SPAWN_TILE_Y 0
#define SPAWN_X__PX (SPAWN_TILE_X * 8)
#define SPAWN_Y__PX (SPAWN_TILE_Y * 8)
// LSM center is the spawn chunk (0,0) -> band center px = (-32, -96).
#define CAM_X__PX (-32)
#define CAM_Y__PX (-96)

static Camera _main_camera;
static Graphics_Window *p_gfx_window__world = 0;

// GEN-FORWARD-BEGIN
// ***) Define a basic client creation process
void m_process__create_client(
        Process *p_this_process,
        Game *p_game) {
    // Note, if a client needs to have certain additional resources
    // such as an entity, this is where you would allocate them.
    Client *p_client = (Client*)p_this_process->p_process_data;

    // It is our responsibility for create_client
    // to set it as loaded, not active.
    set_client_as__loaded(p_client);
    complete_process(p_this_process);
}
// GEN-FORWARD-END

// ***) The tile render kernel.
// Called once per tile, per graphics window, when a chunk is
// composed. Maps the ground tile kind straight onto the
// tilesheet index (the Tile_Kind values are defined 1:1 with
// the tilesheet index slots, 0 = None = transparent/skip).
void m_f_tile_render_kernel__checkerboard(
        Local_Space *p_local_space,
        Tile_Render_Kernel_Result *p_tile_kernel_render_results,
        Quantity__u32 quantity_of__tile_kernel_render_results,
        u8 x__local,
        u8 y__local,
        u8 z__local) {
    Chunk *p_chunk =
        get_p_chunk_from__global_space(
                get_p_global_space_from__local_space(p_local_space));
    Tile *p_tile = 0;
    if (p_chunk) {
        p_tile = get_p_tile_from__chunk(
                p_chunk,
                (Local_Tile_Vector__3u8){x__local, y__local, z__local});
    }
    if (!quantity_of__tile_kernel_render_results) {
        return;
    }
    // index_of__texture is 1-based by convention: 0 = transparent.
    p_tile_kernel_render_results[0].index_of__texture =
        (Index__u16)(p_tile ? p_tile->the_kind_of__tile : 0);
    p_tile_kernel_render_results[0].is_flipped__x = 0;
    p_tile_kernel_render_results[0].is_flipped__y = 0;
}

void m_load_scene_as__main_handler(
        Scene *p_this_scene,
        Game *p_game) {
    // GEN-LOAD-BEGIN
    // 1) Load tilesheet texture.
    register_aliased_textures(
            get_p_aliased_texture_manager_from__gfx_context(
                get_p_gfx_context_from__game(p_game)), 
            p_game);
    
    // ***) register game actions for single player
    register_game_actions__offline(
            get_p_game_action_logic_table_from__game(p_game));

    // 2) Allocate the world.
    bool is_world__successfully_allocated =
        allocate_world_for__game(p_game);

    // 3) Verify allocation worked.
    if (!is_world__successfully_allocated) {
        debug_abort("m_enter_scene_as__main_handler, allocate_world_for__game failed.");
        // NOTE: debug_abort should cause the game to crash.
        // However to make sure we exit we can call
        // quit_scene_state_machine.
        quit_scene_state_machine(
                get_p_scene_manager_from__game(p_game));
        return;
    }

    // ***) Do not forget to initialize the world!
    initialize_world(
            p_game, 
            get_p_world_from__game(p_game));

    // 4) Register the chunk generators, by default this will
    // register a blank chunk generator.
    register_chunk_generators(
            get_p_chunk_generation_table_from__game(p_game));

    register_tile_logic_tables(
            p_game, 
            get_p_tile_logic_context_from__world(
                get_p_world_from__game(p_game)));

    Identifier__u32 uuid_of__tileset_texture =
        get_uuid_of__aliased_texture(
                get_p_aliased_texture_manager_from__game(p_game),
                name_of__texture__tileset);

    if (is_identifier_u32__invalid(uuid_of__tileset_texture)) {
        debug_error("m_load_scene_as__main_handler, failed to load tileset texture.");
    }

    // 5) The world loads its local space around the spawn point,
    // so give it one to load at.
    get_p_world_from__game(p_game)->spawn_point =
        get_vector__3i32F4(
                i32_to__i32F4(SPAWN_X__PX),
                i32_to__i32F4(SPAWN_Y__PX),
                i32_to__i32F4(0));

    // 6) Register the tile render kernel. Without one the
    // renderer has no way to know which tilesheet index to
    // draw for a tile (the kernel is NOT set by initialize_world).
    set_f_tile_render_kernel_of__world(
            get_p_world_from__game(p_game),
            m_f_tile_render_kernel__checkerboard);

    allocate_hitbox_manager_from__hitbox_context(
            get_p_hitbox_context_from__game(p_game),
            GET_UUID_P(get_p_world_from__game(p_game)),
            Hitbox_Manager_Type__AABB,
            256);

    allocate_client_pool_for__game(
            p_game,
            1);

    allocate_hitbox_aabb_from__hitbox_aabb_manager(
            GET_P_HITBOX_AABB_MANAGER_FROM__GAME_WORLD(p_game), 
            GET_UUID_P(get_p_local_client_by__from__game(p_game)));
    set_dispatch_handler_process_for__create_client(
            p_game,
            m_process__create_client);

    // 7) Set up the platform-provided (backbuffer) graphics window
    // to compose the world: point it at the tileset, give it a
    // static camera centered on the render band, and share the
    // hitbox manager with it.
    p_gfx_window__world = 
        allocate_graphics_window_with__uuid_from__graphics_window_manager(
                get_p_gfx_context_from__game(p_game), 
                get_p_graphics_window_manager_from__gfx_context(
                    get_p_gfx_context_from__game(p_game)), 
                GET_UUID_P(get_p_world_from__game(p_game)), 
                TEXTURE_FLAGS(
                    TEXTURE_FLAG__SIZE_256x256,
                    0,
                    TEXTURE_FLAG__FORMAT__RGBA8888));
    if (!p_gfx_window__world) {
        debug_abort("m_load_scene_as__main_handler, no platform graphics window.");
        return;
    }
    set_graphics_window__tile_map__texture(
            p_gfx_window__world, 
            uuid_of__tileset_texture);
    share_hitbox_manager_with__graphics_window(
            p_gfx_window__world,
            GET_UUID_P(get_p_world_from__game(p_game)));
    p_gfx_window__world->f_PLATFORM_compose_gfx_window =
        PLATFORM_compose_world;
    initialize_camera(
            &_main_camera,
            get_vector__3i32F4(
                i32_to__i32F4(CAM_X__PX),
                i32_to__i32F4(CAM_Y__PX),
                i32_to__i32F4(0)),
            0, // m_camera_handler__default (static)
            CAMERA_FULCRUM__WIDTH,
            CAMERA_FULCRUM__WIDTH,
            i32_to__i32F20(-10),
            i32_to__i32F20(100));
    set_p_camera_of__graphics_window(
            p_gfx_window__world, 
            &_main_camera);
    // GEN-LOAD-END
}

void m_enter_scene_as__main_handler(
        Scene *p_this_scene,
        Game *p_game) {
    // ***) Load the world and a client with client UUID 0.
    // NOTE: for multiplayer a unique UUID would be given to each client.
    // since this is a single player example, setting 0 is fine.
    // NOTE: "load" in this sense will look for a pre-existing world file
    // and pre-existing client file. If none are found, they are created.
    Process *p_process_load_world =
        dispatch_game_action__world__load_world_and__get_a_process(
                p_game, 
                GET_UUID_P(get_p_local_client_by__from__game(p_game)));
    Process *p_process_load_client =
        dispatch_game_action__world__load_client_and__get_a_process(
                p_game, 
                GET_UUID_P(get_p_local_client_by__from__game(p_game)));

    // ***) The client process depends on the world process finishing first.
    enqueue_process(
            p_process_load_client, 
            p_process_load_world);

    // NOTE: it is actually more preferable in a single player
    // game to have a dedicated scene for polling the deserialization
    // processes instead of making a loop like this:
    while (poll_is__scene_active(
                p_game, 
                p_this_scene)) {
        while(!poll__game_tick_timer(p_game));
        manage_game__pre_render(p_game);
        manage_game__post_render(p_game); // <- poll processes
        if (is_process__finished(p_process_load_client)) {
            break;
        }
    }

    Quantity__u32 frame_count = 0;
    bool has_taken__screenshot = false;
    #define MAIN_FRAMES_BEFORE_SCREENSHOT 60
    while (poll_is__scene_active(
                p_game, 
                p_this_scene)) {
        while(!poll__game_tick_timer(p_game));
        // GEN-FRAME-BEGIN
        // GEN-FRAME-END
        manage_game__pre_render(p_game);
        // GEN-PRE-RENDER-BEGIN
        // 5) Poll the world for updates every game tick.
        manage_world(p_game);
        // GEN-PRE-RENDER-END

        // 8) The SDL platform does not compose or render the
        // graphics windows for us, so we do it here: mark the
        // world window dirty, compose (this runs the tile render
        // kernel into the chunk textures), then render to screen.
        set_graphics_window_as__in_need_of__composition(
                p_gfx_window__world);
        compose_graphic_windows_in__graphics_window_manager(p_game);
        render_graphic_windows_in__graphics_window_manager(p_game);

        if (!has_taken__screenshot
                && ++frame_count >= MAIN_FRAMES_BEFORE_SCREENSHOT) {
            if (gl_debug_screencap(p_game)) {
                debug_info("scene__main: wrote screen.png "
                        "(spawn %d,%d cam %d,%d)",
                        SPAWN_X__PX, SPAWN_Y__PX,
                        CAM_X__PX, CAM_Y__PX);
            }
            has_taken__screenshot = true;
        }

        manage_game__post_render(p_game);
        // GEN-POST-RENDER-BEGIN
        // GEN-POST-RENDER-END
    }
}

void m_unload_scene_as__main_handler(
        Scene *p_this_scene,
        Game *p_game) {
    // GEN-UNLOAD-BEGIN
    // 6) Clean up!
    release_all_aliased_textures(
            get_p_gfx_context_from__game(p_game), 
            get_p_aliased_texture_manager_from__gfx_context(
                get_p_gfx_context_from__game(p_game)));
    // GEN-UNLOAD-END
}

void register_scene__main(Scene_Manager *p_scene_manager) {
    register_scene_into__scene_manager(
            p_scene_manager, 
            Scene_Kind__None, 
            m_load_scene_as__main_handler, 
            m_enter_scene_as__main_handler, 
            m_unload_scene_as__main_handler);
}

// GEN-UI-MANAGEMENT-BEGIN
// GEN-UI-MANAGEMENT-END
