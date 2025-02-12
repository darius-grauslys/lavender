#ifndef COLLISION_NODE_POOL_H
#define COLLISION_NODE_POOL_H

#include "defines.h"
#include "defines_weak.h"

void initialize_collision_node_pool(
        Collision_Node_Pool *p_collision_node_pool);

Collision_Node *allocate_collision_node_from__collision_node_pool(
        Collision_Node_Pool *p_collision_node_pool,
        Identifier__u32 uuid__u32);

void release_collision_node_from__collision_node_pool(
        Collision_Node_Pool *p_collision_node_pool,
        Collision_Node *p_collision_node);

#endif
