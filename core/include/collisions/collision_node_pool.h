#ifndef COLLISION_NODE_POOL_H
#define COLLISION_NODE_POOL_H

#include "defines.h"
#include "defines_weak.h"
#include "platform_defines.h"
#include "serialization/hashing.h"

void initialize_collision_node_pool(
        Collision_Node_Pool *p_collision_node_pool);

Collision_Node *allocate_collision_node_from__collision_node_pool(
        Collision_Node_Pool *p_collision_node_pool,
        Identifier__u64 uuid__u64);

void release_collision_node_from__collision_node_pool(
        Collision_Node_Pool *p_collision_node_pool,
        Collision_Node *p_collision_node);

Collision_Node_Entry *allocate_collision_node_entry_from__collision_node_pool(
        Collision_Node_Pool *p_collision_node_pool);

void release_collision_node_entry_from__collision_node_pool(
        Collision_Node_Pool *p_collision_node_pool,
        Collision_Node_Entry *p_collision_node_entry);

static inline
Collision_Node *get_p_collision_node_by__uuid_64_from__collision_node_pool(
        Collision_Node_Pool *p_collision_node_pool,
        Identifier__u64 uuid__u64) {
    return (Collision_Node*)dehash_identitier_u64_in__contigious_array(
            (Serialization_Header__UUID_64*)
                &p_collision_node_pool->collision_nodes, 
            QUANTITY_OF__GLOBAL_SPACE, 
            uuid__u64);
}

#endif
