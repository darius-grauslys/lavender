set_ui_element_as__using_ui_tile_span — core/include/ui/ui_element.h

Clears the `UI_FLAGS__BIT_IS_USING__SPRITE_OR_UI_TILE_SPAN` bit in the given UI_Element's `ui_flags` field, thereby marking the element as "using UI tile span" (as opposed to "using sprite").

Pre-conditions:
1. p_ui_element must be a non-null pointer to a writable UI_Element object. The function dereferences p_ui_element without a null check; it is the caller's responsibility to ensure validity. This is consistent with the surrounding inline helper functions in this header.
2. The UI_Element struct must have a `ui_flags` field of an unsigned integer type that supports bitwise AND-assign with a bitmask constant.

Post-conditions:
1. The `UI_FLAGS__BIT_IS_USING__SPRITE_OR_UI_TILE_SPAN` bit in `p_ui_element->ui_flags` is cleared (set to 0). All other bits in `ui_flags` are preserved.
2. After return, `is_ui_element__using_ui_tile_span(p_ui_element)` will return true (since that function returns the logical negation of the bit test).
3. After return, `is_ui_element__using_sprite(p_ui_element)` will return false.

Correctness Verdict: Correct

Semantic Alignment:
The function name `set_ui_element_as__using_ui_tile_span` correctly describes its intent: to configure the UI_Element so that it is treated as "using a UI tile span" rather than "using a sprite." The implementation clears the `UI_FLAGS__BIT_IS_USING__SPRITE_OR_UI_TILE_SPAN` bit, which is the correct operation because:
- `is_ui_element__using_sprite_or__ui_tile_span` tests the bit directly (returns true when set).
- `is_ui_element__using_sprite` returns `is_ui_element__using_sprite_or__ui_tile_span(p)` (true when bit is set).
- `is_ui_element__using_ui_tile_span` returns `!is_ui_element__using_sprite_or__ui_tile_span(p)` (true when bit is cleared).
Thus, clearing the bit makes `is_ui_element__using_ui_tile_span` return true and `is_ui_element__using_sprite` return false, exactly matching the function's semantic intent. The complementary function `set_ui_element_as__using_sprite` sets the bit via `|=`, confirming the intended dual relationship.

Implementation Correctness:
Type compatibility — `p_ui_element->ui_flags` is an unsigned integer type and `UI_FLAGS__BIT_IS_USING__SPRITE_OR_UI_TILE_SPAN` is a bitmask constant of a compatible unsigned type; the `&=` and `~` operators are well-defined for these types. No implicit conversions or truncation occur.
No undefined behavior — no pointer arithmetic, no null dereference (the function assumes a valid pointer per the pre-condition), no type punning, no out-of-bounds access. The bitwise complement and AND-assign are standard, safe operations on unsigned integers.
Validation — no validation is performed inside the function. This is appropriate for a low-level inline setter; the caller is responsible for passing a valid pointer. This is consistent with the pattern used by all sibling `set_ui_element_as__*` functions in this header.

Side Effects:
Mutates `p_ui_element->ui_flags` by clearing the `UI_FLAGS__BIT_IS_USING__SPRITE_OR_UI_TILE_SPAN` bit. All other bits in `ui_flags` are left unchanged. No other memory is touched, no I/O is performed, and no other functions are called.
