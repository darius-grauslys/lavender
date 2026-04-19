#include "game_action/core/hitbox/game_action__hitbox.h"
#include "collisions/collision_node.h"
#include "collisions/hitbox_context.h"
#include "defines.h"
#include "defines_weak.h"
#include "game.h"
#include "game_action/game_action_logic_entry.h"
#include "game_action/game_action_logic_table.h"
#include "collisions/core/aabb/hitbox_aabb_manager.h"
#include "collisions/core/aabb/hitbox_aabb.h"
#include "process/process.h"
#include "types/implemented/game_action_kind.h"
#include "types/implemented/hitbox_kind.h"
#include "vectors.h"
#include "world/chunk_vectors.h"
#include "world/global_space.h"
#include "world/global_space_manager.h"
#include "world/world.h"
#include "game_action/types/core/collisions/aabb/ga_types__aabb.h"

void m_process__game_action__hitbox(
        Process *p_this_process,
        Game *p_game) {
    Game_Action *p_game_action =
        (Game_Action*)p_this_process->p_process_data;


    void *pV_hitbox =
        get_pV_hitbox_from__hitbox_context(
                get_p_hitbox_context_from__game(p_game), 
                GET_UUID_P(get_p_world_from__game(p_game)),
                p_game_action->ga_kind__hitbox__uuid_of__target);

    if (!pV_hitbox) {
        debug_error("m_process__game_action__hitbox, pV_hitbox == 0.");
        fail_process(p_this_process);
        return;
    }

    Hitbox_Kind the_kind_of__hitbox =
        p_game_action->ga_kind__hitbox__the_kind_of__hitbox;

    Vector__3i32F4 position_of__hitbox__3i32F4 = 
        p_game_action->ga_kind__hitbox__position__3i32F4;
    Vector__3i32F4 velocity_of__hitbox__3i32F4 = 
        p_game_action->ga_kind__hitbox__velocity__3i32F4;
    Vector__3i16F8 acceleration_of__hitbox__3i16F8 = 
        p_game_action->ga_kind__hitbox__acceleration__3i16F8;

    Vector__3i32F4 position_OLD_of__hitbox__3i32F4;

#warning TODO(tech-debt): this should be broken up into their own actions
    switch (the_kind_of__hitbox) {
        case Hitbox_Kind__Opaque:
        default:
            opaque_access_to__hitbox(
                    get_p_hitbox_context_from__game(p_game), 
                    GET_UUID_P(get_p_world_from__game(p_game)), 
                    p_game_action->ga_kind__hitbox__uuid_of__target, 
                    0, 
                    &position_OLD_of__hitbox__3i32F4,
                    0,
                    0,
                    0,
                    OPAQUE_HITBOX_ACCESS__GET);

            opaque_access_to__hitbox(
                    get_p_hitbox_context_from__game(p_game), 
                    GET_UUID_P(get_p_world_from__game(p_game)), 
                    p_game_action->ga_kind__hitbox__uuid_of__target, 
                    0, 
                    &position_of__hitbox__3i32F4,
                    &velocity_of__hitbox__3i32F4,
                    &acceleration_of__hitbox__3i16F8,
                    0,
                    OPAQUE_HITBOX_ACCESS__SET);
            break;
        case Hitbox_Kind__AABB:
            ;
            Hitbox_AABB *p_hitbox_aabb =
                (Hitbox_AABB*)pV_hitbox;
            position_OLD_of__hitbox__3i32F4 =
                get_position_3i32F4_of__hitbox_aabb(
                        p_hitbox_aabb);
            set_hitbox_aabb__position_with__3i32F4(
                    p_hitbox_aabb, 
                    p_game_action->ga_kind__hitbox__position__3i32F4);
            set_velocity_to__hitbox_aabb(
                    p_hitbox_aabb, 
                    p_game_action->ga_kind__hitbox__velocity__3i32F4);
            set_acceleration_to__hitbox_aabb(
                    p_hitbox_aabb, 
                    p_game_action->ga_kind__hitbox__acceleration__3i16F8);
            break;
    }

    poll_for_collision_node_update(
            p_game, 
            position_OLD_of__hitbox__3i32F4, 
            p_game_action->ga_kind__hitbox__position__3i32F4, 
            p_game_action->ga_kind__hitbox__uuid_of__target);

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
        Vector__3i32F4 velocity__3i32F4,
        Vector__3i16F8 acceleration__3i16F8,
        Hitbox_Kind the_kind_of__hitbox) {
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
    p_game_action->ga_kind__hitbox__acceleration__3i16F8 =
        acceleration__3i16F8;
    p_game_action->ga_kind__hitbox__the_kind_of__hitbox =
        the_kind_of__hitbox;
}
