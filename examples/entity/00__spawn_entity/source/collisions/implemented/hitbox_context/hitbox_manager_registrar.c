#include "collisions/implemented/hitbox_context/hitbox_manager_registrar.h"
#include "collisions/hitbox_context.h"
#include "collisions/core/aabb/hitbox_aabb_manager.h"
#include "debug/debug.h"
#include "defines.h"
#include <stdlib.h>

// ***) The engine's stock AABB hitbox allocator (core) uses
// malloc for the hitbox pool: freshly allocated hitboxes can
// inherit STALE position/velocity/acceleration bytes from
// whatever lived in that memory before. A client/entity
// hitbox that starts with a garbage velocity is immediately
// thrown through the world by the collision resolver's
// gravity pass, and the game crawls to a halt (quadratic
// ray-cast cost) while collision-node updates fail against
// chunks that no longer have global spaces.
//
// This project's allocator is the stock allocator, except the
// hitbox pool is calloc'ed so every hitbox starts at (0,0,0)
// with zero velocity and acceleration.
static void *m_f_hitbox_manager__allocator_zeroed_AABB(
        Hitbox_Manager_Type the_type_of__hitbox_manager_to__allocate,
        Quantity__u32 quantity_of__hitboxes_to__pool) {
    (void)the_type_of__hitbox_manager_to__allocate;
    void *pM_hitbox_manager = malloc(sizeof(Hitbox_AABB_Manager));
    if (!pM_hitbox_manager) {
        debug_error("m_f_hitbox_manager__allocator_zeroed_AABB, failed to allocate manager.");
        return 0;
    }

    void *pM_pool_of__hitboxes =
        calloc(quantity_of__hitboxes_to__pool, sizeof(Hitbox_AABB));
    if (!pM_pool_of__hitboxes) {
        debug_error("m_f_hitbox_manager__allocator_zeroed_AABB, failed to allocate hitbox pool.");
        free(pM_hitbox_manager);
        return 0;
    }

    void *pM_ptr_array_of__hitbox_records =
        calloc(quantity_of__hitboxes_to__pool, sizeof(Hitbox_AABB*));
    if (!pM_ptr_array_of__hitbox_records) {
        debug_error("m_f_hitbox_manager__allocator_zeroed_AABB, failed to allocate hitbox pointer array.");
        free(pM_hitbox_manager);
        free(pM_pool_of__hitboxes);
        return 0;
    }

    Hitbox_AABB_Manager *p_hitbox_manager__aabb =
        (Hitbox_AABB_Manager*)pM_hitbox_manager;

    initialize_hitbox_aabb_manager(
            p_hitbox_manager__aabb,
            pM_pool_of__hitboxes,
            pM_ptr_array_of__hitbox_records,
            quantity_of__hitboxes_to__pool
            );

    return p_hitbox_manager__aabb;
}

void register_hitbox_managers(Hitbox_Context *p_hitbox_context) {
    debug_warning("Be sure to register the correct hitbox managers for your project.");
    debug_warning("Registering just Hitbox_AABB_Manager");

    register_hitbox_manager(
            p_hitbox_context, 
            m_f_hitbox_manager__allocator_zeroed_AABB, 
            f_hitbox_manager__deallocator_AABB, 
            f_hitbox_manager__opaque_property_access_of__hitbox_AABB,
            Hitbox_Manager_Type__AABB, 
            QUANTITY_OF__HITBOX_COMPONENTS(dimensions, 2), 
            QUANTITY_OF__HITBOX_COMPONENTS(pos_vel, 3), 
            SIZE_OF__HITBOX_COMPONENTS(dimensions, sizeof(i32)), 
            SIZE_OF__HITBOX_COMPONENTS(pos_vel, sizeof(i32F4)), 
            SIZE_OF__HITBOX_COMPONENTS(acceleration, sizeof(i16F8)), 
            FRACTIONAL_PERCISION_OF__HITBOX_COMPONENTS(
                dimensions,
                FRACTIONAL_PERCISION_0__BIT_SIZE), 
            FRACTIONAL_PERCISION_OF__HITBOX_COMPONENTS(
                pos_vel,
                FRACTIONAL_PERCISION_4__BIT_SIZE), 
            FRACTIONAL_PERCISION_OF__HITBOX_COMPONENTS(
                acceleration,
                FRACTIONAL_PERCISION_16__BIT_SIZE)
            );
}
