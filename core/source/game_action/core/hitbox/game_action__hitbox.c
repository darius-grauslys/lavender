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

#error TODO: impl hitbox resolver look up table with:
    // p_game_action->ga_kind__hitbox__the_kind_of__hitbox;

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
        Vector__3i16F8 acceleration__3i16F8) {
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
}
