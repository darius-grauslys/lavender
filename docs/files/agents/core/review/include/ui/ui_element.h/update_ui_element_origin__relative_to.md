# Function Review: update_ui_element_origin__relative_to

## 1. Header

- **Function name**: `update_ui_element_origin__relative_to`
- **File of origin**: `core/source/ui/ui_element.c`

## 2. Semantic

Updates the position of a UI element's hitbox AABB by computing the relative offset from `position__old__3i32` to `position__new__3i32` and applying that offset to the element's current hitbox position. This preserves the element's relative placement when its reference origin changes.

## 3. Pre-conditions

1. `p_ui_element` must be non-null. This is checked in debug builds only (guarded by `#ifndef NDEBUG`).
2. `p_game` must be valid and contain a properly initialized `hitbox_context` with a registered `Hitbox_AABB_Manager` whose UUID matches the UI manager's UUID. Not explicitly checked — assumed valid by the caller.
3. `p_ui_manager` must be valid and have a `Serialization_Header` with a valid UUID. Not explicitly checked — assumed valid by the caller.
4. The `p_ui_element` must have an associated `Hitbox_AABB` registered in the hitbox AABB manager. Checked at runtime — if no hitbox is found, the function returns early without modifying anything.
5. `position__old__3i32` and `position__new__3i32` are `Vector__3i32` values representing the old and new reference positions. No range constraints are enforced.

## 4. Post-conditions

1. If `p_ui_element` is null (debug builds only), the function logs an error and returns without modification.
2. If no `Hitbox_AABB` is found for the `p_ui_element`, the function returns early without modifying any state.
3. If successful, the `Hitbox_AABB`'s position is updated to: `current_position - position__old__3i32 + position__new__3i32` (i.e., the relative offset from the old reference position is preserved relative to the new reference position).
4. The `UI_Manager` is marked as dirty (`UI_MANAGER_FLAG__IS_DIRTY` is set).
5. The `Hitbox_AABB` is marked as dirty (via `set_hitbox_aabb__position_with__3i32`, which calls `set_hitbox_aabb_as__dirty`).

## 5. Correctness Verdict

**Correct**

## 6. Semantic Alignment

The implementation correctly fulfills the semantic intent. The computation:

```
position_final = (current_position - position__old) + position__new
```

is the correct mathematical formulation for a relative position update. If the UI element was at `current_position` relative to `position__old`, it should now be at `current_position + (position__new - position__old)` relative to the new reference point. The implementation computes exactly this.

The vector arithmetic functions (`add_vectors__3i32`, `subtract_vectors__3i32`) are correctly composed and operate on `Vector__3i32` types consistently throughout.

## 7. Implementation Correctness

- **Type compatibility**: All types match exactly. `Vector__3i32` is used consistently for position parameters. `add_vectors__3i32` and `subtract_vectors__3i32` accept and return `Vector__3i32`. `get_position_3i32_of__hitbox_aabb` returns `Vector__3i32`, and `set_hitbox_aabb__position_with__3i32` accepts `Vector__3i32`. The `void*` return from `get_pV_hitbox_manager_from__hitbox_context` is correctly cast to `Hitbox_AABB_Manager*`, consistent with the pattern used throughout the codebase (e.g., in `ui_manager.c`).

- **Undefined behavior**: No broken pointer arithmetic, no null dereference, no type punning, no out-of-bounds access. `p_ui_element` is null-checked in debug builds, and `p_hitbox_aabb` is null-checked at runtime. The `p_game` and `p_ui_manager` pointers are assumed valid by the caller, consistent with the codebase's conventions.

- **Validation**: Appropriate for the function's role. The `p_ui_element` null check in debug mode follows the codebase pattern. The `p_hitbox_aabb` null check at runtime is necessary because not all UI elements may have an associated hitbox (e.g., elements that have not yet been allocated a hitbox). The null check on `p_hitbox_aabb` is a runtime guard, not just a debug assertion, which is correct since missing hitboxes are a legitimate runtime condition.

- **Fractional precision note**: The internal hitbox position is stored as `Vector__3i32F4` (4-bit fixed-point fractional). When reading via `get_position_3i32_of__hitbox_aabb`, the fractional bits are truncated via `i32F4_to__i32` (arithmetic right shift by 4). When writing via `set_hitbox_aabb__position_with__3i32`, the integer values are shifted left by 4, zeroing the fractional bits. This means any sub-tile fractional position is lost during this operation. This is a design characteristic of the `Vector__3i32` API layer, not a bug in this function — the function correctly uses the integer-position API consistently.

## 8. Side Effects

1. **UI_Manager mutation**: Sets `UI_MANAGER_FLAG__IS_DIRTY` on `p_ui_manager` via `set_ui_manager_as__dirty`, marking the UI manager as requiring recomposition.
2. **Hitbox_AABB mutation**: Sets the dirty flag on the hitbox AABB (via `set_hitbox_aabb__position_with__3i32`, which calls `set_hitbox_aabb_as__dirty`).
3. **Hitbox_AABB position change**: Overwrites the `position__3i32F4` field of the hitbox AABB with the computed relative position. The fractional bits are zeroed due to the `Vector__3i32` to `Vector__3i32F4` conversion in `set_hitbox_aabb__position_with__3i32`.
