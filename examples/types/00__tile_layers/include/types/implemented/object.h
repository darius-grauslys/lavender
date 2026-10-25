#ifndef IMPL_OBJECT_H
#define IMPL_OBJECT_H

#include <defines.h>

///
/// The following are function pointer arrays which are null terminated.
/// These function pointer arrays act as callback tables for activating
/// deactivating, and teleporting arbitrary objects.
///
/// Each callback looks up a resource by the provided uuid for existance
/// and assumes that resource is owned by something by that uuid.
/// The corresponding semantic of activation, deactivation, and teleportation
/// are applied.
///
extern const f_Object_Handler array_of__object_handlers__activate_object[];
extern const f_Object_Handler array_of__object_handlers__deactivate_object[];
extern const f_Object_Handler array_of__object_handlers__pre_teleport_object[];
extern const f_Object_Handler array_of__object_handlers__post_teleport_object[];

#endif
