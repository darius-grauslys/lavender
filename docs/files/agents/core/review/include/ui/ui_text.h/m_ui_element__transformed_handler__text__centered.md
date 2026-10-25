m_ui_element__transformed_handler__text__centered — core/source/ui/ui_text.c

Centers the typer's position within the hitbox's bounding box and sets the typer's bounding box size to match the hitbox dimensions.

Pre-conditions:
1. p_this_ui_element must be a non-null pointer to a properly initialized UI_Element of kind UI_Element_Kind__Text (or compatible with UI_Text union members).
2. p_this_ui_element->typer.p_font must be non-null; the function dereferences it to access max_width_of__font_letter and max_height_of__font_letter without any null check.
3. p_hitbox_aabb must be a non-null pointer to a valid Hitbox_AABB with initialized width__quantity_u32 and height__quantity_u32 fields.
4. p_game must be a non-null pointer to a valid Game instance (used to retrieve the UI_Manager).
5. p_graphics_window must be a non-null pointer to a valid Graphics_Window associated with a UI_Manager.
6. p_this_ui_element->size_of__char_buffer should reflect the actual text length for accurate centering (it is used as a proxy for text width).

Post-conditions:
1. The UI_Manager associated with p_graphics_window is marked dirty (UI_MANAGER_FLAG__IS_DIRTY set).
2. The typer's text_bounding_box position is set to a computed offset from position_NEW_of__hitbox__3i32 intended to center the text horizontally and vertically within the hitbox.
3. The typer's text_bounding_box size is set to the width and height of p_hitbox_aabb.

Correctness Verdict: Incorrect

Semantic Alignment:
The function's intent is to center text within a hitbox. Two bugs prevent correct centering:

1. Y-axis sign error (major): The y offset is computed as `-(hitbox_height/2 - font_height/2)`, which equals `font_height/2 - hitbox_height/2`. This has the opposite sign of the x offset (which correctly uses `hitbox_width/2 - text_width/2`). For centering, the y offset should be `hitbox_height/2 - font_height/2` (same sign convention as x). The erroneous negative sign causes the text to be positioned outside the hitbox (above it in a y-down coordinate system, or below it in a y-up system) rather than centered. The correct expression would be:
   ```
   ((get_height_u32_of__hitbox_aabb(p_hitbox_aabb) >> 1)
    - (p_this_ui_element->typer.p_font->max_height_of__font_letter >> 1))
   ```
   without the leading negation.

2. Division-before-multiplication in x-axis (minor): The x offset computes `char_buffer_size * (font_max_width / 2)` instead of `(char_buffer_size * font_max_width) / 2`. Due to integer truncation, when `font_max_width` is odd (e.g., 5), `font_max_width / 2` truncates to 2, and the subsequent multiplication loses precision. The correct expression would be:
   ```
   (p_this_ui_element->size_of__char_buffer
     * p_this_ui_element->typer.p_font->max_width_of__font_letter) >> 1
   ```
   This ensures the multiplication happens before the division, preserving precision.

Implementation Correctness:
- Type compatibility: The expressions passed to get_vector__3i32 use unsigned arithmetic (u32) for both x and y offsets. The subtraction of two u32 values can produce values that exceed INT_MAX, relying on implicit conversion from u32 to i32 (Signed_Index__i32). While this works correctly on two's complement systems (the bit pattern wraps and is reinterpreted as a negative i32), it is technically implementation-defined behavior per the C standard. The non-centered variant does not have this issue as it passes position directly without arithmetic.
- Undefined behavior: The function dereferences p_this_ui_element->typer.p_font without a null check. If p_font is NULL, this is undefined behavior. The non-centered variant does not access p_font and is therefore immune to this issue.
- Validation: No validation is performed for p_font being null, which is inconsistent with the debug-mode null checks present in get_p_ui_manager_from__graphics_window and the hitbox accessor functions.

Side Effects:
1. Marks the UI_Manager as dirty via set_ui_manager_as__dirty, triggering a UI recomposition.
2. Mutates the typer's text_bounding_box position (via set_typer__position).
3. Mutates the typer's text_bounding_box size (via set_typer__bounding_box_size).
