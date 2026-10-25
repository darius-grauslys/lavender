#include "entity/implemented/entity__dummy.h"
#include "collisions/core/aabb/hitbox_aabb.h"
#include "collisions/core/aabb/hitbox_aabb_manager.h"
#include "collisions/hitbox_context.h"
#include "defines.h"
#include "defines_weak.h"
#include "entity/entity_manager.h"
#include "game.h"
#include "rendering/aliased_texture_manager.h"
#include "rendering/graphics_window.h"
#include "rendering/implemented/aliased_texture_registrar.h"
#include "rendering/sprite_manager.h"
#include "world/world.h"

// ***) The entity's update handler. Called by manage_world()
// (via manage_world__entities) once per game tick for every
// enabled entity.
//
// Entity construction is LAZY: allocation only registers the
// entity; its components (sprite, hitbox) are built here, the
// first tick it runs. Both allocations are uuid-keyed (the
// entity's uuid), so re-running them later is a no-op that just
// returns the existing allocation.
void m_entity_handler__update_dummy(
        Entity *p_this_entity,
        Game *p_game,
        World *p_world) {
    // ***) The sprite: the window that renders the world
    // (world->p_graphics_window_for__world) must own a sprite
    // manager. The sprite tracks the entity's hitbox position
    // automatically at render time.
    //
    // NOTE: allocate_sprite_from__sprite_manager is NOT
    // idempotent — it grabs a fresh pool slot (and a fresh
    // platform texture + vertex object) on every call, so we
    // look the sprite up by uuid first and only allocate it on
    // the first tick. Re-allocating it every tick leaks the
    // sprite manager's fixed render-record array and corrupts
    // the heap (a segfault in the GL driver a dozen frames in).
    Graphics_Window *p_gfx_window =
        get_p_graphics_window_from__world(p_world);
    if (p_gfx_window) {
        Sprite_Manager *p_sprite_manager =
            get_p_sprite_manager_from__graphics_window(
                    p_game, p_gfx_window);
        // NOTE: the lookup dehashes the pool and may return a
        // DEALLOCATED slot (first run), so validate that the
        // slot is actually allocated to us before skipping.
        Sprite *p_sprite =
            get_p_sprite_by__uuid_from__sprite_manager(
                    p_sprite_manager,
                    GET_UUID_P(p_this_entity));
        if (!p_sprite
                || is_sprite__deallocated(p_sprite)) {
            Texture texture_of__dummy;
            get_texture_by__alias(
                    get_p_aliased_texture_manager_from__game(p_game),
                    name_of__texture__dummy,
                    &texture_of__dummy);
            p_sprite =
                allocate_sprite_from__sprite_manager(
                        get_p_gfx_context_from__game(p_game),
                        p_sprite_manager,
                        p_gfx_window,
                        GET_UUID_P(p_this_entity),
                        texture_of__dummy,
                        TEXTURE_FLAGS(
                            TEXTURE_FLAG__SIZE_16x16,
                            TEXTURE_FLAG__RENDER_METHOD__0,
                            TEXTURE_FLAG__FORMAT__RGBA8888));
            if (!p_sprite) {
                debug_error("m_entity_handler__update_dummy, failed to allocate sprite.");
                set_entity_as__disabled(p_this_entity);
                return;
            }
        }
    }

    // ***) The hitbox: allocated by the scene's create_client
    // process (it must exist, at the spawn point, before the
    // load_client game action's outbound check runs), keyed by
    // the entity's uuid (which is the client's uuid for our
    // dummy, so the client and entity share one hitbox).
    Hitbox_AABB_Manager *p_hitbox_aabb_manager =
        (Hitbox_AABB_Manager*)get_pV_hitbox_manager_from__hitbox_context(
                get_p_hitbox_context_from__game(p_game),
                GET_UUID_P(get_p_world_from__game(p_game)));
    Hitbox_AABB *p_hitbox_aabb =
        get_p_hitbox_aabb_by__uuid_u32_from__hitbox_aabb_manager(
                p_hitbox_aabb_manager,
                GET_UUID_P(p_this_entity));
    if (!p_hitbox_aabb) {
        debug_error("m_entity_handler__update_dummy, hitbox not found.");
        set_entity_as__disabled(p_this_entity);
        return;
    }
    // ***) set_size marks the hitbox dirty, which is what makes
    // the collision system's per-tick movement pass (gravity)
    // run for it. With ground registered in the tile logic
    // table, the collision resolver's falling ray-cast finds
    // the floor and the dummy lands on it and stays there.
    set_size_of__hitbox_aabb(p_hitbox_aabb, 8, 8);
}

// ***) Register the dummy entity kind: fill in its function
// table and hand it to the entity manager.
void register_entity_dummy_into__entity_manager(
        Entity_Manager *p_entity_manager) {
    Entity_Functions entity_functions__dummy;
    memset(&entity_functions__dummy, 0, sizeof(Entity_Functions));
    entity_functions__dummy.m_entity_update_handler =
        m_entity_handler__update_dummy;

    register_entity_into__entity_manager(
            p_entity_manager,
            Entity_Kind__Dummy,
            entity_functions__dummy);
}
