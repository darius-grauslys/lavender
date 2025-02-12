#ifndef COLLISION_NODE_H
#define COLLISION_NODE_H

#include "defines.h"
#include "serialization/serialization_header.h"

void initialize_collision_node(
        Collision_Node *p_collision_node);

void add_entry_to__collision_node(
        Collision_Node_Pool *p_collision_node_pool,
        Collision_Node *p_collision_node,
        Hitbox_AABB *p_hitbox);

static inline
bool is_collision_node__allocated(
        Collision_Node *p_collision_node) {
    return is_serialized_struct__deallocated(
            &p_collision_node->_serialization_header);
}
#endif
