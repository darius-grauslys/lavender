#ifndef TILE_VECTORS_H
#define TILE_VECTORS_H

#include "defines_weak.h"
#include "numerics.h"
#include "platform_defaults.h"
#include "platform_defines.h"
#include "world/chunk_vectors.h"
#include <defines.h>
#include <vectors.h>

static inline
i32 normalize_xyz_i32_to__tile_xyz_i32(i32 xyz__i32) {
    return xyz__i32 >> TILE__WIDTH_AND__HEIGHT__BIT_SHIFT;
}

static inline
i32 normalize_xyz_i32F4_to__tile_xyz_i32(i32F4 xyz__i32F4) {
    return normalize_xyz_i32_to__tile_xyz_i32(
            i32F4_to__i32(xyz__i32F4));
}

static inline
i32 normalize_xyz_i32F20_to__tile_xyz_i32(i32F20 xyz__i32F20) {
    return normalize_xyz_i32_to__tile_xyz_i32(
            i32F20_to__i32(xyz__i32F20));
}

static Index__u8 inline normalize_i32__to_tile_u8(
        Signed_Index__i32 x) {
    return 
        ARITHMETRIC_MASK(
                ARITHMETRIC_R_SHIFT(x, 
                        TILE__WIDTH_AND__HEIGHT__BIT_SHIFT)
                - (x < 0),
                MASK(CHUNK__WIDTH_AND__HEIGHT__BIT_SHIFT));
}

static Index__u8 inline normalize_i32F4__to_tile_u8(
        i32F4 x) {
    return normalize_i32__to_tile_u8(
            i32F4_to__i32(x)
            - (x < 0 && -x <= BIT(FRACTIONAL_PERCISION_4__BIT_SIZE)));
}

static Index__u8 inline get_tile_x_u8_from__vector_3i32F4(
        Vector__3i32F4 vector__3i32F4) {
    return 
        normalize_i32F4__to_tile_u8(
                get_x_i32F4_from__vector_3i32F4(vector__3i32F4));
}

static Index__u8 inline get_tile_y_u8_from__vector_3i32F4(
        Vector__3i32F4 vector__3i32F4) {
    return 
        normalize_i32F4__to_tile_u8(
                get_y_i32F4_from__vector_3i32F4(vector__3i32F4));
}

static Index__u8 inline get_tile_z_u8_from__vector_3i32F4(
        Vector__3i32F4 vector__3i32F4) {
    return 
        normalize_i32F4__to_tile_u8(
                get_z_i32F4_from__vector_3i32F4(vector__3i32F4));
}

///
/// X, Y, and Z are tile indices.
///
static inline 
Tile_Vector__3i32 get_tile_vector(
        Signed_Index__i32 x,
        Signed_Index__i32 y,
        Signed_Index__i32 z) {
    return (Vector__3i32) {
        x,
        y,
        z
    };
}

static inline
Tile_Vector__3i32 get_tile_vector_using__i32F4(
        i32F4 x,
        i32F4 y,
        i32F4 z) {
    return (Tile_Vector__3i32) {
        normalize_xyz_i32F4_to__tile_xyz_i32(x),
        normalize_xyz_i32F4_to__tile_xyz_i32(y),
        normalize_xyz_i32F4_to__tile_xyz_i32(z),
    };
}

static inline
Tile_Vector__3i32 get_tile_vector_using__3i32F4(
        Vector__3i32F4 position__3i32F4) {
    return get_tile_vector_using__i32F4(
            position__3i32F4.x__i32F4,
            position__3i32F4.y__i32F4,
            position__3i32F4.z__i32F4
            );
}

static inline
Tile_Vector__3i32 vector_3i32_to__tile_vector(
        Vector__3i32F4 vector) {
    return (Tile_Vector__3i32) {
        normalize_xyz_i32_to__tile_xyz_i32(vector.x__i32F4),
        normalize_xyz_i32_to__tile_xyz_i32(vector.y__i32F4),
        normalize_xyz_i32_to__tile_xyz_i32(vector.z__i32F4)
    };
}

static inline
Tile_Vector__3i32 vector_3i32F4_to__tile_vector(
        Vector__3i32F4 vector) {
    return (Tile_Vector__3i32) {
        normalize_xyz_i32F4_to__tile_xyz_i32(vector.x__i32F4),
        normalize_xyz_i32F4_to__tile_xyz_i32(vector.y__i32F4),
        normalize_xyz_i32F4_to__tile_xyz_i32(vector.z__i32F4)
    };
}

static inline
Tile_Vector__3i32 vector_3i32F20_to__tile_vector(
        Vector__3i32F20 vector) {
    return (Tile_Vector__3i32) {
        normalize_xyz_i32F20_to__tile_xyz_i32(vector.x__i32F20),
        normalize_xyz_i32F20_to__tile_xyz_i32(vector.y__i32F20),
        normalize_xyz_i32F20_to__tile_xyz_i32(vector.z__i32F20)
    };
}

static inline
Tile_Vector__3i32 get_ray_endpoint_as__tile_vector(
        Ray__3i32F20 *p_ray) {
    return vector_3i32F20_to__tile_vector(
            p_ray->ray_current_vector__3i32F20);
}

static inline
Vector__3i32 tile_vector_3i32_to__vector_3i32(
        Tile_Vector__3i32 tile_vector__3i32) {
    return get_vector__3i32(
            tile_vector__3i32.x__i32
            << TILE__WIDTH_AND__HEIGHT__BIT_SHIFT,
            tile_vector__3i32.y__i32
            << TILE__WIDTH_AND__HEIGHT__BIT_SHIFT,
            tile_vector__3i32.z__i32
            << TILE__WIDTH_AND__HEIGHT__BIT_SHIFT);
}

static inline
Vector__3i32F4 tile_vector_3i32_to__vector_3i32F4(
        Tile_Vector__3i32 tile_vector__3i32) {
    return get_vector__3i32F4_using__i32(
            (tile_vector__3i32.x__i32
            << TILE__WIDTH_AND__HEIGHT__BIT_SHIFT),
            (tile_vector__3i32.y__i32
            << TILE__WIDTH_AND__HEIGHT__BIT_SHIFT),
            (tile_vector__3i32.z__i32
            << TILE__WIDTH_AND__HEIGHT__BIT_SHIFT));
}

///
/// Returns a Vector__3u8 with x,y,z fit for indexing tiles
///
static inline 
Local_Tile_Vector__3u8 tile_vector_3i32_to__local_tile_vector_3u8(
        Tile_Vector__3i32 tile_vector__3i32) {
    return get_vector__3u8(
            ARITHMETRIC_MASK(tile_vector__3i32.x__i32, MASK(TILE__WIDTH_AND__HEIGHT__BIT_SHIFT)),
            ARITHMETRIC_MASK(tile_vector__3i32.y__i32, MASK(TILE__WIDTH_AND__HEIGHT__BIT_SHIFT)),
            ARITHMETRIC_MASK(tile_vector__3i32.z__i32, MASK(TILE__WIDTH_AND__HEIGHT__BIT_SHIFT))
            );
}

static inline 
Local_Tile_Vector__3u8 vector_3i32F4_to__local_tile_vector_3u8(
        Vector__3i32F4 vector__3i32F4) {
    return (Local_Tile_Vector__3u8){
        get_tile_x_u8_from__vector_3i32F4(vector__3i32F4),
        get_tile_y_u8_from__vector_3i32F4(vector__3i32F4),
        get_tile_z_u8_from__vector_3i32F4(vector__3i32F4)
    };
}

#endif
