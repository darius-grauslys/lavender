# Specification: core/include/random.h

## Overview

Provides a deterministic, repeatable pseudo-random number generator (PRNG)
system. The `Repeatable_Psuedo_Random` struct maintains PRNG state that
can be seeded, queried intrusively (advancing state) or non-intrusively
(without advancing state), and used for reproducible procedural generation.

## Dependencies

- `defines.h` (for `Repeatable_Psuedo_Random`, `Psuedo_Random_Seed__u32`,
  `Psuedo_Random__i32`, `Signed_Index__i32`, `Direction__u8`)

## Types

### Repeatable_Psuedo_Random (struct)

    typedef struct Repeatable_Psuedo_Random_t {
        Psuedo_Random_Seed__u32 seed__initial;
        Psuedo_Random_Seed__u32 seed__current_random;
    } Repeatable_Psuedo_Random;

| Field | Type | Description |
|-------|------|-------------|
| `seed__initial` | `Psuedo_Random_Seed__u32` | The initial seed used to create this PRNG. |
| `seed__current_random` | `Psuedo_Random_Seed__u32` | The current state of the PRNG. |

## Functions

### Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_repeatable_psuedo_random` | `(Repeatable_Psuedo_Random*, Psuedo_Random_Seed__u32 seed) -> void` | Initializes the PRNG with the given seed. Sets both `seed__initial` and `seed__current_random`. |

### Intrusive Queries (advance state)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_pseudo_random_i32__intrusively` | `(Repeatable_Psuedo_Random*) -> Psuedo_Random__i32` | `Psuedo_Random__i32` | Returns a random value and advances the PRNG state. |
| `get_pseudo_random_i32_with__xy__intrusively` | `(Repeatable_Psuedo_Random*, Signed_Index__i32 x, Signed_Index__i32 y) -> Psuedo_Random__i32` | `Psuedo_Random__i32` | Returns a random value seeded by position and advances state. |

### Non-Intrusive Queries (do not advance state)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_pseudo_random_i32__non_intrusively` | `(Repeatable_Psuedo_Random*) -> Psuedo_Random__i32` | `Psuedo_Random__i32` | Returns a random value without advancing state. |
| `get_pseudo_random_i32__non_intrusively_with__seed` | `(Repeatable_Psuedo_Random*, i32 seed) -> Psuedo_Random__i32` | `Psuedo_Random__i32` | Returns a random value derived from the given seed without advancing state. |
| `get_psuedo_random__direction_u8__non_intrusively_with__seed` | `(Repeatable_Psuedo_Random*, i32 seed) -> Direction__u8` | `Direction__u8` | Returns a random direction derived from the given seed without advancing state. |

## Agentic Workflow

### When to Use

Use `Repeatable_Psuedo_Random` when:

- Procedural generation must be deterministic and reproducible (e.g.
  chunk generation, entity spawning).
- Multiple independent PRNG streams are needed (each manager has its
  own `Repeatable_Psuedo_Random`).
- You need to query random values without changing the sequence
  (non-intrusive queries).

### Intrusive vs Non-Intrusive

| Query Type | State Change | Use Case |
|------------|-------------|----------|
| Intrusive | Advances `seed__current_random` | Sequential random generation (entity placement, loot drops). |
| Non-intrusive | No state change | Position-based lookups (tile variation, noise sampling). |

### PRNG Instances in the Engine

Several subsystems maintain their own `Repeatable_Psuedo_Random`:

- `Entity_Manager.randomizer` — entity UUID generation.
- `World.repeatable_pseudo_random` — world generation.
- `Game_Action_Manager.repeatable_pseudo_random` — game action UUIDs.
- `UI_Manager.randomizer` — UI element UUIDs.
- `Aliased_Texture_Manager.repeatable_psuedo_random_for__texture_uuid` — texture UUIDs.
- `Process_Manager.repeatable_psuedo_random_for__process_uuid` — process UUIDs.

### Preconditions

- `initialize_repeatable_psuedo_random` must be called before any
  queries.
- `p_repeatable_psuedo_random` must be non-null for all functions.

### Postconditions

- After `initialize_repeatable_psuedo_random`: both seed fields are set
  to the provided seed.
- After intrusive queries: `seed__current_random` is advanced.
- After non-intrusive queries: `seed__current_random` is unchanged.

### Error Handling

- No explicit error handling. Null pointers result in undefined behavior.
