set_ui_element_as__using_sprite — core/include/ui/ui_element.h

Sets the "using sprite" flag bit on a UI element, marking it as sprite-backed rather than UI-tile-span-backed.

Pre-conditions:
1. p_ui_element must be a non-null pointer to a valid, initialized UI_Element struct.
2. p_ui_element->ui_flags must be a valid UI_Flags__u16 (uint16_t); no specific bit pattern is required beforehand.

Post-conditions:
1. The UI_FLAGS__BIT_IS_USING__SPRITE_OR_UI_TILE_SPAN bit (BIT(6)) in p_ui_element->ui_flags is set to 1.
2. All other bits in p_ui_element->ui_flags remain unchanged.
3. After return, is_ui_element__using_sprite(p_ui_element) evaluates to true.

Correctness Verdict: Correct

Semantic Alignment:
The implementation correctly sets the shared flag bit UI_FLAGS__BIT_IS_USING__SPRITE_OR_UI_TILE_SPAN via bitwise OR (|=). This flag is a single bit (BIT(6)) that distinguishes between two rendering modes: sprite (bit set) and UI tile span (bit cleared). The companion function set_ui_element_as__using_ui_tile_span clears the same bit via &= ~, and the getter is_ui_element__using_sprite checks the bit. The implementation is consistent with the semantic intent of marking a UI element as using a sprite. The flag name itself ("IS_USING__SPRITE_OR_UI_TILE_SPAN") reflects that this single bit is the discriminator between the two modes.

Implementation Correctness:
Type compatibility — p_ui_element->ui_flags is UI_Flags__u16 (typedef uint16_t). UI_FLAGS__BIT_IS_USING__SPRITE_OR_UI_TILE_SPAN expands to BIT(6) = ((1U) << 6) = 64, which is an unsigned int. The |= operation assigns an unsigned int result back to a uint16_t, which is safe since the value (64) fits within uint16_t range. No implicit truncation or conversion issues.
Undefined behavior — no pointer arithmetic, no null dereference (consistent with all sibling flag-setting functions in this header), no type punning, no out-of-bounds access. The function dereferences p_ui_element without a null check, but this is the established pattern for all static inline flag setters in this file (e.g., set_ui_element_as__focused, set_ui_element_as__being_dragged, etc.). Validation is the caller's responsibility.
No validation is needed — this is a low-level inline bit-flag setter. The caller is responsible for ensuring p_ui_element is valid.

Side Effects:
Mutates p_ui_element->ui_flags by setting the UI_FLAGS__BIT_IS_USING__SPRITE_OR_UI_TILE_SPAN bit. No other observable side effects.
