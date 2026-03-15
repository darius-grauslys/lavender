#ifndef GAME_ACTION__HITBOX__AABB
#define GAME_ACTION__HITBOX__AABB

#include "collisions/core/aabb/hitbox_aabb.h"
#include "collisions/core/aabb/hitbox_aabb_manager.h"
#include "defines.h"
#include "defines_weak.h"
#include "game.h"
#include "collisions/hitbox_context.h"
#include "process/process.h"

void m_process__game_action__hitbox__aabb(
        Process *p_this_process,
        Game *p_game) {
    //
    // We are assuming the hitbox given to us is AABB!
    //

    Game_Action *p_game_action = 
        (Game_Action*)p_this_process->p_process_data;
    World *p_world = get_p_world_from__game(p_game);
    void *pV_hitbox_manager =
        get_p_hitbox_manager_instance_using__uuid_from__hitbox_context(
                get_p_hitbox_context_from__game(p_game), 
                GET_UUID_P(p_world));
    Hitbox_AABB_Manager *p_hitbox_aabb_manager =
        (Hitbox_AABB_Manager*)pV_hitbox_manager;

#ifndef NDEBUG
    if (!p_hitbox_aabb_manager) {
        debug_error( "m_process__game_action__hitbox__aabb, p_hitbox_manager == 0." );
        fail_process(p_this_process);
        return;
    }
#endif

    Hitbox_AABB *p_hitbox_aabb =
        get_p_hitbox_aabb_by__uuid_u32_from__hitbox_aabb_manager(
                p_hitbox_aabb_manager,
                p_game_action
                ->ga_kind__hitbox__uuid_of__target);

    Vector__3i32F4 position_old__3i32F4 =
        get_position_3i32F4_of__hitbox_aabb(
                p_hitbox_aabb);

    set_hitbox_aabb__position_with__3i32F4(
            p_hitbox_aabb, 
            p_game_action
            ->ga_kind__hitbox__position__3i32F4);
    set_velocity_to__hitbox_aabb(
            p_hitbox_aabb, 
            p_game_action
            ->ga_kind__hitbox__velocity__3i32F4);
    set_acceleration_to__hitbox_aabb(
            p_hitbox_aabb, 
            p_game_action
            ->ga_kind__hitbox__acceleration__3i16F8);
    
    bool is_successful =
        poll_for_collision_node_update(
                p_game,
                position_old__3i32F4,
                p_game_action
                ->ga_kind__hitbox__position__3i32F4,
                GET_UUID_P(p_hitbox_aabb));

    if (!is_successful) {
        debug_error( "m_process__game_action__hitbox__aabb, failed to update collision node." );
        fail_process(p_this_process);
        return;
    }

    complete_process(p_this_process);
}
#endif
