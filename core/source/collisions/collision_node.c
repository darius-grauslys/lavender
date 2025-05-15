#include "collisions/collision_node.h"
#include "collisions/collision_node_pool.h"
#include "collisions/hitbox_aabb.h"
#include "collisions/hitbox_aabb_manager.h"
#include "defines.h"
#include "defines_weak.h"
#include "entity/entity_manager.h"
#include "game.h"
#include "serialization/serialization_header.h"
#include "world/world.h"

void initialize_collision_node(
        Collision_Node *p_collision_node,
        Identifier__u64 uuid__u64) {
    initialize_serialization_header__uuid_64(
            &p_collision_node->_serialization_header, 
            uuid__u64,
            sizeof(Collision_Node));
    p_collision_node->p_linked_list__collision_node_entries__tail = 0;
}

bool add_entry_to__collision_node(
        Collision_Node_Pool *p_collision_node_pool,
        Collision_Node *p_collision_node,
        Hitbox_AABB *p_hitbox) {
#ifndef NDEBUG
    if (!p_collision_node_pool) {
        debug_error("add_entry_to__collision_node, p_collision_node_pool == 0.");
        return false;
    }
    if (!p_collision_node) {
        debug_error("add_entry_to__collision_node, p_collision_node == 0.");
        return false;
    }
    if (!p_hitbox) {
        debug_error("add_entry_to__collision_node, p_hitbox == 0.");
        return false;
    }
#endif
    Collision_Node_Entry *p_collision_node_entry =
        allocate_collision_node_entry_from__collision_node_pool(p_collision_node_pool);

    if (!p_collision_node_entry) {
        debug_error("add_entry_to__collision_node, p_collision_node_entry == 0.");
        return false;
    }

    p_collision_node_entry->uuid_of__hitbox__u32 =
        GET_UUID_P(p_hitbox);

    p_collision_node_entry->p_previous_entry =
        p_collision_node->p_linked_list__collision_node_entries__tail;
    p_collision_node->p_linked_list__collision_node_entries__tail =
        p_collision_node_entry;

    return true;
}

void remove_entry_from__collision_node(
        Collision_Node_Pool *p_collision_node_pool,
        Collision_Node *p_collision_node,
        Identifier__u32 uuid__u32) {
    Collision_Node_Entry *p_collision_node_entry =
        p_collision_node->p_linked_list__collision_node_entries__tail;
    Collision_Node_Entry *p_collision_node_entry__parent = 
        p_collision_node_entry;

    while (p_collision_node_entry) {
        if (uuid__u32 == p_collision_node_entry->uuid_of__hitbox__u32) {
            break;
        }
        p_collision_node_entry__parent =
            p_collision_node_entry;
        p_collision_node_entry =
            p_collision_node_entry->p_previous_entry;
    }

    if (!p_collision_node_entry) {
        debug_error("remove_entry_from__collision_node, uuid__u32 not present in node.");
        return;
    }

    if (p_collision_node_entry
            == p_collision_node_entry__parent) {
        p_collision_node
            ->p_linked_list__collision_node_entries__tail =
            p_collision_node_entry->p_previous_entry;
    } else {
        p_collision_node_entry__parent->p_previous_entry =
            p_collision_node_entry->p_previous_entry;
    }

    release_collision_node_entry_from__collision_node_pool(
            p_collision_node_pool, 
            p_collision_node_entry);
}

Hitbox_AABB *get_p_hitbox_aabb_at__vector_3i32F4_from__collision_node(
        Hitbox_AABB_Manager *p_hitbox_aabb_manager,
        Collision_Node *p_collision_node,
        Vector__3i32F4 vector__3i32F4) {
    if (!p_collision_node->p_linked_list__collision_node_entries__tail)
        return 0;

    Collision_Node_Entry *p_entry =
        p_collision_node->p_linked_list__collision_node_entries__tail;

    do {
        Hitbox_AABB *p_hitbox_aabb =
            get_p_hitbox_aabb_by__uuid_u32_from__hitbox_aabb_manager(
                    p_hitbox_aabb_manager, 
                    p_entry->uuid_of__hitbox__u32);
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

void poll_for__collisions_within_this__collision_node(
        Game *p_game,
        World *p_world,
        Collision_Node *p_collision_node,
        f_Hitbox_AABB_Collision_Handler f_hitbox_collision_handler,
        Hitbox_AABB *p_hitbox_aabb) {
    Collision_Node_Entry *p_collision_node_entry =
        p_collision_node->p_linked_list__collision_node_entries__tail;

    while (p_collision_node_entry) {
        Hitbox_AABB *p_hitbox_aabb__other =
            get_p_hitbox_aabb_by__uuid_u32_from__hitbox_aabb_manager(
                    get_p_hitbox_aabb_manager_from__game(p_game), 
                    p_collision_node_entry->uuid_of__hitbox__u32);

        if (p_hitbox_aabb__other 
                && p_hitbox_aabb__other
                != p_hitbox_aabb
                && is_hitbox__colliding(
                    p_hitbox_aabb, 
                    p_hitbox_aabb__other)) {
            f_hitbox_collision_handler(
                    p_game,
                    p_world,
                    p_hitbox_aabb,
                    p_hitbox_aabb__other);
        }

        p_collision_node_entry =
            p_collision_node_entry->p_previous_entry;
    }
}

Entity *iterate_entities_in__collision_node_entry(
        Entity_Manager *p_entity_manager,
        Collision_Node_Entry **p_ptr_collision_node__entry,
        Entity **p_ptr_entity) {
#ifndef NDEBUG
    if (!p_ptr_entity) {
        debug_error("iterate_entities_in__collision_node_entry, p_ptr_entity == 0.");
        return 0;
    }
    if (!p_entity_manager) {
        debug_error("iterate_entities_in__collision_node_entry, p_entity_manager == 0.");
        *p_ptr_entity = 0;
        return 0;
    }
#endif
    Collision_Node_Entry *p_collision_node_entry =
        *p_ptr_collision_node__entry;
    if (!p_collision_node_entry) {
        *p_ptr_entity = 0;
        return 0;
    }

    Entity *p_entity =
        get_p_entity_by__uuid_from__entity_manager(
                p_entity_manager, 
                p_collision_node_entry->uuid_of__hitbox__u32);

    *p_ptr_collision_node__entry =
        p_collision_node_entry
        ->p_previous_entry;
    *p_ptr_entity = p_entity;

    return p_entity;
}
