#include "collisions/collision_node_pool.h"
#include "collisions/collision_node.h"
#include "defines.h"
#include "numerics.h"
#include "platform_defines.h"
#include "serialization/hashing.h"
#include "serialization/identifiers.h"
#include "serialization/serialization_header.h"
#include "serialization/serialized_field.h"

static inline
Collision_Node_Entry *get_p_collision_node_entry_by__index_from__collision_node_pool(
        Collision_Node_Pool *p_collision_node_pool,
        Index__u32 index_of__collision_node_entry) {
#ifndef NDEBUG
    if (!p_collision_node_pool) {
        debug_error("get_p_collision_node_entry_by__index_from__collision_node_pool, p_collision_node == 0.");
        return 0;
    }
    if (index_of__collision_node_entry >= MAX_QUANTITY_OF__HITBOX_AABB) {
        debug_error("get_p_collision_node_entry_by__index_from__collision_node_pool, index_of__collision_node_entry > MAX_QUANTITY_OF__HITBOX_AABB.");
        return 0;
    }
#endif
    return &p_collision_node_pool->collision_node_entries[
        index_of__collision_node_entry];
}

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

static inline
void initialize_collision_node_entry(
        Collision_Node_Entry *p_collision_node_entry) {
    p_collision_node_entry->uuid_of__hitbox__u32 =
        IDENTIFIER__UNKNOWN__u32;
    p_collision_node_entry->p_previous_entry = 0;
}

void initialize_collision_node_pool(
        Collision_Node_Pool *p_collision_node_pool) {
    initialize_serialization_header__contiguous_array__uuid_64(
            (Serialization_Header__UUID_64*)
                p_collision_node_pool->collision_nodes, 
            QUANTITY_OF__GLOBAL_SPACE, 
            sizeof(Collision_Node));
    for (Index__u32 index_of__collision_node_entry = 0;
            index_of__collision_node_entry < MAX_QUANTITY_OF__HITBOX_AABB;
            index_of__collision_node_entry++) {
        initialize_collision_node_entry(
                get_p_collision_node_entry_by__index_from__collision_node_pool(
                    p_collision_node_pool,
                    index_of__collision_node_entry));
    }
}

Collision_Node *allocate_collision_node_from__collision_node_pool(
        Collision_Node_Pool *p_collision_node_pool,
        Identifier__u64 uuid__u64) {
    Collision_Node *p_collision_node =
        (Collision_Node*)get_next_available__allocation_in__contiguous_array__u64(
                (Serialization_Header__UUID_64*)
                    p_collision_node_pool->collision_nodes, 
                QUANTITY_OF__GLOBAL_SPACE, 
                uuid__u64);

    if (!p_collision_node) {
        debug_error("allocate_collision_node_from__collision_node_pool, failed to allocate collision_node.");
        return 0;
    }
    if (!IS_DEALLOCATED_P__u64(p_collision_node)) {
        debug_error("allocate_collision_node_from__collision_node_pool, uuid already in use.");
        return 0;
    }

    initialize_collision_node(
            p_collision_node, 
            uuid__u64);

    return p_collision_node;
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

    initialize_serialization_header_for__deallocated_struct__uuid_64(
            &p_collision_node->_serialization_header, 
            sizeof(Collision_Node));
}

Collision_Node_Entry *allocate_collision_node_entry_from__collision_node_pool(
        Collision_Node_Pool *p_collision_node_pool) {
    // TODO: can we do better than O(N) here?
    for (Index__u32 index_of__entry = 0;
            index_of__entry < MAX_QUANTITY_OF__HITBOX_AABB;
            index_of__entry++) {
        Collision_Node_Entry *p_collision_node_entry =
            &p_collision_node_pool->collision_node_entries[
                index_of__entry];

        if (!is_identifier_u32__invalid(
                    p_collision_node_entry->uuid_of__hitbox__u32)) {
            continue;
        }

        return p_collision_node_entry;
    }
    
    debug_error("get_next_available__collision_node_entry, failed to find available entry.");
    return 0;
}

void release_collision_node_entry_from__collision_node_pool(
        Collision_Node_Pool *p_collision_node_pool,
        Collision_Node_Entry *p_collision_node_entry) {
#ifndef NDEBUG
    if (!p_collision_node_pool) {
        debug_error("release_collision_node_from__collision_node_pool, p_collision_node_pool == 0.");
        return;
    }
    if (!p_collision_node_entry) {
        debug_error("release_collision_node_from__collision_node_pool, p_collision_node_entry == 0.");
        return;
    }
    if (p_collision_node_entry - p_collision_node_pool->collision_node_entries
            >= MAX_QUANTITY_OF__HITBOX_AABB) {
        debug_error("release_collision_node_entry_from__collision_node_pool, p_collision_node_entry is not allocated with this collision_node_pool.");
        return;
    }
#endif
    initialize_collision_node_entry(p_collision_node_entry);
}
