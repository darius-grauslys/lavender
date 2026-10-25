# Function Review: get_highest_priority_ui_element_thats__under_the_cursor

**File of origin**: `core/source/ui/ui_manager.c` (lines 243–289)

---

## Semantic

Iterates through the UI_Manager's packed pointer array of UI elements (ordered by priority — lowest index = highest priority), skipping disabled and non-interactive elements, and returns the first (highest-priority) UI element whose hitbox AABB contains the current cursor position. If a click was just released, the previous cursor position is used instead of the current one.

---

## Pre-conditions

1. `p_ui_manager` must be non-null and have its `pM_ptr_array_of__ui_elements` allocated (via `allocate_ui_manager__members`). The array is packed — no gaps between valid entries.
2. `p_game` must be non-null and properly initialized, with a valid `Hitbox_Context` containing a registered `Hitbox_AABB_Manager` for this UI_Manager's UUID.
3. `p_game->input` (or the client's input) must be valid, providing `cursor__3i32` and `cursor__old__3i32`.
4. The UI_Manager must have been allocated with a `max_quantity_of__ui_elements` that does not exceed `MAX_QUANTITY_OF__UI_ELEMENTS` (128).

---

## Post-conditions

1. Returns a pointer to the highest-priority (lowest array index) enabled, interactive UI element whose hitbox contains the cursor position.
2. Returns `NULL` (0) if no matching UI element is found.
3. No state is mutated — the function is read-only with respect to both `p_ui_manager` and `p_game`.

---

## Correctness Verdict

**Incorrect**

---

## Semantic Alignment

The function's intent is to find the highest-priority UI element under the cursor. The iteration order (index 0 upward) correctly corresponds to priority ordering, as confirmed by `get_ui_element__priority` and `swap_priority_of__ui_elenents_within__ui_manager`. However, the implementation contains a critical bug that causes it to fail its semantic intent in common scenarios.

---

## Implementation Correctness

### Bug 1 (Critical): `return 0` instead of `continue` on missing hitbox (line 278–279)

When `get_p_hitbox_aabb_by__uuid_u32_from__hitbox_aabb_manager` returns `NULL` (indicating the UI element does not have a hitbox registered in the hitbox manager), the function immediately returns `0` (NULL):

```c
if (!p_hitbox_aabb)
    return 0;
```

This is incorrect. A UI element may legitimately lack a hitbox — for example:
- A logical/container `UI_Element` (kind `UI_Element_Kind__Logical` or `UI_Element_Kind__Window`) that has no collision geometry.
- An element that has been allocated but whose hitbox has not yet been set up via `allocate_hitbox_for__ui_element`.

When such an element appears at a lower index (higher priority) than a valid interactive element under the cursor, the function aborts the entire search and returns `NULL`, even though a lower-priority element does contain the cursor. The correct behavior is to `continue` past elements without hitboxes, allowing the search to proceed to subsequent elements.

**Fix**: Replace `return 0;` with `continue;`.

### Bug 2 (Minor): Stray semicolon (line 257)

A stray semicolon appears after the ternary expression that assigns `cursor_position`:

```c
Vector__3i32 cursor_position =
    (is_input__click_released(p_input))
    ? p_input->cursor__old__3i32
    : p_input->cursor__3i32;
    ;  // <-- empty statement, harmless but poor style
```

This is harmless (an empty statement) but indicates sloppy code.

### Type Compatibility

- The loop variable `Index__u32` (uint32_t) is compared against `max_quantity_of__ui_elements` of type `Quantity__u16` (uint16_t). The uint16_t is implicitly widened to uint32_t for the comparison, which is safe.
- The cast `(Hitbox_AABB_Manager*)` on the return of `get_pV_hitbox_manager_from__hitbox_context` (which returns `void*`) is appropriate.
- `cursor_position` is `Vector__3i32`, matching the parameter type of `is_vector_3i32_inside__hitbox_aabb`.

### Null Check on `break` (line 264–265)

The `break` on a null `p_ui_element` is correct. The UI_Manager uses a packed array (confirmed by `allocate_ui_element_from__ui_manager` and `release__ui_element_from__ui_manager`, which uses a swap-and-pop pattern). Once a null entry is encountered, all subsequent entries are also null, so breaking is the correct behavior.

---

## Side Effects

No side effects. The function is read-only — it does not modify `p_ui_manager`, `p_game`, or any UI elements. It only reads from the UI_Manager's element array, the game's input state, and the hitbox manager.