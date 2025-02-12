#include "collisions/collision_node.h"
#include "defines.h"
#include "serialization/serialization_header.h"

void initialize_collision_node(
        Collision_Node *p_collision_node) {
    initialize_serialization_header_for__deallocated_struct(
            &p_collision_node->_serialization_header, 
            sizeof(Collision_Node));
    p_collision_node->p_linked_list__collision_node_entries__tail = 0;
}

void add_entry_to__collision_node(
        Collision_Node_Pool *p_collision_node_pool,
        Collision_Node *p_collision_node,
        Hitbox_AABB *p_hitbox) {
    debug_abort("add_entry_to__collision_node, impl");
}
