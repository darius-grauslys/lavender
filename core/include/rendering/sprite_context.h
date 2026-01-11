#ifndef SPRITE_CONTEXT_H
#define SPRITE_CONTEXT_H

#include "defines.h"
#include "defines_weak.h"
#include "serialization/hashing.h"

void initialize_sprite_context(
        Sprite_Context *p_sprite_context);

bool allocate_sprite_managers_from__sprite_context(
        Sprite_Context *p_sprite_context,
        Quantity__u8 quantity_of__sprite_managers);

void release_sprite_managers_from__sprite_context(
        Sprite_Context *p_sprite_context);

Sprite_Manager *allocate_sprite_manager_from__sprite_context(
        Sprite_Context *p_sprite_context,
        Identifier__u32 uuid_of__sprite_manager,
        Quantity__u32 max_quantity_of__sprites_in__sprite_manager);

void release_sprite_manager_from__sprite_context(
        Sprite_Context *p_sprite_context,
        Sprite_Manager *p_sprite_manager);

static inline
bool is_sprite_managers_allocated_in__sprite_context(
        Sprite_Context *p_sprite_context) {
    return p_sprite_context->pM_sprite_managers;
}

static inline
Sprite_Manager *get_p_sprite_manager_by__uuid_from__sprite_context(
        Sprite_Context *p_sprite_context,
        Identifier__u32 uuid_of__sprite_manager) {
    return (Sprite_Manager*)dehash_identitier_u32_in__contigious_array(
            (Serialization_Header*)p_sprite_context->pM_sprite_managers, 
            p_sprite_context->max_quantity_of__sprite_managers, 
            uuid_of__sprite_manager);
}

static inline
void register_sprite_animation_into__sprite_context(
        Sprite_Context *p_sprite_context,
        Sprite_Animation_Kind the_kind_of__sprite_animation,
        Sprite_Animation sprite_animation) {
#ifndef NDEBUG
    if (!p_sprite_context) {
        debug_error("register_sprite_animation_into__sprite_context, p_sprite_context == 0.");
        return;
    }
    if (the_kind_of__sprite_animation >= Sprite_Animation_Kind__Unknown) {
        debug_error("register_sprite_animation_into__sprite_context, the_kind_of__sprite_animation >= Sprite_Animation_Kind__Unknown.");
        return;
    }
#endif
    p_sprite_context->sprite_animations[
        the_kind_of__sprite_animation] = sprite_animation;
}

static inline
Sprite_Animation get_sprite_animation_from__sprite_context(
        Sprite_Context *p_sprite_context,
        Sprite_Animation_Kind the_kind_of__sprite_animation) {
#ifndef NDEBUG
    if (!p_sprite_context) {
        debug_error("get_sprite_animation_from__sprite_context, p_sprite_context == 0.");
        return (Sprite_Animation){0};
    }
    if (the_kind_of__sprite_animation >= Sprite_Animation_Kind__Unknown) {
        debug_error("get_sprite_animation_from__sprite_context, the_kind_of__sprite_animation >= Sprite_Animation_Kind__Unknown.");
        return (Sprite_Animation){0};
    }
#endif
    return p_sprite_context->sprite_animations[
        the_kind_of__sprite_animation];
}

static inline
void register_sprite_animation_group_into__sprite_context(
        Sprite_Context *p_sprite_context,
        Sprite_Animation_Group_Kind the_kind_of__sprite_animation_group,
        Sprite_Animation_Group_Set sprite_animation_group) {
#ifndef NDEBUG
    if (!p_sprite_context) {
        debug_error("register_sprite_animation_group_into__sprite_context, p_sprite_context == 0.");
        return;
    }
    if (the_kind_of__sprite_animation_group 
            >= Sprite_Animation_Group_Kind__Unknown) {
        debug_error("register_sprite_animation_group_into__sprite_context, the_kind_of__sprite_animation_group >= Sprite_Animation_Group_Kind__Unknown.");
        return;
    }
#endif
    p_sprite_context->sprite_animation_groups[
        the_kind_of__sprite_animation_group] = sprite_animation_group;
}

static inline
Sprite_Animation_Group_Set get_sprite_animation_group_from__sprite_context(
        Sprite_Context *p_sprite_context,
        Sprite_Animation_Group_Kind the_kind_of__sprite_animation_group) {
#ifndef NDEBUG
    if (!p_sprite_context) {
        debug_error("get_sprite_animation_group_from__sprite_context, p_sprite_context == 0.");
        return (Sprite_Animation_Group_Set){0};
    }
    if (the_kind_of__sprite_animation_group >= Sprite_Animation_Group_Kind__Unknown) {
        debug_error("get_sprite_animation_group_from__sprite_context, the_kind_of__sprite_animation_group >= Sprite_Animation_Group_Kind__Unknown.");
        return (Sprite_Animation_Group_Set){0};
    }
#endif
    return p_sprite_context->sprite_animation_groups[
        the_kind_of__sprite_animation_group];
}

static inline
Sprite_Animation_Group_Set 
*get_p_sprite_animation_group_from__sprite_context(
        Sprite_Context *p_sprite_context,
        Sprite_Animation_Group_Kind the_kind_of__sprite_animation_group) {
#ifndef NDEBUG
    if (the_kind_of__sprite_animation_group
            >= Sprite_Animation_Kind__Unknown) {
        debug_error("get_p_sprite_animation_group_from__sprite_context, invalid kind.");
        return 0;
    }
#endif
    return &p_sprite_context->sprite_animation_groups[
        the_kind_of__sprite_animation_group];
}

#endif
