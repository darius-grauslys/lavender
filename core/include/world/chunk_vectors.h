#ifndef CHUNK_VECTORS_H
#define CHUNK_VECTORS_H

#include "numerics.h"
#include "platform_defaults.h"
#include "platform_defines.h"
#include <defines.h>
#include <vectors.h>

static inline
i32 normalize_xyz_i32_to__chunk_xyz_i32(
        i32 tile_xyz__i32) {
    return ARITHMETRIC_R_SHIFT(
            tile_xyz__i32, 
            LOCAL_SPACE__WIDTH_AND__HEIGHT_IN__PIXELS__BIT_SHIFT);
}

static inline
i32 normalize_xyz_tile_i32_to__chunk_xyz_i32(
        i32 tile_xyz__i32) {
    return ARITHMETRIC_R_SHIFT(
            tile_xyz__i32, 
            LOCAL_SPACE__WIDTH_AND__HEIGHT_IN__TILES__BIT_SHIFT);
}

static inline
i32 get_chunk_x_i32_from__tile_vector_3i32(
        Tile_Vector__3i32 tile_vector__3i32) {
    return normalize_xyz_tile_i32_to__chunk_xyz_i32(
            tile_vector__3i32.x__i32);
}

static inline
i32 get_chunk_y_i32_from__tile_vector_3i32(
        Tile_Vector__3i32 tile_vector__3i32) {
    return normalize_xyz_tile_i32_to__chunk_xyz_i32(
            tile_vector__3i32.y__i32);
}

static inline
i32 get_chunk_z_i32_from__tile_vector_3i32(
        Tile_Vector__3i32 tile_vector__3i32) {
    return normalize_xyz_tile_i32_to__chunk_xyz_i32(
            tile_vector__3i32.z__i32);
}

static inline
i32 normalize_xyz_i32F4_to__chunk_xyz_i32(i32F4 xyz__i32F4) {
    return normalize_xyz_i32_to__chunk_xyz_i32(
            i32F4_to__i32(xyz__i32F4));
}

static Signed_Index__i32 inline get_chunk_x_i32_from__vector_3i32F4(
        Vector__3i32F4 vector__3i32F4) {
    return 
        normalize_xyz_i32F4_to__chunk_xyz_i32(
            get_x_i32F4_from__vector_3i32F4(vector__3i32F4));
}

static Signed_Index__i32 inline get_chunk_y_i32_from__vector_3i32F4(
        Vector__3i32F4 vector__3i32F4) {
    return 
        normalize_xyz_i32F4_to__chunk_xyz_i32(
            get_y_i32F4_from__vector_3i32F4(vector__3i32F4));
}

static Signed_Index__i32 inline get_chunk_z_i32_from__vector_3i32F4(
        Vector__3i32F4 vector__3i32F4) {
    return 
        normalize_xyz_i32F4_to__chunk_xyz_i32(
            get_z_i32F4_from__vector_3i32F4(vector__3i32F4));
}

static Chunk_Vector__3i32 inline get_chunk_vector__3i32(
        Signed_Index__i32 x,
        Signed_Index__i32 y,
        Signed_Index__i32 z) {
    return (Vector__3i32) {
        x, 
        y, 
        z
    };
}

static Chunk_Vector__3i32 inline get_chunk_vector__3i32_with__i32F4(
        i32F4 x,
        i32F4 y,
        i32F4 z) {
    return (Chunk_Vector__3i32) {
        normalize_xyz_i32F4_to__chunk_xyz_i32(x),
        normalize_xyz_i32F4_to__chunk_xyz_i32(y),
        normalize_xyz_i32F4_to__chunk_xyz_i32(z)
    };
}

static inline 
Chunk_Vector__3i32 tile_vector_3i32_to__chunk_vector_3i32(
        Tile_Vector__3i32 vector) {
    return (Tile_Vector__3i32) {
        get_chunk_x_i32_from__tile_vector_3i32(vector),
        get_chunk_y_i32_from__tile_vector_3i32(vector),
        get_chunk_z_i32_from__tile_vector_3i32(vector)
            + (vector.z__i32 < 0 ? -1 : 0)
    };
}

static inline 
Chunk_Vector__3i32 vector_3i32F4_to__chunk_vector_3i32(
        Vector__3i32F4 vector) {
    return (Tile_Vector__3i32) {
        get_chunk_x_i32_from__vector_3i32F4(vector),
        get_chunk_y_i32_from__vector_3i32F4(vector),
        get_chunk_z_i32_from__vector_3i32F4(vector)
            + (vector.z__i32F4 < 0 ? -1 : 0)
    };
}

static Chunk_Vector__3i32 inline vector_3i32_to__chunk_vector_3i32(
        Vector__3i32 vector) {
    return (Chunk_Vector__3i32) {
        normalize_xyz_i32_to__chunk_xyz_i32(vector.x__i32),
        normalize_xyz_i32_to__chunk_xyz_i32(vector.y__i32),
        normalize_xyz_i32_to__chunk_xyz_i32(vector.z__i32)
            + (vector.z__i32 < 0 ? -1 : 0)
    };
}

static inline 
Chunk_Vector__3i32 chunk_vector_3i32_to__tile_vector_3i32(
        Chunk_Vector__3i32 chunk_vector) {
    return (Tile_Vector__3i32) {
        ARITHMETRIC_L_SHIFT(
                chunk_vector.x__i32,
                LOCAL_SPACE__WIDTH_AND__HEIGHT_IN__PIXELS__BIT_SHIFT
                - TILE__WIDTH_AND__HEIGHT__BIT_SHIFT),
        ARITHMETRIC_L_SHIFT(
                chunk_vector.y__i32,
                LOCAL_SPACE__WIDTH_AND__HEIGHT_IN__PIXELS__BIT_SHIFT
                - TILE__WIDTH_AND__HEIGHT__BIT_SHIFT),
        ARITHMETRIC_L_SHIFT(
                chunk_vector.z__i32,
                LOCAL_SPACE__WIDTH_AND__HEIGHT_IN__PIXELS__BIT_SHIFT
                - TILE__WIDTH_AND__HEIGHT__BIT_SHIFT),
    };
}

static Vector__3i32 inline chunk_vector_3i32_to__vector_3i32(
        Chunk_Vector__3i32 chunk_vector) {
    return (Vector__3i32) {
        ARITHMETRIC_L_SHIFT(
                chunk_vector.x__i32,
                LOCAL_SPACE__WIDTH_AND__HEIGHT_IN__PIXELS__BIT_SHIFT),
        ARITHMETRIC_L_SHIFT(
                chunk_vector.y__i32,
                LOCAL_SPACE__WIDTH_AND__HEIGHT_IN__PIXELS__BIT_SHIFT),
        ARITHMETRIC_L_SHIFT(
                chunk_vector.z__i32,
                LOCAL_SPACE__WIDTH_AND__HEIGHT_IN__PIXELS__BIT_SHIFT),
    };
}

static Vector__3i32F4 inline chunk_vector_3i32_to__vector_3i32F4(
        Chunk_Vector__3i32 chunk_vector) {
    return vector_3i32_to__vector_3i32F4(
            chunk_vector_3i32_to__vector_3i32(chunk_vector));
}

#endif
