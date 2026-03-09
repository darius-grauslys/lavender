#include "collisions/hitbox_manager_instance.h"
#include "defines.h"
#include "serialization/serialization_header.h"

void initialize_hitbox_manager_instance_as__deallocated(
        Hitbox_Manager_Instance *p_hitbox_manager_instance) {
    memset(p_hitbox_manager_instance, 0, sizeof(Hitbox_Manager_Instance));
    initialize_serialization_header_for__deallocated_struct(
            &p_hitbox_manager_instance->_serialization_header, 
            sizeof(Hitbox_Manager_Instance));
}

void initialize_hitbox_manager_instance_as__allocated(
        Hitbox_Manager_Instance *p_hitbox_manager_instance,
        void *pM_hitbox_manager,
        Identifier__u32 uuid_of__hitbox_manager__u32,
        Hitbox_Manager_Type the_type_of__hitbox_manager__allocated) {
    initialize_serialization_header(
            &p_hitbox_manager_instance->_serialization_header, 
            uuid_of__hitbox_manager__u32, 
            sizeof(Hitbox_Manager_Instance));
    p_hitbox_manager_instance->type_of__hitbox_manager =
        the_type_of__hitbox_manager__allocated;
    p_hitbox_manager_instance->pM_hitbox_manager =
        pM_hitbox_manager;
}

