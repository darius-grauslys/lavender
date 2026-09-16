#include "debug/debug.h"
#include "defines.h"
#include "defines_weak.h"
#include "vectors.h"
#include <collisions/collision_utils.h>
#include <collisions/core/aabb/hitbox_aabb_manager.h>
#include <world/global_space_manager.h>
#include <world/global_space.h>
#include "vectors.h"
#include <world/chunk_vectors.h>
#include <collisions/collision_node_pool.h>
#include <collisions/collision_node.h>
#include <game.h>


Global_Space *_get_global_space_of_position_for__collision_utils(
        Game *p_game,
        Vector__3i32F4 position__3i32F4) {
    Global_Space *p_global_space =
        (is_world_allocated_for__game(p_game))
        ? get_p_global_space_from__global_space_manager(
                get_p_global_space_manager_from__game(p_game), 
                vector_3i32F4_to__chunk_vector_3i32(
                    position__3i32F4))
        : 0
        ;

    return p_global_space;
}

Vector__3i32F4 _resolve_hitbox_position_for__collision_utils(
        Game *p_game,
        Identifier__u32 uuid__u32) {
    // TODO: need to replace AABBs with opaque variants
    Hitbox_AABB_Manager *p_hitbox_aabb_manager =
        GET_P_HITBOX_AABB_MANAGER_FROM__GAME_WORLD(p_game);
    
    if (!p_hitbox_aabb_manager) {
        return VECTOR__3i32F4__OUT_OF_BOUNDS;
    }

    Hitbox_AABB *p_hitbox_aabb =
        get_p_hitbox_aabb_by__uuid_u32_from__hitbox_aabb_manager(
                p_hitbox_aabb_manager, 
                uuid__u32);

    if (!p_hitbox_aabb) {
        return VECTOR__3i32F4__OUT_OF_BOUNDS;
    }

    return p_hitbox_aabb->position__3i32F4;
}

static inline
bool _resolve_collision_components_for__collision_utils(
        Game *p_game,
        Identifier__u32 uuid__u32,
        Vector__3i32F4 *p_OUT_position__3i32F4,
        Collision_Node_Pool **p_ptr_OUT_collision_node_pool,
        Collision_Node **p_ptr_OUT_collision_node) {
    *p_OUT_position__3i32F4 =
        VECTOR__3i32F4__OUT_OF_BOUNDS;
    *p_ptr_OUT_collision_node_pool = 0;
    *p_ptr_OUT_collision_node = 0;

    Vector__3i32F4 position__3i32F4 =
        _resolve_hitbox_position_for__collision_utils(
                p_game, 
                uuid__u32);

    if (is_vectors_3i32F4__out_of_bounds(position__3i32F4)) {
        // Idempotent short circuit.
        debug_warning("attach_object_to__collision_system, could not resolve hitbox.");
        return false;
    }

    Global_Space *p_global_space =
        _get_global_space_of_position_for__collision_utils(
                p_game, 
                position__3i32F4);

    if (!p_global_space) {
        // Idempotent short circuit, collision node
        // does not exist at hitbox's current position.
        debug_warning("attach_object_to__collision_system, hitbox out of bounds.");
        return false;
    }

    if (p_OUT_position__3i32F4)
        *p_OUT_position__3i32F4 =
            position__3i32F4;

    Collision_Node_Pool *p_collision_node_pool =
        get_p_collision_node_pool_from__world(
                get_p_world_from__game(p_game));
    Collision_Node *p_collision_node =
        get_p_collision_node_from__global_space(
                p_global_space);

    bool existence = 
        is_collision_node_entry__present(
                p_collision_node_pool, 
                p_collision_node,
                uuid__u32);

    if (p_ptr_OUT_collision_node)
        *p_ptr_OUT_collision_node =
            p_collision_node;
    if (p_ptr_OUT_collision_node)
        *p_ptr_OUT_collision_node =
            p_collision_node;

    return existence;
}

void attach_object_to__collision_system(
        Game *p_game,
        World *p_world,
        Identifier__u32 uuid__u32) {
    Collision_Node_Pool *p_collision_node_pool = 0;
    Collision_Node *p_collision_node = 0;
    Vector__3i32F4 position__3i32F4;

    if (_resolve_collision_components_for__collision_utils(
                p_game, 
                uuid__u32, 
                &position__3i32F4, 
                &p_collision_node_pool, 
                &p_collision_node)) {
        // Idempotent short circuit
        return;
    }

    if (is_vectors_3i32F4__out_of_bounds(position__3i32F4)) {
        debug_warning("attach_object_to__collision_system, position out of bounds.");
        return;
    }

    if (!p_collision_node_pool || !p_collision_node) {
        debug_warning("attach_object_to__collision_system, failed to attach.");
        return;
    }

    // Attach hitbox to collision system.
    add_entry_to__collision_node(
            p_collision_node_pool, 
            p_collision_node, 
            uuid__u32);
}

void detach_object_from__collision_system(
        Game *p_game,
        World *p_world,
        Identifier__u32 uuid__u32) {
    Collision_Node_Pool *p_collision_node_pool = 0;
    Collision_Node *p_collision_node = 0;
    Vector__3i32F4 position__3i32F4;

    if (!_resolve_collision_components_for__collision_utils(
                p_game, 
                uuid__u32, 
                &position__3i32F4, 
                &p_collision_node_pool, 
                &p_collision_node)) {
        // Idempotent short circuit
        return;
    }

    // Detach hitbox to collision system.
    remove_entry_from__collision_node(
            p_collision_node_pool, 
            p_collision_node, 
            uuid__u32);
}
