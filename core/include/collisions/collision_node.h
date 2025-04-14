#ifndef COLLISION_NODE_H
#define COLLISION_NODE_H

#include "defines.h"
#include "defines_weak.h"
#include "serialization/serialization_header.h"

void initialize_collision_node(
        Collision_Node *p_collision_node,
        Identifier__u64 uuid__u64);

void add_entry_to__collision_node(
        Collision_Node_Pool *p_collision_node_pool,
        Collision_Node *p_collision_node,
        Hitbox_AABB *p_hitbox);

void remove_entry_from__collision_node(
        Collision_Node_Pool *p_collision_node_pool,
        Collision_Node *p_collision_node,
        Identifier__u32 uuid__u32);

Hitbox_AABB *get_p_hitbox_aabb_at__vector_3i32F4_from__collision_node(
        Collision_Node *p_collision_node,
        Vector__3i32F4 vector__3i32F4);

Quantity__u32 get_quantity_of__entries_in__collision_node(
        const Collision_Node *p_collision_node);

static inline
Collision_Node_Entry *iterate_collision_node__entry(
        Collision_Node_Entry **p_collision_node__entry) {
    *p_collision_node__entry =
        (*p_collision_node__entry)
        ->p_previous_entry;
    return *p_collision_node__entry;
}

static inline
bool is_collision_node__allocated(
        Collision_Node *p_collision_node) {
    return is_serialized_struct__deallocated__uuid_64(
            &p_collision_node->_serialization_header);
}
#endif
