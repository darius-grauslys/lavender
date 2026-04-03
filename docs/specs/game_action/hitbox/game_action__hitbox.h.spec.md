# Specification: core/include/game_action/core/hitbox/game_action__hitbox.h

## Overview

Provides initialization, registration, and dispatch for hitbox-related
game actions (`Game_Action_Kind__Hitbox__Set_Position`). This is the
**correct** way to update a hitbox's position, velocity, and acceleration
for entities registered in the collision system, as it ensures collision
node consistency.

## Dependencies

- `defines.h` (for `Game_Action`, `Game_Action_Logic_Table`,
  `Vector__3i32F4`, `Vector__3i16F8`, `Hitbox_Kind`)
- `game.h` (for `dispatch_game_action_to__server`)
- `collisions/core/aabb/hitbox_aabb.h` (for hitbox types)
- `collisions/hitbox_context.h` (for hitbox context access)
- `types/implemented/hitbox_kind.h` (for `Hitbox_Kind` enum)

## Game_Action_Kind

`Game_Action_Kind__Hitbox__Set_Position`

## Payload Fields

| Field | Type | Description |
|-------|------|-------------|
| `ga_kind__hitbox__uuid_of__target` | `Identifier__u32` | UUID of the hitbox to update. |
| `ga_kind__hitbox__position__3i32F4` | `Vector__3i32F4` | New position. |
| `ga_kind__hitbox__velocity__3i32F4` | `Vector__3i32F4` | New velocity. |
| `ga_kind__hitbox__acceleration__3i16F8` | `Vector__3i16F8` | New acceleration. |
| `ga_kind__hitbox__the_kind_of__hitbox` | `Hitbox_Kind` | Discriminator for the hitbox type (e.g. `Hitbox_Kind__AABB`). |

## Functions

### Registration

| Function | Signature | Description |
|----------|-----------|-------------|
| `register_game_action__hitbox_for__server` | `(Game_Action_Logic_Table*) -> void` | Registers the hitbox action for server-side processing. |
| `register_game_action__hitbox_for__offline` | `(Game_Action_Logic_Table*) -> void` | Delegates to `register_game_action__hitbox_for__server`. (static inline) |
| `register_game_action__hitbox_for__client` | `(Game_Action_Logic_Table*) -> void` | Registers the hitbox action for client-side processing. |

### Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_game_action_for__hitbox` | `(Game_Action*, Identifier__u32 target_uuid, Vector__3i32F4 position, Vector__3i32F4 velocity, Vector__3i16F8 acceleration, Hitbox_Kind kind) -> void` | Initializes a hitbox update action with all kinematic properties. |

### Dispatch (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `dispatch_game_action__hitbox` | `(Game*, Identifier__u32 target_uuid, Vector__3i32F4 position, Vector__3i32F4 velocity, Vector__3i16F8 acceleration, Hitbox_Kind kind) -> bool` | `bool` | Creates and dispatches a hitbox update to the server. |

## Agentic Workflow

### Why Use Game Actions for Hitbox Updates

Directly calling `set_hitbox_aabb__position_with__3i32F4` on a hitbox
that is registered in the collision system will **not** update its
`Collision_Node_Entry`. This causes the hitbox to become invisible to
the collision resolver.

`dispatch_game_action__hitbox` ensures:
1. The hitbox position, velocity, and acceleration are updated.
2. The collision node entry is migrated if the hitbox crossed a chunk boundary.

### Process Handler

The AABB variant (`m_process__game_action__hitbox__aabb` in
`game_action__hitbox__aabb.h`) performs:

1. Looks up the `Hitbox_AABB_Manager` from the world's hitbox context.
2. Finds the target `Hitbox_AABB` by UUID.
3. Saves the old position.
4. Sets the new position, velocity, and acceleration.
5. Calls `poll_for_collision_node_update` to migrate the collision node
   entry if needed.
6. Completes or fails the process based on the result.

### Preconditions

- The target hitbox UUID must exist in the active `Hitbox_AABB_Manager`.
- The world must be loaded and have a valid hitbox context.

### Postconditions

- The hitbox's kinematic properties are updated.
- The collision node entry is consistent with the new position.

### Error Handling

- If the hitbox manager is null, the process fails with `debug_error`.
- If the collision node update fails, the process fails with `debug_error`.
