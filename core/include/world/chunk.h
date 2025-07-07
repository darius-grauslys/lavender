#ifndef CHUNK_H
#define CHUNK_H

#include <defines.h>
#include "numerics.h"
#include "platform_defines.h"
#include "tile.h"
#include "vectors.h"

void initialize_chunk(
        Chunk *p_chunk,
        Identifier__u64 uuid__u64);

void m_process__serialize_chunk(
        Process *p_this_process,
        Game *p_game);

void m_process__deserialize_chunk(
        Process *p_this_process,
        Game *p_game);

static inline
Identifier__u64 get_uuid__chunk(
        Chunk *p_chunk) {
    return p_chunk->_serialization_header.uuid;
}

///
/// x, y, and z are local to the chunk.
/// Implementation should store tiles sequentially in memory.
/// So, x=0, y=0, z=0 gets us the first tile in memory.
///
static inline 
void set_tile_of__chunk(
        Chunk* chunk, 
        Local_Tile_Vector__3u8 local_tile_vector,
        Tile* tile) {
    //TODO: we need debug stuffs.
    int32_t index = 
        (local_tile_vector.y__u8 << CHUNK__WIDTH_AND__HEIGHT__BIT_SHIFT)
        + (local_tile_vector.z__u8 << (CHUNK__WIDTH_AND__HEIGHT__BIT_SHIFT*2)) 
        + local_tile_vector.x__u8;

    chunk->tiles[index] = *tile;
}

static inline 
Tile* get_p_tile_from__chunk(
        Chunk *chunk, 
        Local_Tile_Vector__3u8 local_tile_vector) {
#ifndef NDEBUG
    if (local_tile_vector.x__u8 >= CHUNK__WIDTH) {
        debug_error("get_p_tile_from__chunk, x out of bounds.");
        return 0;
    }
    if (local_tile_vector.y__u8 >= CHUNK__WIDTH) {
        debug_error("get_p_tile_from__chunk, y out of bounds.");
        return 0;
    }
    if (local_tile_vector.z__u8 >= CHUNK__WIDTH) {
        debug_error("get_p_tile_from__chunk, z out of bounds.");
        return 0;
    }
#endif
    // TODO: improve
    // int32_t index = (1 << (z * CHUNK__DEPTH_BIT_SHIFT)) +
    //     ((CHUNK_WIDTH__IN_TILES - y) << CHUNK__HEIGHT_BIT_SHIFT) + x;
    // Index__u8 index__u8 = 
    //     local_tile_vector.x__u8
    //     + (7 - local_tile_vector.y__u8) 
    //     * 8;
    Index__u16 index__u16 = 
        local_tile_vector.x__u8
        + (((CHUNK__HEIGHT-1)
                - local_tile_vector.y__u8)
            * CHUNK__WIDTH)
        + (CHUNK__WIDTH*CHUNK__HEIGHT
                * local_tile_vector.z__u8)
        ;

    return &chunk->tiles[index__u16];
}

static inline
Tile *try_get_p_tile_from__chunk(
        Chunk *chunk, 
        Local_Tile_Vector__3u8 local_tile_vector) {
    if (local_tile_vector.x__u8 >= CHUNK__WIDTH) {
        return 0;
    }
    if (local_tile_vector.y__u8 >= CHUNK__WIDTH) {
        return 0;
    }
    if (local_tile_vector.z__u8 >= CHUNK__WIDTH) {
        return 0;
    }
    return get_p_tile_from__chunk(
            chunk, 
            local_tile_vector);
}

static inline
Tile *get_p_tile_from__chunk_neighborhood(
        Chunk *p_chunk, 
        Chunk *ptr_array_of__chunks[8],
        i8 x__local__i8,
        i8 y__local__i8,
        u8 z__local__u8) {
    if (z__local__u8 >= CHUNK__DEPTH) 
        return 0;
    if (y__local__i8 < 0) {
        if (x__local__i8 < 0) {
            p_chunk = ptr_array_of__chunks[0];
        } else if (x__local__i8 >= (i8)CHUNK__WIDTH) {
            p_chunk = ptr_array_of__chunks[2];
        } else {
            p_chunk = ptr_array_of__chunks[1];
        }
    } else if (y__local__i8 >= (i8)CHUNK__HEIGHT) {
        if (x__local__i8 < 0) {
            p_chunk = ptr_array_of__chunks[5];
        } else if (x__local__i8 >= (i8)CHUNK__WIDTH) {
            p_chunk = ptr_array_of__chunks[7];
        } else {
            p_chunk = ptr_array_of__chunks[6];
        }
    } else if (x__local__i8 >= (i8)CHUNK__WIDTH) {
        p_chunk = ptr_array_of__chunks[4];
    } else if (x__local__i8 < 0) {
        p_chunk = ptr_array_of__chunks[3];
    }

    if (!p_chunk)
        return 0;

    return get_p_tile_from__chunk(
            p_chunk, (Local_Tile_Vector__3u8){
                mod__i8_into__u8(x__local__i8, CHUNK__WIDTH),
                mod__i8_into__u8(y__local__i8, CHUNK__HEIGHT),
                z__local__u8
            });
}

static inline 
Tile* get_p_tile_from__chunk_using__u8(
        Chunk *chunk, 
        Index__u8 x__local__u8,
        Index__u8 y__local__u8,
        Index__u8 z__local__u8) {
    Index__u16 index__u16 =
        (x__local__u8
         + ((CHUNK__HEIGHT - 1 - y__local__u8)
             * CHUNK__WIDTH)
         + ((CHUNK__HEIGHT * CHUNK__DEPTH * z__local__u8)));

    return &chunk->tiles[index__u16];
}

///
/// Becareful calling this, make sure
/// you're not carelessly dropping a
/// CHUNK_FLAG__IS_UPDATED.
///
static inline
void clear_chunk_flags(Chunk *p_chunk) {
    p_chunk->chunk_flags = CHUNK_FLAGS__NONE;
}

static inline
void set_chunk_as__awaiting_serialization(Chunk *p_chunk) {
    p_chunk->chunk_flags &= 
        ~(CHUNK_FLAG__IS_AWAITING_DESERIALIZATION
                | CHUNK_FLAG__IS_ACTIVE);
    p_chunk->chunk_flags |= 
        CHUNK_FLAG__IS_AWAITING_SERIALIZATION;
}

static inline
void set_chunk_as__awaiting_deserialization(Chunk *p_chunk) {
    p_chunk->chunk_flags &= 
        ~(CHUNK_FLAG__IS_AWAITING_SERIALIZATION
                | CHUNK_FLAG__IS_ACTIVE);
    p_chunk->chunk_flags |= 
        CHUNK_FLAG__IS_AWAITING_DESERIALIZATION;
}

static inline
void set_chunk_as__active(Chunk *p_chunk) {
    p_chunk->chunk_flags &= 
        ~(CHUNK_FLAG__IS_AWAITING_SERIALIZATION
                | CHUNK_FLAG__IS_AWAITING_DESERIALIZATION);
    p_chunk->chunk_flags |= CHUNK_FLAG__IS_ACTIVE;
}

static inline
void set_chunk_as__inactive(Chunk *p_chunk) {
    p_chunk->chunk_flags &= ~CHUNK_FLAG__IS_ACTIVE;
}

///
/// Once set as updated, it will not be set as
/// not updated!
///
/// Use this if a tile is CHANGED, but not animated.
///
/// This flag lets the chunk serializer know if
/// it needs to be serialized.
///
static inline
void set_chunk_as__updated(Chunk *p_chunk) {
    p_chunk->chunk_flags |= CHUNK_FLAG__IS_UPDATED;
}

///
/// Use this if a tile is animated, or changed.
/// If a tile is changed, be sure to call set_chunk_as__updated
/// as well.
///
static inline
void set_chunk_as__visually_updated(Chunk *p_chunk) {
    p_chunk->chunk_flags |= CHUNK_FLAG__IS_VISUALLY_UPDATED;
}

static inline
void set_chunk_as__visually_committed(Chunk *p_chunk) {
    p_chunk->chunk_flags &= ~CHUNK_FLAG__IS_VISUALLY_UPDATED;
}

static inline
bool is_chunk__awaiting_serialization(Chunk *p_chunk) {
    return p_chunk->chunk_flags & CHUNK_FLAG__IS_AWAITING_SERIALIZATION;
}

static inline
bool is_chunk__awaiting_deserialization(Chunk *p_chunk) {
    return p_chunk->chunk_flags & CHUNK_FLAG__IS_AWAITING_DESERIALIZATION;
}

static inline
bool is_chunk__active(Chunk *p_chunk) {
    return p_chunk->chunk_flags & CHUNK_FLAG__IS_ACTIVE;
}

static inline
bool is_chunk__updated(Chunk *p_chunk) {
    return p_chunk->chunk_flags & CHUNK_FLAG__IS_UPDATED;
}

static inline
bool is_chunk__visually_updated(Chunk *p_chunk) {
    return p_chunk->chunk_flags & CHUNK_FLAG__IS_UPDATED;
}

#endif
