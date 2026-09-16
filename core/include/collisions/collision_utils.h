#ifndef COLLISION_UTILS_H
#define COLLISION_UTILS_H

/*
 * This module defines various utility functions of cross cutting concerns
 * for mutliple modules, with the main focus being arbitrary UUID component
 * bearing objects possessing a hitbox component.
 */

#include "defines_weak.h"

void attach_object_to__collision_system(
        Game *p_game,
        World *p_world,
        Identifier__u32 uuid__u32);

void detach_object_from__collision_system(
        Game *p_game,
        World *p_world,
        Identifier__u32 uuid__u32);

#endif
