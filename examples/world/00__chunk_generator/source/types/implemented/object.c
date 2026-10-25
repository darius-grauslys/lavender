#include "client.h"
#include "collisions/hitbox.h"
#include "defines.h"
#include "entity/entity.h"
#include <types/implemented/object.h>

///
/// Warning: removing the const specifier is a serious security risk.
/// TODO: add a engine_config macro to limit the possible overflow
/// if the last entry is somehow not null terminating.
///

const f_Object_Handler array_of__object_handlers__activate_object[] = {
    f_object_handler__hitbox__activate,
    f_object_handler__entity__activate,
    f_object_handler__client__activate,
    0
};

const f_Object_Handler array_of__object_handlers__deactivate_object[] = {
    f_object_handler__hitbox__deactivate,
    f_object_handler__entity__deactivate,
    f_object_handler__client__deactivate,
    0
};

const f_Object_Handler array_of__object_handlers__pre_teleport_object[] = {
    f_object_handler__hitbox__deactivate,
    f_object_handler__entity__deactivate,
    f_object_handler__client__deactivate,
    0
};

const f_Object_Handler array_of__object_handlers__post_teleport_object[] = {
    0
};
