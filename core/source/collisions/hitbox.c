#include "collisions/collision_node.h"
#include "collisions/hitbox_context.h"
#include "debug/debug.h"
#include "defines.h"
#include "defines_weak.h"
#include "game.h"
#include "world/chunk_vectors.h"
#include "world/global_space.h"
#include "world/global_space_manager.h"
#include "world/world.h"
#include <collisions/hitbox.h>

void f_object_handler__hitbox__activate(
        Game *p_game,
        Identifier__u32 uuid_of__object__u32) {
    // TODO need to do existance check to avoid error printout.

    Hitbox_Flags__u8 hitbox_flags__u8 = 
        HITBOX_FLAG__IS_ACTIVE;
    Hitbox_Flags__u8 hitbox_flags__mask__u8 =
        HITBOX_FLAG__IS_ACTIVE;
    opaque_access_to__hitbox(
            get_p_hitbox_context_from__game(p_game), 
            GET_UUID_P(get_p_world_from__game(p_game)), 
            uuid_of__object__u32, 
            0, 
            0, 
            0, 
            0, 
            &hitbox_flags__u8,
            &hitbox_flags__mask__u8,
            OPAQUE_ACCESS__HITBOX__IS_SETTING);
}
void f_object_handler__hitbox__deactivate(
        Game *p_game,
        Identifier__u32 uuid_of__object__u32) {
    // TODO need to do existance check to avoid error printout.

    Hitbox_Flags__u8 hitbox_flags__u8 = 
        ~HITBOX_FLAG__IS_ACTIVE;
    Hitbox_Flags__u8 hitbox_flags__mask__u8 =
        HITBOX_FLAG__IS_ACTIVE;
    opaque_access_to__hitbox(
            get_p_hitbox_context_from__game(p_game), 
            GET_UUID_P(get_p_world_from__game(p_game)), 
            uuid_of__object__u32, 
            0, 
            0, 
            0, 
            0, 
            &hitbox_flags__u8,
            &hitbox_flags__mask__u8,
            OPAQUE_ACCESS__HITBOX__IS_SETTING);
}

void f_object_handler__hitbox__pre_teleport(
        Game *p_game,
        Identifier__u32 uuid_of__object__u32) {
    // TODO need to do existance check to avoid error printout.

    // TODO assumption of concrete position type is unsafe
    Vector__3i32F4 position_of__hitbox__3i32F4;
    bool success = 
        opaque_access_to__hitbox(
            get_p_hitbox_context_from__game(p_game), 
            GET_UUID_P(get_p_world_from__game(p_game)), 
            uuid_of__object__u32, 
            &position_of__hitbox__3i32F4, 
            0, 
            0, 
            0, 
            0,
            0,
            OPAQUE_ACCESS__HITBOX__IS_GETTING);

    if (!success) {
        // short circuit
        debug_warning("f_object_handler__hitbox__pre_teleport, success == false, uuid:%d remains activated", uuid_of__object__u32);
        return;
    }

    Global_Space *p_global_space =
        get_p_global_space_from__global_space_manager(
                get_p_global_space_manager_from__game(p_game), 
                vector_3i32F4_to__chunk_vector_3i32(
                    position_of__hitbox__3i32F4));

    if (!p_global_space) {
        // short circuit
        debug_warning("f_object_handler__hitbox__pre_teleport, p_global_space == 0, uuid:%d remains activated", uuid_of__object__u32);
        return;
    }

    debug_info__verbose("f_object_handler__hitbox__post_teleport, f_object_handler__hitbox__post_teleport, uuid:%d deactivated", uuid_of__object__u32);
    f_object_handler__hitbox__deactivate(
            p_game, 
            uuid_of__object__u32);

    remove_entry_from__collision_node(
            get_p_collision_node_pool_from__world(
                get_p_world_from__game(p_game)), 
            get_p_collision_node_from__global_space(p_global_space), 
            uuid_of__object__u32);
}

void f_object_handler__hitbox__post_teleport(
        Game *p_game,
        Identifier__u32 uuid_of__object__u32) {
    // TODO need to do existance check to avoid error printout.

    // TODO assumption of concrete position type is unsafe
    Vector__3i32F4 position_of__hitbox__3i32F4;
    bool success = 
        opaque_access_to__hitbox(
            get_p_hitbox_context_from__game(p_game), 
            GET_UUID_P(get_p_world_from__game(p_game)), 
            uuid_of__object__u32, 
            &position_of__hitbox__3i32F4, 
            0, 
            0, 
            0, 
            0,
            0,
            OPAQUE_ACCESS__HITBOX__IS_GETTING);

    if (!success) {
        // short circuit
        debug_warning("f_object_handler__hitbox__post_teleport, success == false, uuid:%d remains deactivated", uuid_of__object__u32);
        return;
    }

    Global_Space *p_global_space =
        get_p_global_space_from__global_space_manager(
                get_p_global_space_manager_from__game(p_game), 
                vector_3i32F4_to__chunk_vector_3i32(
                    position_of__hitbox__3i32F4));

    if (!p_global_space) {
        // short circuit
        debug_warning("f_object_handler__hitbox__post_teleport, p_global_space == 0, uuid:%d remains deactivated", uuid_of__object__u32);
        return;
    }

    debug_info__verbose("f_object_handler__hitbox__post_teleport, f_object_handler__hitbox__post_teleport, uuid:%d activated", uuid_of__object__u32);
    f_object_handler__hitbox__activate(
            p_game, 
            uuid_of__object__u32);

    add_entry_to__collision_node(
            get_p_collision_node_pool_from__world(
                get_p_world_from__game(p_game)), 
            get_p_collision_node_from__global_space(p_global_space), 
            uuid_of__object__u32);
}
