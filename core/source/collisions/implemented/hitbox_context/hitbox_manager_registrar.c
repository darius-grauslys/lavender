#include "collisions/implemented/hitbox_context/hitbox_manager_registrar.h"
#include "collisions/hitbox_context.h"
#include "collisions/core/aabb/hitbox_aabb_manager.h"
#include "debug/debug.h"
#include "defines.h"
#include "types/implemented/hitbox_manager_type.h"

void register_hitbox_managers(Hitbox_Context *p_hitbox_context) {
    debug_warning("Be sure to register the correct hitbox managers for your project.");
    debug_warning("Registering just Hitbox_AABB_Manager");

    register_hitbox_manager(
            p_hitbox_context, 
            f_hitbox_manager__allocator_AABB, 
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
