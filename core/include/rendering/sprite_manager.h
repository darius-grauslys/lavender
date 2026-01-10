#ifndef SPRITE_MANAGER_H
#define SPRITE_MANAGER_H

#include "defines.h"
#include "defines_weak.h"
#include "serialization/hashing.h"

void initialize_sprite_manager(
        Sprite_Manager *p_sprite_manager);

bool allocate_sprite_pools_from__sprite_manager(
        Sprite_Manager *p_sprite_manager,
        Quantity__u8 quantity_of__sprite_pools);

void release_sprite_pools_from__sprite_manager(
        Sprite_Manager *p_sprite_manager);

Sprite_Pool *allocate_sprite_pool_from__sprite_manager(
        Sprite_Manager *p_sprite_manager,
        Identifier__u32 uuid_of__sprite_pool,
        Quantity__u32 max_quantity_of__sprites_in__sprite_pool);

void release_sprite_pool_from__sprite_manager(
        Sprite_Manager *p_sprite_manager,
        Sprite_Pool *p_sprite_pool);

static inline
bool is_sprite_pools_allocated_in__sprite_manager(
        Sprite_Manager *p_sprite_manager) {
    return p_sprite_manager->pM_sprite_pools;
}

static inline
Sprite_Pool *get_p_sprite_pool_by__uuid_from__sprite_manager(
        Sprite_Manager *p_sprite_manager,
        Identifier__u32 uuid_of__sprite_pool) {
    return (Sprite_Pool*)dehash_identitier_u32_in__contigious_array(
            (Serialization_Header*)p_sprite_manager->pM_sprite_pools, 
            p_sprite_manager->max_quantity_of__sprite_pools, 
            uuid_of__sprite_pool);
}

static inline
void register_sprite_animation_into__sprite_manager(
        Sprite_Manager *p_sprite_manager,
        Sprite_Animation_Kind the_kind_of__sprite_animation,
        Sprite_Animation sprite_animation) {
#ifndef NDEBUG
    if (!p_sprite_manager) {
        debug_error("register_sprite_animation_into__sprite_manager, p_sprite_manager == 0.");
        return;
    }
    if (the_kind_of__sprite_animation >= Sprite_Animation_Kind__Unknown) {
        debug_error("register_sprite_animation_into__sprite_manager, the_kind_of__sprite_animation >= Sprite_Animation_Kind__Unknown.");
        return;
    }
#endif
    p_sprite_manager->sprite_animations[
        the_kind_of__sprite_animation] = sprite_animation;
}

static inline
Sprite_Animation get_sprite_animation_from__sprite_manager(
        Sprite_Manager *p_sprite_manager,
        Sprite_Animation_Kind the_kind_of__sprite_animation) {
#ifndef NDEBUG
    if (!p_sprite_manager) {
        debug_error("get_sprite_animation_from__sprite_manager, p_sprite_manager == 0.");
        return (Sprite_Animation){0};
    }
    if (the_kind_of__sprite_animation >= Sprite_Animation_Kind__Unknown) {
        debug_error("get_sprite_animation_from__sprite_manager, the_kind_of__sprite_animation >= Sprite_Animation_Kind__Unknown.");
        return (Sprite_Animation){0};
    }
#endif
    return p_sprite_manager->sprite_animations[
        the_kind_of__sprite_animation];
}

static inline
void register_sprite_animation_group_into__sprite_manager(
        Sprite_Manager *p_sprite_manager,
        Sprite_Animation_Group_Kind the_kind_of__sprite_animation_group,
        Sprite_Animation_Group_Set sprite_animation_group) {
#ifndef NDEBUG
    if (!p_sprite_manager) {
        debug_error("register_sprite_animation_group_into__sprite_manager, p_sprite_manager == 0.");
        return;
    }
    if (the_kind_of__sprite_animation_group 
            >= Sprite_Animation_Group_Kind__Unknown) {
        debug_error("register_sprite_animation_group_into__sprite_manager, the_kind_of__sprite_animation_group >= Sprite_Animation_Group_Kind__Unknown.");
        return;
    }
#endif
    p_sprite_manager->sprite_animation_groups[
        the_kind_of__sprite_animation_group] = sprite_animation_group;
}

static inline
Sprite_Animation_Group_Set get_sprite_animation_group_from__sprite_manager(
        Sprite_Manager *p_sprite_manager,
        Sprite_Animation_Group_Kind the_kind_of__sprite_animation_group) {
#ifndef NDEBUG
    if (!p_sprite_manager) {
        debug_error("get_sprite_animation_group_from__sprite_manager, p_sprite_manager == 0.");
        return (Sprite_Animation_Group_Set){0};
    }
    if (the_kind_of__sprite_animation_group >= Sprite_Animation_Group_Kind__Unknown) {
        debug_error("get_sprite_animation_group_from__sprite_manager, the_kind_of__sprite_animation_group >= Sprite_Animation_Group_Kind__Unknown.");
        return (Sprite_Animation_Group_Set){0};
    }
#endif
    return p_sprite_manager->sprite_animation_groups[
        the_kind_of__sprite_animation_group];
}

static inline
Sprite_Animation_Group_Set 
*get_p_sprite_animation_group_from__sprite_manager(
        Sprite_Manager *p_sprite_manager,
        Sprite_Animation_Group_Kind the_kind_of__sprite_animation_group) {
#ifndef NDEBUG
    if (the_kind_of__sprite_animation_group
            >= Sprite_Animation_Kind__Unknown) {
        debug_error("get_p_sprite_animation_group_from__sprite_manager, invalid kind.");
        return 0;
    }
#endif
    return &p_sprite_manager->sprite_animation_groups[
        the_kind_of__sprite_animation_group];
}

#endif
