#include "collisions/collision_node.h"
#include "defines.h"
#include "world/local_space.h"

void initialize_local_space(
        Local_Space *p_local_space) {
    memset(p_local_space,
            0,
            sizeof(Local_Space));
}

///
/// Examines this local_space, and all 8 neighbors.
///
void poll_for__collisions(
        Game *p_game,
        World *p_world,
        Local_Space *p_local_space,
        f_Hitbox_AABB_Collision_Handler f_hitbox_collision_handler,
        Hitbox_AABB *p_hitbox_aabb) {
    // center
    poll_for__collisions_within_this__collision_node(
            p_game, 
            p_world, 
            get_p_collision_node_from__local_space(p_local_space), 
            f_hitbox_collision_handler, 
            p_hitbox_aabb);

    // NE
    poll_for__collisions_within_this__collision_node(
            p_game, 
            p_world, 
            get_p_collision_node_from__local_space(
                p_local_space
                ->p_local_space__north
                ->p_local_space__east), 
            f_hitbox_collision_handler, 
            p_hitbox_aabb);

    // N
    poll_for__collisions_within_this__collision_node(
            p_game, 
            p_world, 
            get_p_collision_node_from__local_space(
                p_local_space
                ->p_local_space__north),
            f_hitbox_collision_handler, 
            p_hitbox_aabb);

    // NW
    poll_for__collisions_within_this__collision_node(
            p_game, 
            p_world, 
            get_p_collision_node_from__local_space(
                p_local_space
                ->p_local_space__north
                ->p_local_space__west),
            f_hitbox_collision_handler, 
            p_hitbox_aabb);

    // E
    poll_for__collisions_within_this__collision_node(
            p_game, 
            p_world, 
            get_p_collision_node_from__local_space(
                p_local_space
                ->p_local_space__east),
            f_hitbox_collision_handler, 
            p_hitbox_aabb);
    
    // W
    poll_for__collisions_within_this__collision_node(
            p_game, 
            p_world, 
            get_p_collision_node_from__local_space(
                p_local_space
                ->p_local_space__west),
            f_hitbox_collision_handler, 
            p_hitbox_aabb);
    
    // SE
    poll_for__collisions_within_this__collision_node(
            p_game, 
            p_world, 
            get_p_collision_node_from__local_space(
                p_local_space
                ->p_local_space__south
                ->p_local_space__east),
            f_hitbox_collision_handler, 
            p_hitbox_aabb);
    
    // S
    poll_for__collisions_within_this__collision_node(
            p_game, 
            p_world, 
            get_p_collision_node_from__local_space(
                p_local_space
                ->p_local_space__south),
            f_hitbox_collision_handler, 
            p_hitbox_aabb);
    
    // SW
    poll_for__collisions_within_this__collision_node(
            p_game, 
            p_world, 
            get_p_collision_node_from__local_space(
                p_local_space
                ->p_local_space__south
                ->p_local_space__west),
            f_hitbox_collision_handler, 
            p_hitbox_aabb);
}
