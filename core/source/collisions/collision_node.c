#include "collisions/collision_node.h"
#include "collisions/hitbox_aabb.h"
#include "defines.h"
#include "defines_weak.h"
#include "serialization/serialization_header.h"

void initialize_collision_node(
        Collision_Node *p_collision_node,
        Identifier__u64 uuid__u64) {
    initialize_serialization_header__uuid_64(
            &p_collision_node->_serialization_header, 
            uuid__u64,
            sizeof(Collision_Node));
    p_collision_node->p_linked_list__collision_node_entries__tail = 0;
}

void add_entry_to__collision_node(
        Collision_Node_Pool *p_collision_node_pool,
        Collision_Node *p_collision_node,
        Hitbox_AABB *p_hitbox) {
    debug_abort("add_entry_to__collision_node, impl");
}

void remove_entry_from__collision_node(
        Collision_Node_Pool *p_collision_node_pool,
        Collision_Node *p_collision_node,
        Identifier__u32 uuid__u32) {
    debug_abort("remove_entry_to__collision_node, impl");
}

Hitbox_AABB *get_p_hitbox_aabb_at__vector_3i32F4_from__collision_node(
        Collision_Node *p_collision_node,
        Vector__3i32F4 vector__3i32F4) {
    if (!p_collision_node->p_linked_list__collision_node_entries__tail)
        return 0;

    Collision_Node_Entry *p_entry =
        p_collision_node->p_linked_list__collision_node_entries__tail;

    do {
        Hitbox_AABB *p_hitbox_aabb =
            (Hitbox_AABB*)p_entry->s_hitbox.p_serialized_field__data;
        if (p_hitbox_aabb
                && is_vector_3i32F4_inside__hitbox(
                    vector__3i32F4, 
                    p_hitbox_aabb)) {
            return p_hitbox_aabb;
        }
    } while((p_entry = p_entry->p_previous_entry));

    return 0;
}

Quantity__u32 get_quantity_of__entries_in__collision_node(
        const Collision_Node *p_collision_node) {
    Collision_Node_Entry *p_collision_node__entry =
        p_collision_node
        ->p_linked_list__collision_node_entries__tail;

    Quantity__u32 quantity_of__entries = 0;

    if (!p_collision_node__entry)
        return 0;

    do {
        quantity_of__entries++;
    } while (iterate_collision_node__entry(
                &p_collision_node__entry));

    return quantity_of__entries;
}
