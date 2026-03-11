#ifndef HITBOX_MANAGER_INSTANCE_H
#define HITBOX_MANAGER_INSTANCE_H

#include "defines.h"
#include "defines_weak.h"
#include "serialization/identifiers.h"

void initialize_hitbox_manager_instance_as__deallocated(
        Hitbox_Manager_Instance *p_hitbox_manager_instance);

void initialize_hitbox_manager_instance_as__allocated(
        Hitbox_Manager_Instance *p_hitbox_manager_instance,
        void *pM_hitbox_manager,
        Identifier__u32 uuid_of__hitbox_manager__u32,
        Hitbox_Manager_Type the_type_of__hitbox_manager__allocated);

static inline
bool is_p_hitbox_manager_instance__valid(
        Hitbox_Manager_Instance *p_hitbox_manager_instance) {
    return 
        p_hitbox_manager_instance
        && !is_identifier_u32__invalid(p_hitbox_manager_instance
                ->_serialization_header.uuid)
        && p_hitbox_manager_instance->pVM_hitbox_manager != 0
        ;
}

#endif
