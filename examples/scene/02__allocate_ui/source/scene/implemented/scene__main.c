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
#include "types/implemented/rendering/graphics_window_kind.h"
#include "ui/implemented/ui_window_registrar.h"
#include "ui/ui_context.h"
#include "ui/ui_manager.h"
#include "ui/ui_tile_map_manager.h"
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
static Graphics_Window *p_gfx_window__backbuffer = 0;
static Graphics_Window *p_gfx_window__ground = 0;
static Graphics_Window *p_gfx_window__ui__hud = 0;

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

    // 7) Acquire the platform-provided (backbuffer) graphics
    // window. This is the ROOT of the graphics window hierarchy;
    // it is presented to the screen.
    p_gfx_window__backbuffer =
        get_default_platform_graphics_window(
                get_p_gfx_context_from__game(p_game));
    if (!p_gfx_window__backbuffer) {
        debug_abort("m_load_scene_as__main_handler, no platform graphics window.");
        return;
    }

    // 8) Allocate a "ground" graphics window as a CHILD of the
    // backbuffer, and let IT compose the world. NOTE: the
    // platform's world compositor (GL_compose_world) treats each
    // CHILD of the composed window as a world render layer, so
    // anything that is not a world layer (like UI windows) must
    // NOT be a child of this window.
    p_gfx_window__ground =
        allocate_graphics_window_from__graphics_window_manager(
                get_p_gfx_context_from__game(p_game),
                get_p_graphics_window_manager_from__gfx_context(
                    get_p_gfx_context_from__game(p_game)),
                TEXTURE_FLAGS(
                    TEXTURE_FLAG__SIZE_256x256,
                    0,
                    TEXTURE_FLAG__FORMAT__RGBA8888));
    if (!p_gfx_window__ground) {
        debug_abort("m_load_scene_as__main_handler, no ground graphics window.");
        return;
    }
    set_graphics_window__tile_map__texture(
            p_gfx_window__ground,
            uuid_of__tileset_texture);
    share_hitbox_manager_with__graphics_window(
            p_gfx_window__ground,
            GET_UUID_P(get_p_world_from__game(p_game)));
    p_gfx_window__ground->f_PLATFORM_compose_gfx_window =
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
            p_gfx_window__ground,
            &_main_camera);
    set_graphics_window_as__parent_to__this_graphics_window(
            get_p_graphics_window_manager_from__gfx_context(
                get_p_gfx_context_from__game(p_game)),
            p_gfx_window__backbuffer,
            p_gfx_window__ground);

    // 9) Register our UI windows. This only fills in the
    // UI_Window_Records (load/close functions + pool quantities)
    // keyed by Graphics_Window_Kind; the windows themselves are
    // opened later with open_ui_window().
    register_ui_windows(
            get_p_gfx_context_from__game(p_game));
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

    // 9) Open the HUD UI window.
    //
    // We do the "open" manually (allocate -> equip -> populate)
    // because the record's load function runs at populate time
    // and NEEDS the window to already be fully equipped:
    //   1) allocate the Graphics_Window (with a fixed uuid so we
    //      can reference it later, e.g. to close it on unload);
    //   2) give it a ui_tile_map + point its ui_tile_map__texture
    //      at the tileset (UI tile spans draw 8px sub-tiles out
    //      of THIS texture, not the world tile_map__texture);
    //   3) share the world's hitbox manager (UI element hitboxes
    //      are allocated here);
    //   4) allocate the ui_manager;
    //   5) populate: sets the window kind, runs the registered
    //      load function (building the buttons), marks the
    //      window enabled + in need of composition.
    Gfx_Context *p_gfx_context =
        get_p_gfx_context_from__game(p_game);
    Graphics_Window_Manager *p_gfx_window_manager =
        get_p_graphics_window_manager_from__gfx_context(
            p_gfx_context);
    Identifier__u32 uuid_of__gfx_window__ui__hud = 1;
    p_gfx_window__ui__hud =
        allocate_graphics_window_with__uuid_from__graphics_window_manager(
                p_gfx_context,
                p_gfx_window_manager,
                uuid_of__gfx_window__ui__hud,
                TEXTURE_FLAGS(
                    TEXTURE_FLAG__SIZE_256x256,
                    0,
                    TEXTURE_FLAG__FORMAT__RGBA8888));
    if (!p_gfx_window__ui__hud) {
        debug_error("m_enter_scene_as__main_handler, failed to allocate HUD graphics window.");
    } else {
        // ***) 1.5) Give the HUD window position Z=1 so it renders
        // ABOVE the ground window (Z=0): siblings render in order
        // of their window position's Z. NOTE: this must happen
        // BEFORE the UI is populated; moving a window afterwards
        // shifts its UI elements through the hitbox manager
        // (which expects the ui_manager to OWN that manager).
        set_position_3i32_of__graphics_window(
                p_game,
                p_gfx_window__ui__hud,
                get_vector__3i32(0, 0, 1));

        // ***) 2) UI tile map + its texture (the tileset).
        set_graphics_window__ui_tile_map(
                p_gfx_window__ui__hud,
                allocate_ui_tile_map_with__ui_tile_map_manager(
                        get_p_ui_tile_map_manager_from__gfx_context(
                            p_gfx_context),
                        UI_Tile_Map_Size__Large));
        Identifier__u32 uuid_of__tileset_texture =
            get_uuid_of__aliased_texture(
                    get_p_aliased_texture_manager_from__game(p_game),
                    name_of__texture__tileset);
        set_graphics_window__ui_tile_map__texture(
                p_gfx_window__ui__hud,
                uuid_of__tileset_texture);

        // ***) 3) Share the world's hitbox manager with the HUD
        // so its UI elements get hitboxes in it.
        share_hitbox_manager_with__graphics_window(
                p_gfx_window__ui__hud,
                GET_UUID_P(get_p_world_from__game(p_game)));

        // ***) 4) Allocate the ui_manager (capacity 16).
        allocate_ui_manager_for__graphics_window(
                p_gfx_context,
                p_gfx_window__ui__hud,
                16);

        // ***) 5) Populate the window with its UI (runs
        // allocate_ui_for__ui_window__main).
        populate_window_with__ui(
                p_game,
                p_gfx_window__ui__hud,
                Graphics_Window_Kind__UI__Hud,
                0);

        // ***) Render the HUD on top of the world: make it a
        // CHILD of the BACKBUFFER window (a SIBLING of the
        // ground window; the Z=1 window position set above keeps
        // it drawn above the ground's Z=0). It must NOT be a
        // child of the ground window (that would make the world
        // compositor treat it as a world render layer).
        set_graphics_window_as__parent_to__this_graphics_window(
                p_gfx_window_manager,
                p_gfx_window__backbuffer,
                p_gfx_window__ui__hud);
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

        // 10) Poll the HUD ui_manager for input (focus, clicks,
        // drops, ...). The SDL platform does NOT poll ui
        // managers for you; call this yourself every frame for
        // each window you want to be interactive.
        if (p_gfx_window__ui__hud) {
            poll_ui_manager__update(
                    get_p_ui_manager_from__graphics_window(
                        p_game,
                        p_gfx_window__ui__hud),
                    p_game,
                    p_gfx_window__ui__hud);
        }
        // GEN-PRE-RENDER-END

        // 11) The SDL platform does not compose or render the
        // graphics windows for us, so we do it here: mark the
        // ground window dirty, compose (this runs the tile
        // render kernel into the chunk textures), then render
        // all windows (children first, parents after) to screen.
        // NOTE: the HUD window re-marks itself dirty through its
        // (dirty) ui_manager every frame, so it keeps composing.
        set_graphics_window_as__in_need_of__composition(
                p_gfx_window__ground);
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
    // 12) Close the HUD window: runs the record's close function
    // (which releases the ui elements) and releases the
    // Graphics_Window itself.
    if (p_gfx_window__ui__hud) {
        close_ui_window(
                p_game,
                GET_UUID_P(p_gfx_window__ui__hud));
        p_gfx_window__ui__hud = 0;
    }
    // 13) Release the ground window (a plain child window; the
    // backbuffer is platform-provided and outlives the scene).
    if (p_gfx_window__ground) {
        release_graphics_window_from__graphics_window_manager(
                p_game,
                p_gfx_window__ground);
        p_gfx_window__ground = 0;
    }
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
