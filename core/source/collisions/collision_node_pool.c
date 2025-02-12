#include "collisions/collision_node_pool.h"
#include "collisions/collision_node.h"
#include "defines.h"
#include "numerics.h"
#include "platform_defines.h"
#include "serialization/hashing.h"
#include "serialization/serialization_header.h"
#include "serialization/serialized_field.h"

static inline
Collision_Node *get_p_collision_node_by__index_from__collision_node_pool(
        Collision_Node_Pool *p_collision_node_pool,
        Index__u32 index_of__collision_node) {
#ifndef NDEBUG
    if (index_of__collision_node >= QUANTITY_OF__GLOBAL_SPACE) {
        debug_error("get_p_collision_node_by__index_from__collision_node_pool, index out of bounds, %d/%d", index_of__collision_node, QUANTITY_OF__GLOBAL_SPACE);
        return 0;
    }
#endif
    return &p_collision_node_pool->collision_nodes[index_of__collision_node];
}

void initialize_collision_node_pool(
        Collision_Node_Pool *p_collision_node_pool) {
    initialize_serialization_header__contiguous_array(
            (Serialization_Header*)p_collision_node_pool->collision_nodes, 
            QUANTITY_OF__GLOBAL_SPACE, 
            sizeof(Collision_Node));
}

Collision_Node *allocate_collision_node_from__collision_node_pool(
        Collision_Node_Pool *p_collision_node_pool,
        Identifier__u32 uuid__u32) {
    Index__u32 index_of__collision_node =
        poll_for__uuid_collision(
                (Serialization_Header *)p_collision_node_pool->collision_nodes, 
                QUANTITY_OF__GLOBAL_SPACE, 
                uuid__u32);

    if (is_index_u32__out_of_bounds(index_of__collision_node)) {
        debug_error("allocate_collision_node_from__collision_node_pool, failed to allocate collision_node.");
        return 0;
    }

    return get_p_collision_node_by__index_from__collision_node_pool(
            p_collision_node_pool, 
            index_of__collision_node);
}

void release_collision_node_from__collision_node_pool(
        Collision_Node_Pool *p_collision_node_pool,
        Collision_Node *p_collision_node) {
#ifndef NDEBUG
    u32 index = 
        p_collision_node
        - p_collision_node_pool->collision_nodes;
    if (index >= QUANTITY_OF__GLOBAL_SPACE) {
        debug_error("release_collision_node_from__collision_node_pool, p_collision_node is not from this pool.");
        return;
    }
#endif

    initialize_collision_node(
            p_collision_node);
}

Collision_Node_Entry *get_next_available__collision_node_entry(
        Collision_Node_Pool *p_collision_node_pool) {
    for (Index__u32 index_of__entry = 0;
            index_of__entry < MAX_QUANTITY_OF__HITBOX_AABB;
            index_of__entry++) {
        Collision_Node_Entry *p_collision_node_entry =
            &p_collision_node_pool->collision_node_entries[
                index_of__entry];

        if (is_p_serialized_field__linked(
                    &p_collision_node_entry->s_hitbox)) {
            continue;
        }

        return p_collision_node_entry;
    }
    
    debug_error("get_next_available__collision_node_entry, failed to find available entry.");
    return 0;
}
