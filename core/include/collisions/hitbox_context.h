#ifndef HITBOX_CONTEXT_H
#define HITBOX_CONTEXT_H

#include "defines.h"
#include "defines_weak.h"

void initialize_hitbox_context(Hitbox_Context *p_hitbox_context);

///
/// NOTE: ALL HITBOX MANAGERS MUST OBEY defines.h:Hitbox_Manager_Instrinsic
///
/// Failure to do so will lead to undefined behavior!
///
void register_hitbox_manager(
        Hitbox_Context *p_hitbox_context,
        f_Hitbox_Manager__Allocator f_hitbox_manager__allocator,
        f_Hitbox_Manager__Deallocator f_hitbox_manager__deallocator,
        f_Hitbox_Manager__Opaque_Property_Access_Of__Hitbox 
            f_hitbox_manager__get_properties_of__hitbox,
        Hitbox_Manager_Type the_type_of__hitbox_manager_to__register,
        u8 quantity_of__components__dimensions,
        u8 quantity_of__components__pos_vel_acc,
        u8 size_of__components__dimensions,
        u8 size_of__components__pos_vel,
        u8 size_of__components__acceleration,
        u8 fractional_percision_of__dimensions,
        u8 fractional_percision_of__pos_vel,
        u8 fractional_percision_of__acceleration
        );

Hitbox_Manager_Instance *allocate_hitbox_manager_from__hitbox_context(
        Hitbox_Context *p_hitbox_context,
        Identifier__u32 uuid_of__hitbox_manager__u32,
        Hitbox_Manager_Type the_type_of__hitbox_manager_to__allocate,
        Quantity__u32 quantity_of__hitboxes_to__pool);

void *allocate_pV_hitbox_from__hitbox_context(
        Hitbox_Context *p_hitbox_context,
        Identifier__u32 uuid_of__hitbox_manager__u32,
        Identifier__u32 uuid_of__hitbox__u32);

#define OPAQUE_HITBOX_ACCESS__SET (true)
#define OPAQUE_HITBOX_ACCESS__GET (false)

///
/// If is setting, the opaque callback handler will try
/// and read pV ptrs as the expected format (see Hitbox_Manager_Instance)
/// and either mutate the hitbox to the given values or
/// set the pointer contents to match the hitbox values
/// depending on the boolean state of is_setting_or__getting.
///
/// Returns true if modification/access was performed.
///
bool opaque_access_to__hitbox(
        Hitbox_Context *p_hitbox_context,
        Identifier__u32 uuid_of__hitbox_manager__u32,
        Identifier__u32 uuid_of__hitbox__u32,
        void *pV_OPTIONAL_dimensions,
        void *pV_OPTIONAL_position,
        void *pV_OPTIONAL_velocity,
        void *pV_OPTIONAL_acceleration,
        Hitbox_Flags__u8 *p_OPTIONAL_hitbox_flags__u8,
        bool is_setting_or__getting);

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
