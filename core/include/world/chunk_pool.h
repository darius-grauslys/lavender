#ifndef CHUNK_POOL_H
#define CHUNK_POOL_H

#include "defines.h"
#include "defines_weak.h"

void initialize_chunk_pool(
        Chunk_Pool *p_chunk_pool);

Chunk *allocate_chunk_from__chunk_pool(
        Chunk_Pool *p_chunk_pool,
        Identifier__u32 uuid__u32);

void release_chunk_from__chunk_pool(
        Chunk_Pool *p_chunk_pool,
        Chunk *p_chunk);

#endif
