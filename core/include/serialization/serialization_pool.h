#ifndef SERIALIZATION_POOL_H
#define SERIALIZATION_POOL_H

#include "defines.h"
#include "defines_weak.h"
#include "serialization/hashing.h"

void initialize_serialization_pool(
        Serialization_Pool *p_serialization_pool,
        Quantity__u32 quantity_of__pool_elements,
        Quantity__u32 size_of__element);

Serialization_Header *allocate_from__serialization_pool(
        Serialization_Pool *p_serialization_pool);

void release_from__serialization_pool(
        Serialization_Pool *p_serialization_pool,
        Serialization_Header *p_serialization_header);

static inline
Serialization_Header *dehash_from__serialization_pool(
        Serialization_Pool *p_serialization_pool,
        Identifier__u32 uuid__u32) {
    return dehash_identitier_u32_in__contigious_array(
                p_serialization_pool->p_headers,
                p_serialization_pool->quantity_of__pool_elements
                * p_serialization_pool->size_of__element,
                uuid__u32);
}

static inline
void allocate_by_hash_in__serialization_pool(
        Serialization_Pool *p_serialization_pool,
        Identifier__u32 uuid__u32) {
    Serialization_Header *p_serialization_header =
        dehash_identitier_u32_in__contigious_array(
                p_serialization_pool->p_headers,
                p_serialization_pool->quantity_of__pool_elements
                * p_serialization_pool->size_of__element,
                uuid__u32);
    if (p_serialization_header)
        p_serialization_header->uuid = uuid__u32;
}

#endif
