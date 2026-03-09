#ifndef HITBOX_CONTEXT_H
#define HITBOX_CONTEXT_H

#include "defines.h"
#include "defines_weak.h"

void initialize_hitbox_context(Hitbox_Context *p_hitbox_context);

void register_hitbox_manager(
        Hitbox_Context *p_hitbox_context,
        f_hitbox_manager__allocator f_hitbox_manager__allocator,
        f_hitbox_manager__deallocator f_hitbox_manager__deallocator,
        f_hitbox_manager__get_ptrs_to_properties_of__hitbox 
            f_hitbox_manager__get_properties_of__hitbox,
        Hitbox_Manager_Type the_type_of__hitbox_manager_to__register);


Hitbox_Manager_Instance *allocate_hitbox_manager_from__hitbox_context(
        Hitbox_Context *p_hitbox_context,
        Identifier__u32 uuid_of__hitbox_manager__u32,
        Hitbox_Manager_Type the_type_of__hitbox_manager_to__allocate,
        Quantity__u32 quantity_of__hitboxes_to__pool);

///
/// Returns true if acquision of ptrs is successful.
///
bool get_ptrs_to_properties_of__hitbox(
        Hitbox_Context *p_hitbox_context,
        Identifier__u32 uuid_of__hitbox_manager__u32,
        Identifier__u32 uuid_of__hitbox__u32,
        Vector__3i32 **p_ptr_OPTIONAL_dimensions__3i32,
        Vector__3i32F4 **p_ptr_OPTIONAL_position__3i32F4,
        Vector__3i32F4 **p_ptr_OPTIONAL_velocity__3i32F4,
        Vector__3i32F4 **p_ptr_OPTIONAL_acceleration__3i32F4);

///
/// Returns an invalid Hitbox_Manager_Instance when failing to find.
///
/// Reports no error upon failure to find.
///
Hitbox_Manager_Instance 
*get_p_hitbox_manager_instance_using__uuid_from__hitbox_context(
        Hitbox_Context *p_hitbox_context,
        Identifier__u32 uuid_of__hitbox_manager__u32);

Quantity__u32 get_max_quantity_of__hitboxes_in__hitbox_manager(
        Hitbox_Context *p_hitbox_context,
        Identifier__u32 uuid_of__hitbox_manager__u32);

void *get_pV_hitbox_from__hitbox_context(
        Hitbox_Context *p_hitbox_context,
        Identifier__u32 uuid_of__hitbox_manager__u32,
        Identifier__u32 uuid_of__hitbox__u32);

void release_hitbox_manager_from__hitbox_context(
        Hitbox_Context *p_hitbox_context,
        Identifier__u32 uuid_of__hitbox_manager__u32);

///
/// Returns null ptr when failing to find.
///
/// [ ------- ] Reports no error upon failure to find.
/// [ !NDEBUG ] Reports an error upon invalid type found.
///
Hitbox_AABB_Manager *get_p_hitbox_aabb_manager_from__hitbox_context(
        Hitbox_Context *p_hitbox_context,
        Identifier__u32 uuid_of__hitbox_manager__u32);

#endif
