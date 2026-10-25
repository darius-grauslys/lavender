# is_ui_tile_map__wrapper_with__valid_size

**File of origin:** `core/include/ui/ui_tile_map.h`

---

## Semantic

Returns `true` if the given `UI_Tile_Map__Wrapper` has a valid size, meaning its width and height are both greater than zero and its size category is a valid enum value (i.e., `Small`, `Medium`, or `Large` — not `None` or `Unknown`).

---

## Pre-conditions

1. `p_ui_tile_map__wrapper` must be a non-null pointer to a valid `UI_Tile_Map__Wrapper` struct. Passing `NULL` results in undefined behavior (null pointer dereference on the first field access). This is consistent with the codebase convention for all `is_ui_tile_map__wrapper_*` inline predicates, which assume the caller provides a valid pointer.
2. The `UI_Tile_Map__Wrapper` struct must be properly initialized (its fields populated with meaningful values) before the function is called.

---

## Post-conditions

1. Returns `true` if and only if all three of the following hold:
   - `width_of__ui_tile_map > 0`
   - `height_of__ui_tile_map > 0`
   - `is_ui_tile_map__wrapper_with__valid_size_catagory(p_ui_tile_map__wrapper)` returns `true` (i.e., `catagory_size_of__ui_tile_map` is strictly greater than `UI_Tile_Map_Size__None` and strictly less than `UI_Tile_Map_Size__Unknown`).
2. Returns `false` otherwise.
3. The function does not modify the struct or any other state.

---

## Correctness Verdict

**Correct**

---

## Semantic Alignment

The implementation faithfully fulfills the semantic intent described by the function name. It checks all three dimensions of "valid size":

- **Width positivity:** `p_ui_tile_map__wrapper->width_of__ui_tile_map > 0` — `width_of__ui_tile_map` is of type `Quantity__u32` (`uint32_t`), so the comparison `> 0` is valid and correct for an unsigned type. A width of 0 would indicate an uninitialized or empty tile map.
- **Height positivity:** `p_ui_tile_map__wrapper->height_of__ui_tile_map > 0` — same reasoning as width.
- **Valid size category:** Delegates to `is_ui_tile_map__wrapper_with__valid_size_catagory`, which verifies that `catagory_size_of__ui_tile_map` falls within the valid range (`UI_Tile_Map_Size__Small` through `UI_Tile_Map_Size__Large`), excluding `UI_Tile_Map_Size__None` (0) and `UI_Tile_Map_Size__Unknown` (4).

The `&&` short-circuit evaluation ensures that if width or height is invalid, the category check is skipped, which is a harmless optimization. No semantic drift is present — the function does exactly what its name implies.

---

## Implementation Correctness

- **Type compatibility:** `width_of__ui_tile_map` and `height_of__ui_tile_map` are both `Quantity__u32` (`uint32_t`), and the literal `0` is an `int`. The comparison `uint32_t > int` involves an implicit conversion of `0` to `uint32_t`, which is well-defined and produces the correct result. No truncation or precision loss occurs.
- **Undefined behavior:** No undefined behavior is present, assuming the pre-condition (non-null pointer) is met. There is no broken pointer arithmetic, no type punning, and no out-of-bounds access.
- **Validation appropriateness:** The function does not validate the pointer itself (no null check). This is appropriate for its role as a lightweight `static inline` predicate — the established convention in this module is that callers are responsible for providing valid pointers. The function's own responsibility is to check the *semantic validity* of the size fields, which it does correctly.
- **Minor style note:** There is a stray empty statement (`;`) on its own line after the `return` expression's terminating semicolon. This is harmless (an empty statement inside the function body) but is a minor cosmetic issue.

---

## Side Effects

No side effects. This is a pure query function: it reads fields from the `UI_Tile_Map__Wrapper` struct and returns a boolean result. It does not modify the struct or any other observable state.
