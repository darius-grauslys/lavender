#ifndef IMPL_HITBOX_MANAGER_TYPE_H
#define IMPL_HITBOX_MANAGER_TYPE_H

#define DEFINE_HITBOX_MANAGER_TYPE
///
/// ALL PRESENT TYPES ARE REQUIRED BY CORE!
/// AABB - UI, 2d physics (you 99.9% of the time need this unless you're making something pretty niche.)
/// AAABBB - 3d physics (feel free to omit if not using)
///
/// Feel free to reassign what is default, CORE does not assume what is default
/// and relies on types explicitly.
///
typedef enum Hitbox_Manager_Type_t {
    Hitbox_Manager_Type__Default,
    Hitbox_Manager_Type__AABB = Hitbox_Manager_Type__Default,
    Hitbox_Manager_Type__AAABBB,
    Hitbox_Manager_Type__Unknown
} Hitbox_Manager_Type;

#endif
