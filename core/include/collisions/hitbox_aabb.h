#ifndef HITBOX_AABB_H
#define HITBOX_AABB_H

#include "defines_weak.h"
#include <defines.h>
#include <vectors.h>
#include <world/chunk_vectors.h>

Direction__u8 is_hitbox__colliding(
        Hitbox_AABB *hitbox__checking,
        Hitbox_AABB *hitbox__other);

void get_aa_bb_as__vectors_3i32F4_from__hitbox(
        Hitbox_AABB *hitbox,
        Vector__3i32F4 *aa,
        Vector__3i32F4 *bb);

void get_aa_bb_as__vectors_3i32_from__hitbox(
        Hitbox_AABB *hitbox,
        Vector__3i32 *aa,
        Vector__3i32 *bb);

/// If the hitbox resides in an entity which is
/// registered to the collision system, DO NOT invoke this.
/// Instead invoke using game_action.h .
///
void set_hitbox__position_with__3i32F4(
        Hitbox_AABB *hitbox,
        Vector__3i32F4 position__3i32F4);

/// If the hitbox resides in an entity which is
/// registered to the collision system, DO NOT invoke this.
/// Instead invoke using game_action.h .
///
void set_hitbox__position_with__3i32(
        Hitbox_AABB *hitbox,
        Vector__3i32 position__3i32);

Direction__u8 get_movement_direction_of__hitbox(
        Hitbox_AABB *hitbox);

Direction__u8 get_tile_transition_direction_of__hitbox(
        Hitbox_AABB *hitbox,
        Vector__3i32F4 *aa,
        Vector__3i32F4 *bb);

void initialize_vector_3i32F4_as__aa_bb_without__velocity(
        Vector__3i32F4 *hitbox_point,
        Hitbox_AABB *hitbox,
        Direction__u8 corner_direction);

void initialize_vector_3i32F4_as__aa_bb(
        Vector__3i32F4 *hitbox_point,
        Hitbox_AABB *hitbox,
        Direction__u8 corner_direction);

void initialize_vector_3i32_as__aa_bb_without__velocity(
        Vector__3i32 *hitbox_point,
        Hitbox_AABB *hitbox,
        Direction__u8 corner_direction);

void initialize_vector_3i32_as__aa_bb(
        Vector__3i32 *hitbox_point,
        Hitbox_AABB *hitbox,
        Direction__u8 corner_direction);

void clamp_p_vector_3i32_to__hitbox(
        Hitbox_AABB *p_hitbox, 
        Vector__3i32 *p_position__3i32);

void initialize_hitbox(Hitbox_AABB *hitbox);

void initialize_hitbox_as__allocated(
        Hitbox_AABB *hitbox,
        Identifier__u32 uuid__u32,
        Quantity__u32 width, 
        Quantity__u32 height,
        Vector__3i32F4 position__3i32F4);

///
/// NOTE: Only checks the corners of hitbox__one
/// against hitbox__two. In otherwords, if hitbox__two
/// is fully within hitbox__one, this will return
/// DIRECTION__NONE.
///
Direction__u8 is_this_hitbox__overlapping_this_hitbox(
        Hitbox_AABB *hitbox__one,
        Hitbox_AABB *hitbox__two);

bool is_vector_3i32F4_inside__hitbox(
        Vector__3i32F4 vector,
        Hitbox_AABB *p_hitbox);

bool is_vector_3i32_inside__hitbox(
        Vector__3i32 vector,
        Hitbox_AABB *p_hitbox);

bool is_this_hitbox__fully_inside_this_hitbox__without_velocity(
        Hitbox_AABB *hitbox__one,
        Hitbox_AABB *hitbox__two);

static inline
Vector__3i32F4 get_position_3i32F4_of__hitbox_aabb(
        Hitbox_AABB *p_hitbox_aabb) {
#ifndef NDEBUG
    if (!p_hitbox_aabb) {
        debug_error("get_position_3i32F4_of__hitbox_aabb, p_hitbox_aabb == 0.");
        return VECTOR__3i32F4__OUT_OF_BOUNDS;
    }
#endif
    return p_hitbox_aabb->position__3i32F4;
}

static inline
Vector__3i32 get_position_3i32_of__hitbox_aabb(
        Hitbox_AABB *p_hitbox_aabb) {
#ifndef NDEBUG
    if (!p_hitbox_aabb) {
        debug_error("get_position_3i32_of__hitbox_aabb, p_hitbox_aabb == 0.");
        return VECTOR__3i32__OUT_OF_BOUNDS;
    }
#endif
    return 
        vector_3i32F4_to__vector_3i32(
                p_hitbox_aabb->position__3i32F4);
}

static inline
Vector__3i32F4 get_velocity_3i32F4_of__hitbox_aabb(
        Hitbox_AABB *p_hitbox_aabb) {
#ifndef NDEBUG
    if (!p_hitbox_aabb) {
        debug_error("get_velocity_3i32F4_of__hitbox_aabb, p_hitbox_aabb == 0.");
        return VECTOR__3i32F4__0_0_0;
    }
#endif
    return p_hitbox_aabb->velocity__3i32F4;
}

static inline
Vector__3i16F8 get_acceleration_3i16F8_of__hitbox_aabb(
        Hitbox_AABB *p_hitbox_aabb) {
#ifndef NDEBUG
    if (!p_hitbox_aabb) {
        debug_error("get_acceleration_3i16F8_of__hitbox_aabb, p_hitbox_aabb == 0.");
        return VECTOR__3i16F8__0_0_0;
    }
#endif
    return p_hitbox_aabb->acceleration__3i16F8;
}

static inline
Quantity__u32 get_width_u32_of__hitbox_aabb(
        Hitbox_AABB *p_hitbox_aabb) {
#ifndef NDEBUG
    if (!p_hitbox_aabb) {
        debug_error("get_width_u32_of__hitbox_aabb, p_hitbox_aabb == 0.");
        return 0;
    }
#endif
    return p_hitbox_aabb->width__quantity_u32;
}

static inline
Quantity__u32 get_height_u32_of__hitbox_aabb(
        Hitbox_AABB *p_hitbox_aabb) {
#ifndef NDEBUG
    if (!p_hitbox_aabb) {
        debug_error("get_height_u32_of__hitbox_aabb, p_hitbox_aabb == 0.");
        return 0;
    }
#endif
    return p_hitbox_aabb->height__quantity_u32;
}

static inline
void set_size_of__hitbox_aabb(
        Hitbox_AABB *p_hitbox_aabb,
        Quantity__u32 width__quantity_u32,
        Quantity__u32 height__quantity_u32) {
#ifndef NDEBUG
    if (!p_hitbox_aabb) {
        debug_error("set_size_of__hitbox_aabb, p_hitbox_aabb == 0.");
        return;
    }
#endif
    p_hitbox_aabb->is_hitbox_aabb__dirty = true;
    p_hitbox_aabb->width__quantity_u32 = width__quantity_u32;
    p_hitbox_aabb->height__quantity_u32 = height__quantity_u32;
}

static inline
void apply_x_velocity_to__hitbox(
        Hitbox_AABB *p_hitbox_aabb,
        i32F4 x__velocity) {
#ifndef NDEBUG
    if (!p_hitbox_aabb) {
        debug_error("apply_x_velocity_to__hitbox, p_hitbox_aabb == 0.");
        return;
    }
#endif
    p_hitbox_aabb->velocity__3i32F4.x__i32F4 += x__velocity;
}

static inline
void apply_y_velocity_to__hitbox(
        Hitbox_AABB *p_hitbox_aabb,
        i32F4 y__velocity) {
#ifndef NDEBUG
    if (!p_hitbox_aabb) {
        debug_error("apply_y_velocity_to__hitbox, p_hitbox_aabb == 0.");
        return;
    }
#endif
    p_hitbox_aabb->velocity__3i32F4.y__i32F4 += y__velocity;
}

static inline
void apply_z_velocity_to__hitbox(
        Hitbox_AABB *p_hitbox_aabb,
        i32F4 z__velocity) {
#ifndef NDEBUG
    if (!p_hitbox_aabb) {
        debug_error("apply_z_velocity_to__hitbox, p_hitbox_aabb == 0.");
        return;
    }
#endif
    p_hitbox_aabb->velocity__3i32F4.z__i32F4 += z__velocity;
}


///
/// TODO: really funny stuff happens when
///       we don't take vector as a pointer.
///       Why?
///
static inline
void apply_velocity_to__hitbox(
        Hitbox_AABB *p_hitbox_aabb,
        Vector__3i32F4 *vector) {
#ifndef NDEBUG
    if (!p_hitbox_aabb) {
        debug_error("apply_velocity_to__hitbox, p_hitbox_aabb == 0.");
        return;
    }
#endif
    apply_x_velocity_to__hitbox(p_hitbox_aabb, vector->x__i32F4);
    apply_y_velocity_to__hitbox(p_hitbox_aabb, vector->y__i32F4);
    apply_z_velocity_to__hitbox(p_hitbox_aabb, vector->z__i32F4);
}

/// TODO: REMOVE, must use dispatch_game_action__hitbox instead
static inline
void set_x_position_to__hitbox(
        Hitbox_AABB *p_hitbox_aabb,
        i32F4 x__position) {
#ifndef NDEBUG
    if (!p_hitbox_aabb) {
        debug_error("set_x_position_to__hitbox, p_hitbox_aabb == 0.");
        return;
    }
#endif
    p_hitbox_aabb->is_hitbox_aabb__dirty = true;
    p_hitbox_aabb->position__3i32F4.x__i32F4 = x__position;
}

/// TODO: REMOVE, must use dispatch_game_action__hitbox instead
static inline
void set_y_position_to__hitbox(
        Hitbox_AABB *p_hitbox_aabb,
        i32F4 y__position) {
#ifndef NDEBUG
    if (!p_hitbox_aabb) {
        debug_error("set_y_position_to__hitbox, p_hitbox_aabb == 0.");
        return;
    }
#endif
    p_hitbox_aabb->is_hitbox_aabb__dirty = true;
    p_hitbox_aabb->position__3i32F4.y__i32F4 = y__position;
}

/// TODO: REMOVE, must use dispatch_game_action__hitbox instead
static inline
void set_z_position_to__hitbox(
        Hitbox_AABB *p_hitbox_aabb,
        i32F4 z__position) {
#ifndef NDEBUG
    if (!p_hitbox_aabb) {
        debug_error("set_z_position_to__hitbox, p_hitbox_aabb == 0.");
        return;
    }
#endif
    p_hitbox_aabb->is_hitbox_aabb__dirty = true;
    p_hitbox_aabb->position__3i32F4.z__i32F4 = z__position;
}

/// TODO: REMOVE, must use dispatch_game_action__hitbox instead
static inline
void offset_x_position_to__hitbox(
        Hitbox_AABB *p_hitbox_aabb,
        i32F4 x__position) {
#ifndef NDEBUG
    if (!p_hitbox_aabb) {
        debug_error("offset_x_position_to__hitbox, p_hitbox_aabb == 0.");
        return;
    }
#endif
    p_hitbox_aabb->is_hitbox_aabb__dirty = true;
    p_hitbox_aabb->position__3i32F4.x__i32F4 += x__position;
}

/// TODO: REMOVE, must use dispatch_game_action__hitbox instead
static inline
void offset_y_position_to__hitbox(
        Hitbox_AABB *p_hitbox_aabb,
        i32F4 y__position) {
#ifndef NDEBUG
    if (!p_hitbox_aabb) {
        debug_error("offset_y_position_to__hitbox, p_hitbox_aabb == 0.");
        return;
    }
#endif
    p_hitbox_aabb->is_hitbox_aabb__dirty = true;
    p_hitbox_aabb->position__3i32F4.y__i32F4 += y__position;
}

/// TODO: REMOVE, must use dispatch_game_action__hitbox instead
static inline
void offset_z_position_to__hitbox(
        Hitbox_AABB *p_hitbox_aabb,
        i32F4 z__position) {
#ifndef NDEBUG
    if (!p_hitbox_aabb) {
        debug_error("offset_z_position_to__hitbox, p_hitbox_aabb == 0.");
        return;
    }
#endif
    p_hitbox_aabb->is_hitbox_aabb__dirty = true;
    p_hitbox_aabb->position__3i32F4.z__i32F4 += z__position;
}

static inline
void set_x_velocity_to__hitbox(
        Hitbox_AABB *p_hitbox_aabb,
        i32F4 x__velocity) {
#ifndef NDEBUG
    if (!p_hitbox_aabb) {
        debug_error("set_x_velocity_to__hitbox, p_hitbox_aabb == 0.");
        return;
    }
#endif
    p_hitbox_aabb->is_hitbox_aabb__dirty = true;
    p_hitbox_aabb->velocity__3i32F4.x__i32F4 = x__velocity;
}

static inline
void set_y_velocity_to__hitbox(
        Hitbox_AABB *p_hitbox_aabb,
        i32F4 y__velocity) {
#ifndef NDEBUG
    if (!p_hitbox_aabb) {
        debug_error("set_y_velocity_to__hitbox, p_hitbox_aabb == 0.");
        return;
    }
#endif
    p_hitbox_aabb->is_hitbox_aabb__dirty = true;
    p_hitbox_aabb->velocity__3i32F4.y__i32F4 = y__velocity;
}

static inline
void set_z_velocity_to__hitbox(
        Hitbox_AABB *p_hitbox_aabb,
        i32F4 z__velocity) {
#ifndef NDEBUG
    if (!p_hitbox_aabb) {
        debug_error("set_z_velocity_to__hitbox, p_hitbox_aabb == 0.");
        return;
    }
#endif
    p_hitbox_aabb->is_hitbox_aabb__dirty = true;
    p_hitbox_aabb->velocity__3i32F4.z__i32F4 = z__velocity;
}

static inline
void set_x_acceleration_to__hitbox(
        Hitbox_AABB *p_hitbox_aabb,
        i16F8 x__acceleration) {
#ifndef NDEBUG
    if (!p_hitbox_aabb) {
        debug_error("set_x_acceleration_to__hitbox, p_hitbox_aabb == 0.");
        return;
    }
#endif
    p_hitbox_aabb->is_hitbox_aabb__dirty = true;
    p_hitbox_aabb->acceleration__3i16F8.x__i16F8 = x__acceleration;
}

static inline
void set_y_acceleration_to__hitbox(
        Hitbox_AABB *p_hitbox_aabb,
        i16F8 y__acceleration) {
#ifndef NDEBUG
    if (!p_hitbox_aabb) {
        debug_error("set_y_acceleration_to__hitbox, p_hitbox_aabb == 0.");
        return;
    }
#endif
    p_hitbox_aabb->is_hitbox_aabb__dirty = true;
    p_hitbox_aabb->acceleration__3i16F8.y__i16F8 = y__acceleration;
}

static inline
void set_z_acceleration_to__hitbox(
        Hitbox_AABB *p_hitbox_aabb,
        i16F8 z__acceleration) {
#ifndef NDEBUG
    if (!p_hitbox_aabb) {
        debug_error("set_z_acceleration_to__hitbox, p_hitbox_aabb == 0.");
        return;
    }
#endif
    p_hitbox_aabb->is_hitbox_aabb__dirty = true;
    p_hitbox_aabb->acceleration__3i16F8.z__i16F8 = z__acceleration;
}

static inline
void set_velocity_to__hitbox(
        Hitbox_AABB *p_hitbox_aabb,
        Vector__3i32F4 velocity) {
#ifndef NDEBUG
    if (!p_hitbox_aabb) {
        debug_error("set_velocity_to__hitbox, p_hitbox_aabb == 0.");
        return;
    }
#endif
    p_hitbox_aabb->is_hitbox_aabb__dirty = true;
    set_x_velocity_to__hitbox(p_hitbox_aabb, velocity.x__i32F4);
    set_y_velocity_to__hitbox(p_hitbox_aabb, velocity.y__i32F4);
    set_z_velocity_to__hitbox(p_hitbox_aabb, velocity.z__i32F4);
}

static inline
void set_acceleration_to__hitbox(
        Hitbox_AABB *p_hitbox_aabb,
        Vector__3i16F8 acceleration) {
#ifndef NDEBUG
    if (!p_hitbox_aabb) {
        debug_error("set_acceleration_to__hitbox, p_hitbox_aabb == 0.");
        return;
    }
#endif
    p_hitbox_aabb->is_hitbox_aabb__dirty = true;
    set_x_acceleration_to__hitbox(p_hitbox_aabb, acceleration.x__i16F8);
    set_y_acceleration_to__hitbox(p_hitbox_aabb, acceleration.y__i16F8);
    set_z_acceleration_to__hitbox(p_hitbox_aabb, acceleration.z__i16F8);
}

static inline
i32F4 get_x_i32F4_from__hitbox(
        Hitbox_AABB *p_hitbox) {
#ifndef NDEBUG
    if (!p_hitbox) {
        debug_error("get_x_i32F4_from__hitbox, p_hitbox == 0.");
        return 0;
    }
#endif
    return get_x_i32F4_from__vector_3i32F4(get_position_3i32F4_of__hitbox_aabb(p_hitbox));
}

static inline
i32F4 get_y_i32F4_from__hitbox(
        Hitbox_AABB *p_hitbox) {
#ifndef NDEBUG
    if (!p_hitbox) {
        debug_error("get_y_i32F4_from__hitbox, p_hitbox == 0.");
        return 0;
    }
#endif
    return get_y_i32F4_from__vector_3i32F4(get_position_3i32F4_of__hitbox_aabb(p_hitbox));
}

static inline
i32F4 get_z_i32F4_from__hitbox(
        Hitbox_AABB *p_hitbox) {
#ifndef NDEBUG
    if (!p_hitbox) {
        debug_error("get_z_i32F4_from__hitbox, p_hitbox == 0.");
        return 0;
    }
#endif
    return get_z_i32F4_from__vector_3i32F4(get_position_3i32F4_of__hitbox_aabb(p_hitbox));
}

static inline
Signed_Index__i32 get_x_i32_from__hitbox(
        Hitbox_AABB *p_hitbox) {
#ifndef NDEBUG
    if (!p_hitbox) {
        debug_error("get_x_i32_from__hitbox, p_hitbox == 0.");
        return 0;
    }
#endif
    return get_x_i32_from__vector_3i32F4(get_position_3i32F4_of__hitbox_aabb(p_hitbox));
}

static inline
Signed_Index__i32 get_y_i32_from__hitbox(
        Hitbox_AABB *p_hitbox) {
#ifndef NDEBUG
    if (!p_hitbox) {
        debug_error("get_y_i32_from__hitbox, p_hitbox == 0.");
        return 0;
    }
#endif
    return get_y_i32_from__vector_3i32F4(get_position_3i32F4_of__hitbox_aabb(p_hitbox));
}

static inline
Signed_Index__i32 get_z_i32_from__hitbox(
        Hitbox_AABB *p_hitbox) {
#ifndef NDEBUG
    if (!p_hitbox) {
        debug_error("get_z_i32_from__hitbox, p_hitbox == 0.");
        return 0;
    }
#endif
    return get_z_i32_from__vector_3i32F4(get_position_3i32F4_of__hitbox_aabb(p_hitbox));
}

static inline
Signed_Index__i32 get_chunk_x_i32_from__hitbox(
        Hitbox_AABB *p_hitbox) {
#ifndef NDEBUG
    if (!p_hitbox) {
        debug_error("get_chunk_x_i32_from__hitbox, p_hitbox == 0.");
        return 0;
    }
#endif
    return get_chunk_x_i32_from__vector_3i32F4(
            get_position_3i32F4_of__hitbox_aabb(p_hitbox));
}

static inline
Signed_Index__i32 get_chunk_y_i32_from__hitbox(
        Hitbox_AABB *p_hitbox) {
#ifndef NDEBUG
    if (!p_hitbox) {
        debug_error("get_chunk_y_i32_from__hitbox, p_hitbox == 0.");
        return 0;
    }
#endif
    return get_chunk_y_i32_from__vector_3i32F4(
            get_position_3i32F4_of__hitbox_aabb(p_hitbox));
}

static inline
Signed_Index__i32 get_chunk_z_i32_from__hitbox(
        Hitbox_AABB *p_hitbox) {
#ifndef NDEBUG
    if (!p_hitbox) {
        debug_error("get_chunk_z_i32_from__hitbox, p_hitbox == 0.");
        return 0;
    }
#endif
    return get_chunk_z_i32_from__vector_3i32F4(
            get_position_3i32F4_of__hitbox_aabb(p_hitbox));
}

#endif
