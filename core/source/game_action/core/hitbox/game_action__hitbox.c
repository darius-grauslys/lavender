#include "game_action/core/hitbox/game_action__hitbox.h"
#include "collisions/collision_node.h"
#include "defines.h"
#include "defines_weak.h"
#include "game.h"
#include "game_action/game_action_logic_entry.h"
#include "game_action/game_action_logic_table.h"
#include "collisions/hitbox_aabb_manager.h"
#include "collisions/hitbox_aabb.h"
#include "process/process.h"
#include "types/implemented/game_action_kind.h"
#include "vectors.h"
#include "world/chunk_vectors.h"
#include "world/global_space.h"
#include "world/global_space_manager.h"
#include "world/world.h"

void m_process__game_action__hitbox(
        Process *p_this_process,
        Game *p_game) {
    Game_Action *p_game_action =
        (Game_Action*)p_this_process->p_process_data;
    Hitbox_AABB *p_hitbox_aabb = 
        get_p_hitbox_aabb_by__uuid_u32_from__hitbox_aabb_manager(
                get_p_hitbox_aabb_manager_from__game(p_game), 
                p_game_action
                ->ga_kind__hitbox__uuid_of__target);

    if (!p_hitbox_aabb) {
        debug_error("m_process__game_action__hitbox, invalid uuid target. Lacks hitbox component.");
        fail_process(p_this_process);
        return;
    }

    Chunk_Vector__3i32 gsv__old__3i32 =
        vector_3i32F4_to__chunk_vector_3i32(
                get_position_3i32F4_of__hitbox_aabb(
                    p_hitbox_aabb));

    set_hitbox__position_with__3i32F4(
            p_hitbox_aabb, 
            p_game_action
            ->ga_kind__hitbox__position__3i32F4);
    set_velocity_to__hitbox(
            p_hitbox_aabb, 
            p_game_action
            ->ga_kind__hitbox__velocity__3i32F4);

    Chunk_Vector__3i32 gsv__current__3i32 =
                vector_3i32F4_to__chunk_vector_3i32(
                    get_position_3i32F4_of__hitbox_aabb(
                        p_hitbox_aabb));

    if (!is_chunk_vectors_3i32__equal(
                gsv__old__3i32, 
                gsv__current__3i32)) {
        Global_Space *p_global_space__old =
            get_p_global_space_from__global_space_manager(
                    get_p_global_space_manager_from__game(
                        p_game), 
                    gsv__old__3i32);
        if (!p_global_space__old) {
            debug_error("m_process__game_action__hitbox, p_global_space__old == 0.");
            fail_process(p_this_process);
            return;
        }
        remove_entry_from__collision_node(
                get_p_collision_node_pool_from__world(
                    get_p_world_from__game(p_game)), 
                get_p_collision_node_from__global_space(
                    p_global_space__old), 
                GET_UUID_P(p_hitbox_aabb));
        Global_Space *p_global_space__new =
            get_p_global_space_from__global_space_manager(
                    get_p_global_space_manager_from__game(
                        p_game), 
                    gsv__current__3i32);
        if (!p_global_space__new) {
            debug_error("m_process__game_action__hitbox, p_global_space__new == 0.");
            fail_process(p_this_process);
            return;
        }
        add_entry_to__collision_node(
                get_p_collision_node_pool_from__world(
                    get_p_world_from__game(
                        p_game)), 
                get_p_collision_node_from__global_space(
                    p_global_space__new), 
                p_hitbox_aabb);
    }
    complete_process(p_this_process);
}

void register_game_action__hitbox_for__server(
        Game_Action_Logic_Table *p_game_action_logic_table) {
    initialize_game_action_logic_entry(
            get_p_game_action_logic_entry_by__game_action_kind(
                p_game_action_logic_table, 
                Game_Action_Kind__Hitbox), 
            GAME_ACTION_FLAGS__OUTBOUND_SANITIZE
            | GAME_ACTION_FLAGS__BIT_IS_PROCESSED_ON_INVOCATION_OR_RESPONSE,
            GAME_ACTION_FLAG_MASK__OUTBOUND_SANITIZE,
            GAME_ACTION_FLAGS__INBOUND_SANITIZE,
            GAME_ACTION_FLAG_MASK__INBOUND_SANITIZE,
            PROCESS_PRIORITY__0_MAXIMUM,
            m_process__game_action__hitbox, 
            PROCESS_FLAG__IS_CRITICAL,
            0, 
            0);
}

void register_game_action__hitbox_for__client(
        Game_Action_Logic_Table *p_game_action_logic_table) {
    initialize_game_action_logic_entry(
            get_p_game_action_logic_entry_by__game_action_kind(
                p_game_action_logic_table, 
                Game_Action_Kind__Hitbox), 
            GAME_ACTION_FLAGS__OUTBOUND_SANITIZE,
            GAME_ACTION_FLAG_MASK__OUTBOUND_SANITIZE,
            GAME_ACTION_FLAGS__INBOUND_SANITIZE
            | GAME_ACTION_FLAGS__BIT_IS_PROCESSED_ON_INVOCATION_OR_RESPONSE,
            GAME_ACTION_FLAG_MASK__INBOUND_SANITIZE,
            PROCESS_PRIORITY__0_MAXIMUM,
            0, 
            0,
            m_process__game_action__hitbox, 
            PROCESS_FLAG__IS_CRITICAL);
}

void initialize_game_action_for__hitbox(
        Game_Action *p_game_action,
        Identifier__u32 uuid_of__target__u32,
        Vector__3i32F4 position__3i32F4,
        Vector__3i32F4 velocity__3i32F4) {
    initialize_game_action(p_game_action);
    set_the_kind_of__game_action(
            p_game_action, 
            Game_Action_Kind__Hitbox);
    p_game_action->ga_kind__hitbox__uuid_of__target =
        uuid_of__target__u32;
    p_game_action->ga_kind__hitbox__position__3i32F4 =
        position__3i32F4;
    p_game_action->ga_kind__hitbox__velocity__3i32F4 = 
        velocity__3i32F4;
}
