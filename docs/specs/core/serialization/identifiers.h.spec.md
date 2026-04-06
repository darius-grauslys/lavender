# 1. Specification: core/include/serialization/identifiers.h

## 1.1 Overview

Provides UUID generation and validation utilities. UUIDs are the primary
identity mechanism for all pooled structs in the engine. This module generates
random 32-bit and 64-bit UUIDs using the engine's deterministic pseudo-random
number generator, and provides basic validation checks.

## 1.2 Dependencies

- `defines.h` (for `Identifier__u32`, `Identifier__u64`,
  `IDENTIFIER__UNKNOWN__u32`, `IDENTIFIER__UNKNOWN__u64`, `MASK`)
- `defines_weak.h` (forward declarations)
- `random.h` (for `Repeatable_Psuedo_Random`,
  `get_pseudo_random_i32__intrusively`,
  `get_pseudo_random_i32__non_intrusively`)

## 1.3 Constants

| Constant | Value | Description |
|----------|-------|-------------|
| `IDENTIFIER__UNKNOWN__u32` | `(uint32_t)(-1)` | Sentinel value indicating an invalid or deallocated 32-bit UUID. |
| `IDENTIFIER__UNKNOWN__u64` | `(uint64_t)(-1)` | Sentinel value indicating an invalid or deallocated 64-bit UUID. |

## 1.4 Functions (all static inline)

### 1.4.1 UUID Generation

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_random__uuid_u32` | `(Repeatable_Psuedo_Random*) -> Identifier__u32` | `Identifier__u32` | Generates a random 32-bit UUID by XOR-ing a pseudo-random value with `IDENTIFIER__UNKNOWN__u32`. This ensures the result is never equal to the sentinel value. Uses intrusive randomization (advances the seed). |
| `get_random__uuid_u64` | `(Repeatable_Psuedo_Random*) -> Identifier__u64` | `Identifier__u64` | Generates a random 64-bit UUID by combining two 32-bit pseudo-random values and XOR-ing with `IDENTIFIER__UNKNOWN__u64`. Uses non-intrusive randomization. |

### 1.4.2 UUID Composition

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `merge_identifiers_u32` | `(Identifier__u32 left, Quantity__u8 bits_left, Identifier__u32 right) -> Identifier__u32` | `Identifier__u32` | Merges two identifiers by taking the upper `bits_left` bits from `left` and the remaining lower bits from `right`. |

### 1.4.3 UUID Validation

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `is_identifier_u32__invalid` | `(Identifier__u32) -> bool` | `bool` | Returns true if the identifier equals `IDENTIFIER__UNKNOWN__u32`. |
| `is_identifier_u64__invalid` | `(Identifier__u64) -> bool` | `bool` | Returns true if the identifier equals `IDENTIFIER__UNKNOWN__u64`. |

## 1.5 Agentic Workflow

### 1.5.1 When to use this module

- Use `get_random__uuid_u32` when allocating any struct with a 32-bit
  `Serialization_Header` (entities, hitboxes, sprites, UI elements, etc.).
- Use `get_random__uuid_u64` when allocating any struct with a 64-bit
  `Serialization_Header__UUID_64` (chunks, global spaces, collision nodes).
- Use `is_identifier_u32__invalid` / `is_identifier_u64__invalid` to check
  if a UUID represents a deallocated or uninitialized struct.
- Use `merge_identifiers_u32` for composite identifiers (e.g. inventory
  item stack UUIDs that encode container position).

### 1.5.2 Preconditions

- `p_randomizer` must be a valid, initialized `Repeatable_Psuedo_Random`.
- The randomizer should be seeded appropriately for the context (e.g.
  `Entity_Manager.randomizer`, `Game_Action_Manager.repeatable_pseudo_random`).

### 1.5.3 Postconditions

- `get_random__uuid_u32` will never return `IDENTIFIER__UNKNOWN__u32`.
- `get_random__uuid_u64` will never return `IDENTIFIER__UNKNOWN__u64`.

### 1.5.4 Collision Handling

- UUID collisions are theoretically possible but unlikely. The XOR with
  the sentinel value prevents the most common collision (generating the
  sentinel itself).
- For contiguous array placement, UUID collisions are handled by
  `poll_for__uuid_collision` in `hashing.h`.

### 1.5.5 Intrusive vs Non-Intrusive Randomization

- `get_random__uuid_u32` uses `get_pseudo_random_i32__intrusively`, which
  advances the randomizer's seed state. This means calling it changes the
  randomizer for all subsequent calls.
- `get_random__uuid_u64` uses `get_pseudo_random_i32__non_intrusively`
  (called twice for 64 bits). This does **not** advance the seed state.
