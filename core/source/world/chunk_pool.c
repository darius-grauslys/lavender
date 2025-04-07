#include "world/chunk_pool.h"
#include "defines.h"
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
    initialize_serialization_header__contiguous_array__uuid_64(
            (Serialization_Header__UUID_64*)p_chunk_pool->chunks, 
            QUANTITY_OF__GLOBAL_SPACE, 
            sizeof(Chunk));
}

Chunk *allocate_chunk_from__chunk_pool(
        Chunk_Pool *p_chunk_pool,
        Identifier__u64 uuid__u64) {
    Chunk *p_chunk =
        (Chunk*)get_next_available__allocation_in__contiguous_array__u64(
                (Serialization_Header__UUID_64*)p_chunk_pool->chunks, 
                QUANTITY_OF__GLOBAL_SPACE, 
                uuid__u64);
    
    if (!p_chunk) {
        debug_error("allocate_chunk_from__chunk_pool, failed to allocate chunk.");
        return 0;
    }
    if (!IS_DEALLOCATED_P__u64(p_chunk)) {
        debug_error("allocate_chunk_from__chunk_pool, uuid already in use.");
        return 0;
    }

    initialize_chunk(
            p_chunk,
            uuid__u64);

    return p_chunk;
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

    initialize_serialization_header_for__deallocated_struct__uuid_64(
            &p_chunk->_serialization_header, 
            sizeof(Chunk));
    p_chunk->chunk_flags = CHUNK_FLAGS__NONE;
}
