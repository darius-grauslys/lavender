# initialize_game_action_manager

**File of origin:** `core/source/game_action/game_action_manager.c`

## Semantic

Resets a `Game_Action_Manager` struct to its initial conditions for pool reuse (Lavender-style initialization, not RAII). It zeroes out all `Game_Action` entries in the manager's contiguous array (marking them as deallocated) and seeds the manager's repeatable pseudo-random number generator with the manager's own pointer address.

## Pre-conditions

1. `p_game_action_manager` must be a valid, non-null pointer to a `Game_Action_Manager` struct.
2. The `game_actions` array must be a contiguous block of `MAX_QUANTITY_OF__GAME_ACTIONS` (512) `Game_Action` elements.

## Post-conditions

1. All `MAX_QUANTITY_OF__GAME_ACTIONS` (512) entries in `p_game_action_manager->game_actions` are zeroed via `memset` and their `Serialization_Header` fields are set to `IDENTIFIER__UNKNOWN__u32` (deallocated state), making them available for future allocation.
2. `p_game_action_manager->repeatable_pseudo_random` is initialized with `seed__initial` and `seed__current_random` both set to `(u32)(uint64_t)p_game_action_manager`, providing a deterministic seed derived from the manager's address.

## Correctness Verdict

**Correct**

## Semantic Alignment

The function fulfills the Lavender initialization semantic: it cleans up the struct to its initial conditions for pool reuse. Both fields of the `Game_Action_Manager` struct are properly handled:

- `game_actions` array: Each `Game_Action` element is zeroed and its serialization header is set to the deallocated/unknown UUID state, marking all game actions as available for future allocation.
- `repeatable_pseudo_random`: Seeded with the pointer address of the manager, providing a deterministic but address-derived seed for UUID generation.

No struct fields are omitted. The `Game_Action_Manager` struct has exactly two fields, and both are initialized.

## Implementation Correctness

- **Type compatibility:** The cast `(Serialization_Header*)p_game_action_manager->game_actions` is valid because `Game_Action` has a `Serialization_Header` as its first member (via the union containing `_serialiation_header`). The `sizeof(Game_Action)` correctly matches the size passed to `initialize_serialization_header__contiguous_array`. The seed parameter `(u32)(uint64_t)p_game_action_manager` correctly casts the pointer to `uint64_t` first (to avoid truncation on 64-bit platforms) and then to `u32`, matching the `Psuedo_Random_Seed__u32` parameter type.
- **Undefined behavior:** No broken pointer arithmetic, no null dereference (assuming pre-condition 1 holds), no type punning, no out-of-bounds access. The contiguous array iteration in `initialize_serialization_header__contiguous_array` correctly steps through `size_of__struct` increments.
- **Validation:** No validation is performed inside this function. This is appropriate for the function's role — it is the caller's responsibility to ensure `p_game_action_manager` is non-null and valid. This is consistent with the codebase's convention where debug-mode assertions are handled at call sites or in callees that operate on individual elements.

## Side Effects

1. All 512 `Game_Action` entries in `p_game_action_manager->game_actions` are zeroed and their serialization headers are set to the deallocated state, effectively releasing all game actions from the pool.
2. `p_game_action_manager->repeatable_pseudo_random` is re-seeded with the manager's pointer address, resetting its internal random state.
