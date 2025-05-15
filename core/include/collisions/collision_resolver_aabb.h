#ifndef COLLISION_RESOLVER_AABB_H
#define COLLISION_RESOLVER_AABB_H

#include "defines.h"

void f_hitbox_aabb_collision_handler__default(
        Game *p_game,
        World *p_world,
        Hitbox_AABB *p_hitbox_aabb__colliding,
        Hitbox_AABB *p_hitbox_aabb__collided);

void f_hitbox_aabb_tile_touch_handler__default(
        Game *p_game,
        World *p_world,
        Hitbox_AABB *p_hitbox_aabb,
        Tile *p_tile,
        Signed_Index__i32 x_collision__i32,
        Signed_Index__i32 y_collision__i32);

void poll_collision_resolver_aabb(
        Game *p_game,
        Hitbox_AABB_Manager *p_hitbox_aabb_manager,
        f_Hitbox_AABB_Collision_Handler f_hitbox_aabb_collision_handler,
        f_Hitbox_AABB_Tile_Touch_Handler f_hitbox_aabb_tile_touch_handler);

void poll_hitbox_aabb_for__tile_collision(
        Game *p_game,
        Local_Space_Manager *p_local_space_manager,
        Hitbox_AABB *p_hitbox_aabb,
        f_Hitbox_AABB_Tile_Touch_Handler f_hitbox_aabb_tile_touch_handler);

#endif
