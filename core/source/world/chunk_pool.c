#include "world/chunk_pool.h"
#include "numerics.h"
#include "platform_defines.h"
#include "serialization/hashing.h"
#include "serialization/serialization_header.h"
#include "world/chunk.h"

static inline
Chunk *get_p_chunk_by__index_from__chunk_pool(
        Chunk_Pool *p_chunk_pool,
        Index__u32 index_of__chunk) {
#ifndef NDEBUG
    if (index_of__chunk >= QUANTITY_OF__GLOBAL_SPACE) {
        debug_error("get_p_chunk_by__index_from__chunk_pool, index out of bounds, %d/%d", index_of__chunk, QUANTITY_OF__GLOBAL_SPACE);
        return 0;
    }
#endif
    return &p_chunk_pool->chunks[index_of__chunk];
}

void initialize_chunk_pool(
        Chunk_Pool *p_chunk_pool) {
    initialize_serialization_header__contiguous_array(
            (Serialization_Header *)p_chunk_pool->chunks, 
            QUANTITY_OF__GLOBAL_SPACE, 
            sizeof(Chunk));
}

Chunk *allocate_chunk_from__chunk_pool(
        Chunk_Pool *p_chunk_pool,
        Identifier__u32 uuid__u32) {
    Index__u32 index_of__chunk =
        poll_for__uuid_collision(
                (Serialization_Header *)p_chunk_pool->chunks, 
                QUANTITY_OF__GLOBAL_SPACE, 
                uuid__u32);
    
    if (is_index_u32__out_of_bounds(index_of__chunk)) {
        debug_error("allocate_chunk_from__chunk_pool, failed to allocate chunk.");
        return 0;
    }

    return get_p_chunk_by__index_from__chunk_pool(
            p_chunk_pool, 
            index_of__chunk);
}

void release_chunk_from__chunk_pool(
        Chunk_Pool *p_chunk_pool,
        Chunk *p_chunk) {
#ifndef NDEBUG
    u32 index =
        p_chunk
        - p_chunk_pool->chunks;
    if (index >= QUANTITY_OF__GLOBAL_SPACE) {
        debug_error("release_chunk_from__chunk_pool, p_chunk is not from this pool.");
        return;
    }
#endif

    initialize_chunk(p_chunk);
}
