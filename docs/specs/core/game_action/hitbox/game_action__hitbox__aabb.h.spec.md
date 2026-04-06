# 1. Specification: core/include/game_action/core/hitbox/game_action__hitbox__aabb.h

## 1.1. Overview

Contains the inline implementation of `m_process__game_action__hitbox__aabb`,
the process handler for AABB hitbox game actions. This handler is registered
in the `Game_Action_Logic_Table` for `Game_Action_Kind__Hitbox__Set_Position`
and executes the actual hitbox update with collision node migration.

**Note**: This file contains an inline function definition in a header,
which means it is compiled into every translation unit that includes it.

## 1.2. Dependencies

- `defines.h` (for all struct types)
- `collisions/core/aabb/hitbox_aabb.h` (for hitbox accessors and setters)
- `collisions/core/aabb/hitbox_aabb_manager.h` (for UUID lookup)
- `collisions/hitbox_context.h` (for manager instance lookup)
- `game.h` (for `get_p_world_from__game`, `get_p_hitbox_context_from__game`)
- `process/process.h` (for `fail_process`, `complete_process`)

## 1.3. Functions

### 1.3.1. Process Handler

| Function | Signature | Description |
|----------|-----------|-------------|
| `m_process__game_action__hitbox__aabb` | `(Process*, Game*) -> void` | Inline `m_Process` handler for AABB hitbox updates. |

### 1.3.2. Implementation Steps

1. Extract `Game_Action*` from `p_this_process->p_process_data`.
2. Get the `World*` from `Game`.
3. Get the `Hitbox_AABB_Manager*` from the `Hitbox_Context` using the
   world's UUID.
4. Look up the target `Hitbox_AABB` by
   `ga_kind__hitbox__uuid_of__target`.
5. Save the old position.
6. Set new position via `set_hitbox_aabb__position_with__3i32F4`.
7. Set new velocity via `set_velocity_to__hitbox_aabb`.
8. Set new acceleration via `set_acceleration_to__hitbox_aabb`.
9. Call `poll_for_collision_node_update` with old and new positions.
10. Complete or fail the process.

## 1.4. Agentic Workflow

### 1.4.1. When to use

- Do not call this function directly. It is registered as the `m_Process`
  handler for hitbox game actions via `register_game_action__hitbox_for__server`.

### 1.4.2. Preconditions

- `p_this_process->p_process_data` must point to a valid `Game_Action`.
- The world must be loaded with a valid `Hitbox_AABB_Manager`.
- The target hitbox UUID must exist in the manager.

### 1.4.3. Error Handling

- Null hitbox manager: `debug_error` + `fail_process`.
- Failed collision node update: `debug_error` + `fail_process`.
