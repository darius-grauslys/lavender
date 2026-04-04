# Specification: core/include/game_action/game_action_manager.h

## Overview

Manages a pool of `Game_Action` instances. Each `Client` has two
`Game_Action_Manager` instances: one for inbound actions and one for outbound
actions. The manager provides allocation, deallocation, lookup, and copy
operations using UUID-based hashing.

## Dependencies

- `defines.h` (for `Game_Action_Manager`, `Game_Action`,
  `MAX_QUANTITY_OF__GAME_ACTIONS`, `Identifier__u32`)
- `serialization/hashing.h` (for `get_next_available__random_uuid_in__contiguous_array`)

## Types

### Game_Action_Manager (struct)

    typedef struct Game_Action_Manager_t {
        Game_Action game_actions[MAX_QUANTITY_OF__GAME_ACTIONS];
        Repeatable_Psuedo_Random repeatable_pseudo_random;
    } Game_Action_Manager;

| Field | Type | Description |
|-------|------|-------------|
| `game_actions` | `Game_Action[512]` | Contiguous pool of game action slots. |
| `repeatable_pseudo_random` | `Repeatable_Psuedo_Random` | Randomizer for UUID generation. |

### Limits

| Macro | Default | Description |
|-------|---------|-------------|
| `MAX_QUANTITY_OF__GAME_ACTIONS` | 512 | Maximum number of game actions per manager. |

## Functions

### Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_game_action_manager` | `(Game_Action_Manager*) -> void` | Initializes all slots as deallocated and seeds the randomizer. |

### Allocation

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `allocate_game_action_with__this_uuid_from__game_action_manager` | `(Game_Action_Manager*, Identifier__u32 uuid) -> Game_Action*` | `Game_Action*` or `NULL` | Allocates a slot with the specified UUID. |
| `allocate_game_action_from__game_action_manager` | `(Game_Action_Manager*) -> Game_Action*` | `Game_Action*` or `NULL` | Generates a random UUID and allocates. (static inline) |
| `allocate_as__copy_of__game_action_with__this_uuid_from__manager` | `(Game_Action_Manager*, Game_Action* source, Identifier__u32 uuid) -> Game_Action*` | `Game_Action*` or `NULL` | Allocates a slot and copies the source action into it. |
| `allocate_as__copy_of__game_action_from__game_action_manager` | `(Game_Action_Manager*, Game_Action* source) -> Game_Action*` | `Game_Action*` or `NULL` | Generates a random UUID and copies. (static inline) |

### Deallocation

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `release_game_action_from__game_action_manager` | `(Game_Action_Manager*, Game_Action*) -> bool` | `bool` | Releases the game action back to the pool. Returns true on success. |

### Lookup

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_p_game_action_by__uuid_from__game_action_manager` | `(Game_Action_Manager*, Identifier__u32) -> Game_Action*` | `Game_Action*` or `NULL` | Finds a game action by UUID. |

## Agentic Workflow

### Ownership Model

Each `Client` owns two `Game_Action_Manager` instances:

    typedef struct Client_t {
        ...
        Game_Action_Manager game_action_manager__inbound;
        Game_Action_Manager game_action_manager__outbound;
        ...
    } Client;

- **Outbound**: Actions dispatched by this client to the server/other clients.
- **Inbound**: Actions received by this client from the server/other clients.

### Allocation Pattern

    // Allocate with random UUID
    Game_Action *p_ga = allocate_game_action_from__game_action_manager(
            &client.game_action_manager__outbound);

    // Or copy an existing action
    Game_Action *p_ga_copy = allocate_as__copy_of__game_action_from__game_action_manager(
            &client.game_action_manager__inbound,
            p_source_game_action);

### Preconditions

- Manager must be initialized before any allocation.
- UUID must not be `IDENTIFIER__UNKNOWN__u32` for explicit UUID allocation.

### Postconditions

- After allocation: the returned `Game_Action` has its serialization header
  UUID set and `is_game_action__allocated` returns true.
- After release: the slot is available for reuse.

### Error Handling

- Allocation returns NULL if the pool is full.
- `release_game_action_from__game_action_manager` returns false on failure.
