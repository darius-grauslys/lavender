# get_p_the_kind_of_hitbox_from__ga_collisions

**File of origin:** `core/include/types/core/game_action/collisions/ga_types__collisions.h`

## Semantic

Retrieves a pointer to the `the_kind_of__hitbox` field within the `GA_Collisions` payload of a `Game_Action`. This is an accessor function that provides mutable, pointer-level access to the hitbox kind data.

## Pre-conditions

1. `p_game_action` must be non-null.
2. `p_game_action` must point to a valid `Game_Action` whose payload union has been initialized as a `GA_Collisions` payload (i.e., the game action's kind must correspond to a collisions action).
3. The caller must not use the returned pointer after the `Game_Action` is modified, reinitialized, or deallocated.

## Post-conditions

1. Returns a pointer to the `the_kind_of__hitbox` field within the `GA_Collisions` payload of `p_game_action`.
2. The caller can read or modify the hitbox kind through the returned pointer.
3. No changes are made to `p_game_action` itself; the function is a pure accessor.

## Correctness Verdict

**Incorrect**

## Semantic Alignment

The function's intent is to provide pointer-level access to the `the_kind_of__hitbox` field of the `GA_Collisions` payload. The implementation correctly accesses this field via the `GET_P_GAME_ACTION_PAYLOAD_AS_P` macro and takes its address. However, there is a **type mismatch**: the field `the_kind_of__hitbox` is of type `Hitbox_Kind` (an enum), but the function's return type is `Identifier__u32 *` (i.e., `uint32_t *`). Taking the address of an `enum` field yields a `Hitbox_Kind *`, not a `uint32_t *`. While C allows implicit conversion between enum values and integer types in assignments and returns-by-value, returning a pointer of the wrong type is a type-incompatible pointer conversion. This violates strict aliasing rules and constitutes undefined behavior if the caller writes through the pointer with `uint32_t` semantics that differ from the enum's underlying representation.

The sibling function `get_the_kind_of_hitbox_from__ga_collisions` (returning `Identifier__u32` by value) is semantically correct because returning the enum value as `uint32_t` by value is a valid implicit conversion.

## Implementation Correctness

- **Type compatibility:** The return type `Identifier__u32 *` is incompatible with the actual address-of result `Hitbox_Kind *`. This is a type mismatch — the function casts a pointer to an enum to a pointer to `uint32_t`. While this may work on most platforms where `Hitbox_Kind` is represented as a 32-bit integer, it is technically undefined behavior under strict aliasing rules and is not type-safe.
- **Undefined behavior:** Dereferencing or writing through the returned `uint32_t *` pointer to modify an object that was declared as `Hitbox_Kind` violates strict aliasing. Reading through the pointer may also be UB depending on compiler optimizations.
- **Validation:** The function performs no validation on `p_game_action`. This is consistent with the codebase pattern — other accessor functions (e.g., `get_uuid_of__target_from__ga_collisions`) also do not validate. Validation is the caller's responsibility.

## Side Effects

No side effects. The function is a pure accessor that returns a pointer to internal data; it does not modify `p_game_action` or any other state.
