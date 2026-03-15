#include "collisions/hitbox_context.h"
#include "collisions/implemented/hitbox_context/hitbox_manager_registrar.h"
#include "debug/debug.h"
#include "defines.h"
#include "collisions/hitbox_manager_instance.h"
#include "defines_weak.h"
#include "serialization/hashing.h"
#include "serialization/serialization_header.h"
#include "types/implemented/hitbox_manager_type.h"

void initialize_hitbox_context(Hitbox_Context *p_hitbox_context) {
    initialize_serialization_header__contiguous_array(
            (Serialization_Header *)p_hitbox_context->hitbox_manager_instances, 
            MAX_QUANTITY_OF__HITBOX_MANAGERS, 
            sizeof(Hitbox_Manager_Instance));

    register_hitbox_managers(p_hitbox_context);
}

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
        ) {
#ifndef NDEBUG
    if (Hitbox_Manager_Type__Unknown <= the_type_of__hitbox_manager_to__register) {
        debug_error("register_hitbox_manager_allocator, invalid type.");
        return;
    }
#endif

    Hitbox_Manager_Registration_Record *p_hitbox_manager_registration_record =
        &p_hitbox_context->hitbox_manager_registration_records[
        the_type_of__hitbox_manager_to__register];

    p_hitbox_manager_registration_record
        ->size_of__components__dimensions =
            size_of__components__dimensions;
    p_hitbox_manager_registration_record
        ->size_of__components__pos_vel =
            size_of__components__pos_vel;
    p_hitbox_manager_registration_record
        ->size_of__components__acceleration =
            size_of__components__acceleration;

    p_hitbox_manager_registration_record
        ->quantity_of__components__dimensions =
            quantity_of__components__dimensions;
    p_hitbox_manager_registration_record
        ->quantity_of__components__pos_vel_acc =
            quantity_of__components__pos_vel_acc;

    p_hitbox_manager_registration_record
        ->fractional_percision_of__dimensions = 
            fractional_percision_of__dimensions;
    p_hitbox_manager_registration_record
        ->fractional_percision_of__pos_vel = 
            fractional_percision_of__pos_vel;
    p_hitbox_manager_registration_record
        ->fractional_percision_of__acceleration = 
            fractional_percision_of__acceleration;

    Hitbox_Manager_Instance__Invocation_Table *p_invocation_table =
        &p_hitbox_context->hitbox_manager_instance__invocation_table[
            the_type_of__hitbox_manager_to__register];

    p_invocation_table->f_hitbox_manager__allocator 
        = f_hitbox_manager__allocator;
    p_invocation_table->f_hitbox_manager__deallocator 
        = f_hitbox_manager__deallocator;
    p_invocation_table->f_hitbox_manager__get_properties_of__hitbox
        = f_hitbox_manager__get_properties_of__hitbox;
}

Hitbox_Manager_Instance *allocate_hitbox_manager_from__hitbox_context(
        Hitbox_Context *p_hitbox_context,
        Identifier__u32 uuid_of__hitbox_manager__u32,
        Hitbox_Manager_Type the_type_of__hitbox_manager_to__allocate,
        Quantity__u32 quantity_of__hitboxes_to__pool) {
#ifndef NDEBUG
    if (the_type_of__hitbox_manager_to__allocate
            >= Hitbox_Manager_Type__Unknown) {
        debug_error("allocate_hitbox_manager_from__hitbox_context, invalid type.");
        return 0;
    }
#endif

    Serialization_Header *p_allocation = 
        allocate_serialization_header_with__this_uuid(
                (Serialization_Header *)p_hitbox_context
                    ->hitbox_manager_instances, 
                MAX_QUANTITY_OF__HITBOX_MANAGERS, 
                uuid_of__hitbox_manager__u32);

    if (!p_allocation) {
        debug_error("allocate_hitbox_manager_from__hitbox_context, maximum quantity of managers reached.");
        return 0;
    }

    Hitbox_Manager_Instance *p_hitbox_manager_instance =
        (Hitbox_Manager_Instance*)p_allocation;

    f_Hitbox_Manager__Allocator f_hitbox_manager__allocator_selected =
        p_hitbox_context->hitbox_manager_instance__invocation_table[
            the_type_of__hitbox_manager_to__allocate]
                .f_hitbox_manager__allocator;
    f_Hitbox_Manager__Deallocator f_hitbox_manager__deallocator_selected =
        p_hitbox_context->hitbox_manager_instance__invocation_table[
            the_type_of__hitbox_manager_to__allocate]
                .f_hitbox_manager__deallocator;

    if (!f_hitbox_manager__allocator_selected) {
        debug_error("allocate_hitbox_manager_from__hitbox_context, allocator function is null.");
        return 0;
    }

    void *pVM_hitbox_manager =
        f_hitbox_manager__allocator_selected(
                the_type_of__hitbox_manager_to__allocate,
                quantity_of__hitboxes_to__pool);

    if (!pVM_hitbox_manager) {
        debug_error("allocate_hitbox_manager_from__hitbox_context, failed to dynamically allocate hitbox manager.");
        return 0;
    }

    Hitbox_Manager_Intrinsic *p_hitbox_manager_instrinsic =
        (Hitbox_Manager_Intrinsic*)pVM_hitbox_manager;

#ifndef NDEBUG
    // Validate the type layout of the manager.
    // We expect the first 32bits to be a quantity specifier.
    Quantity__u32 quantity_specifier__u32 = 
        p_hitbox_manager_instrinsic->quantity_of__hitboxes;

    if (quantity_of__hitboxes_to__pool != quantity_specifier__u32) {
        debug_error("allocate_hitbox_manager_from__hitbox_context, bad allocator - pooled quantity does not match.");
        f_hitbox_manager__deallocator_selected(
                pVM_hitbox_manager,
                the_type_of__hitbox_manager_to__allocate);
        return 0;
    }

    // Next we expect a serialization header range of the specified quantity.
    Serialization_Header *p_serialization_header_array =
        p_hitbox_manager_instrinsic->p_array_of__hitboxes;

    if (!is_serialized_struct__deallocated(
                p_serialization_header_array)) {
        debug_error("allocate_hitbox_manager_from__hitbox_context, bad allocator - serialized array begin.");
        f_hitbox_manager__deallocator_selected(
                pVM_hitbox_manager,
                the_type_of__hitbox_manager_to__allocate);
        return 0;
    }
#endif

    initialize_hitbox_manager_instance_as__allocated(
            p_hitbox_manager_instance, 
            pVM_hitbox_manager, 
            uuid_of__hitbox_manager__u32, 
            the_type_of__hitbox_manager_to__allocate);

    return p_hitbox_manager_instance;
}

void *allocate_pV_hitbox_from__hitbox_context(
        Hitbox_Context *p_hitbox_context,
        Identifier__u32 uuid_of__hitbox_manager__u32,
        Identifier__u32 uuid_of__hitbox__u32) {
    Hitbox_Manager_Instance *p_hitbox_manager_instance =
        get_p_hitbox_manager_instance_using__uuid_from__hitbox_context(
                p_hitbox_context, 
                uuid_of__hitbox_manager__u32);

    if (!is_p_hitbox_manager_instance__valid(
                p_hitbox_manager_instance)) {
        debug_error("allocate_pV_hitbox_from__hitbox_context, p_hitbox_manager_instance is invalid.");
        return 0;
    }

    Hitbox_Manager_Intrinsic *p_hitbox_manager_instrinsic =
        (Hitbox_Manager_Intrinsic*)
        p_hitbox_manager_instance->pVM_hitbox_manager;
    
    Serialization_Header *array_of__serialization_headers =
        p_hitbox_manager_instrinsic->p_array_of__hitboxes;

    Serialization_Header *pV_hitbox =
        allocate_serialization_header_with__this_uuid(
                array_of__serialization_headers, 
                p_hitbox_manager_instrinsic->quantity_of__hitboxes, 
                uuid_of__hitbox__u32);

    if (!pV_hitbox) {
        debug_error("allocate_pV_hitbox_from__hitbox_context, failed to allocate hitbox.");
        return 0;
    }

    return pV_hitbox;
}

static inline
Quantity__u32 get_max_quantity_of__hitboxes_in__this_hitbox_manager(
        void *pM_hitbox_manager) {
    return *((Quantity__u32*)pM_hitbox_manager);
}

static inline
void *get_pV_hitbox_from__this_hitbox_manager_in__hitbox_context(
        Hitbox_Context *p_hitbox_context,
        void *pV_hitbox_manager,
        Identifier__u32 uuid_of__hitbox__u32) {
    Hitbox_Manager_Intrinsic *p_hitbox_manager_instrinsic=
        (Hitbox_Manager_Intrinsic*)pV_hitbox_manager;

    return dehash_identitier_u32_in__contigious_array(
            (Serialization_Header*)p_hitbox_manager_instrinsic->p_array_of__hitboxes, 
            get_max_quantity_of__hitboxes_in__this_hitbox_manager(
                pV_hitbox_manager), 
            uuid_of__hitbox__u32);
}


bool opaque_access_to__hitbox(
        Hitbox_Context *p_hitbox_context,
        Identifier__u32 uuid_of__hitbox_manager__u32,
        Identifier__u32 uuid_of__hitbox__u32,
        void *pV_OPTIONAL_dimensions,
        void *pV_OPTIONAL_position,
        void *pV_OPTIONAL_velocity,
        void *pV_OPTIONAL_acceleration,
        Hitbox_Flags__u8 *p_OPTIONAL_hitbox_flags__u8,
        bool is_setting_or__getting) {
    Hitbox_Manager_Instance *p_hitbox_manager_instance =
        get_p_hitbox_manager_instance_using__uuid_from__hitbox_context(
                p_hitbox_context, 
                uuid_of__hitbox_manager__u32);
    if (!p_hitbox_manager_instance) {
        debug_error("get_ptrs_to_properties_of__hitbox, could not dehash hitbox manager uuid.");
        return false;
    }
    void *pV_hitbox = 
        get_pV_hitbox_from__this_hitbox_manager_in__hitbox_context(
                p_hitbox_context, 
                p_hitbox_manager_instance->pVM_hitbox_manager, 
                uuid_of__hitbox__u32);

    if (!pV_hitbox) {
        debug_error("get_ptrs_to_properties_of__hitbox, failed to dehash hitbox uuid.");
        return false;
    }

    p_hitbox_context->hitbox_manager_instance__invocation_table[
        p_hitbox_manager_instance->type_of__hitbox_manager]
            .f_hitbox_manager__get_properties_of__hitbox(
                    pV_hitbox,
                    pV_OPTIONAL_dimensions,
                    pV_OPTIONAL_position,
                    pV_OPTIONAL_velocity,
                    pV_OPTIONAL_acceleration,
                    p_OPTIONAL_hitbox_flags__u8,
                    is_setting_or__getting);

    return true;
}

///
/// Returns an invalid Hitbox_Manager_Instance when failing to find.
///
/// Reports no error upon failure to find.
///
Hitbox_Manager_Instance 
*get_p_hitbox_manager_instance_using__uuid_from__hitbox_context(
        Hitbox_Context *p_hitbox_context,
        Identifier__u32 uuid_of__hitbox_manager__u32) {
    return (Hitbox_Manager_Instance*)dehash_identitier_u32_in__contigious_array(
                (Serialization_Header *)p_hitbox_context
                    ->hitbox_manager_instances, 
                MAX_QUANTITY_OF__HITBOX_MANAGERS, 
                uuid_of__hitbox_manager__u32);
}

Quantity__u32 get_max_quantity_of__hitboxes_in__hitbox_manager(
        Hitbox_Context *p_hitbox_context,
        Identifier__u32 uuid_of__hitbox_manager__u32) {
    Hitbox_Manager_Instance *p_hitbox_manager_instance =
        get_p_hitbox_manager_instance_using__uuid_from__hitbox_context(
                p_hitbox_context, 
                uuid_of__hitbox_manager__u32);
    if (!is_p_hitbox_manager_instance__valid(p_hitbox_manager_instance)) {
        debug_warning("Returning 0 here.");
        debug_error("get_max_quantity_of__hitboxes_in__hitbox_manager, failed to dehash uuid of hitbox manager.");
        return 0;
    }
    return get_max_quantity_of__hitboxes_in__this_hitbox_manager(
            p_hitbox_manager_instance->pVM_hitbox_manager);
}

void *get_pV_hitbox_from__hitbox_context(
        Hitbox_Context *p_hitbox_context,
        Identifier__u32 uuid_of__hitbox_manager__u32,
        Identifier__u32 uuid_of__hitbox__u32) {
    Hitbox_Manager_Instance *p_hitbox_manager_instance =
        get_p_hitbox_manager_instance_using__uuid_from__hitbox_context(
                p_hitbox_context, 
                uuid_of__hitbox_manager__u32);

    if (!p_hitbox_manager_instance) {
        debug_error("get_pV_hitbox_from__hitbox_context, failed to dehash uuid.");
        return 0;
    }

    Serialization_Header *p_serialization_header =
        (Serialization_Header*)p_hitbox_manager_instance->pVM_hitbox_manager;

    return dehash_identitier_u32_in__contigious_array(
            p_serialization_header, 
            get_max_quantity_of__hitboxes_in__this_hitbox_manager(
                p_hitbox_manager_instance->pVM_hitbox_manager), 
            uuid_of__hitbox__u32);
}

void release_hitbox_manager_from__hitbox_context(
        Hitbox_Context *p_hitbox_context,
        Identifier__u32 uuid_of__hitbox_manager__u32) {
    Hitbox_Manager_Instance *p_hitbox_manager_instance =
        get_p_hitbox_manager_instance_using__uuid_from__hitbox_context(
                p_hitbox_context, 
                uuid_of__hitbox_manager__u32);

    if (!p_hitbox_manager_instance) {
        debug_error("release_hitbox_manager_from__hitbox_context, p_hitbox_manager_instance == 0.");
        return;
    }

    f_Hitbox_Manager__Deallocator f_hitbox_manager__deallocator_selected =
        p_hitbox_context->hitbox_manager_instance__invocation_table[
            p_hitbox_manager_instance->type_of__hitbox_manager]
                .f_hitbox_manager__deallocator;

    if (!f_hitbox_manager__deallocator_selected) {
        debug_error("release_hitbox_manager_from__hitbox_context, deallocator function is null.");
        debug_warning("Blindly freeing! Memory could be leaked!");

        free(p_hitbox_manager_instance->pVM_hitbox_manager);
        initialize_hitbox_manager_instance_as__deallocated(
                p_hitbox_manager_instance);
        return;
    }

    f_hitbox_manager__deallocator_selected(
            p_hitbox_manager_instance->pVM_hitbox_manager,
            p_hitbox_manager_instance->type_of__hitbox_manager);
    initialize_hitbox_manager_instance_as__deallocated(
            p_hitbox_manager_instance);
}

///
/// Returns null ptr when failing to find.
///
/// [ ------- ] Reports no error upon failure to find.
/// [ !NDEBUG ] Reports an error upon invalid type found.
///
Hitbox_AABB_Manager *get_p_hitbox_aabb_manager_from__hitbox_context(
        Hitbox_Context *p_hitbox_context,
        Identifier__u32 uuid_of__hitbox_manager__u32) {
    Hitbox_Manager_Instance *p_hitbox_manager_instance =
        get_p_hitbox_manager_instance_using__uuid_from__hitbox_context(
                p_hitbox_context, 
                uuid_of__hitbox_manager__u32);

    if (!p_hitbox_manager_instance)
        return 0;

#ifndef NDEBUG
    if (Hitbox_Manager_Type__AABB 
            != p_hitbox_manager_instance->type_of__hitbox_manager) {
        debug_error("get_p_hitbox_aabb_manager_from__hitbox_context, invalid cast.");
        return 0;
    }
#endif

    return (Hitbox_AABB_Manager*)p_hitbox_manager_instance->pVM_hitbox_manager;
}

