set_ui_tile_as__not_scaling_horizontally — core/include/ui/ui_tile.h

Clears the UI_TILE_FLAG__SCALE_HORIZONTAL bit in the ui_tile_flags bitfield of a UI_Tile, marking the tile as not scaling horizontally.

Pre-conditions:
1. p_ui_tile must be a non-null pointer to a writable UI_Tile object.
2. The caller is responsible for ensuring p_ui_tile points to valid memory; no null check is performed (consistent with all sibling flag-setter functions in this header).

Post-conditions:
1. p_ui_tile->ui_tile_flags has the UI_TILE_FLAG__SCALE_HORIZONTAL bit (BIT(1)) cleared; all other bits in the 6-bit ui_tile_flags bitfield are preserved.

Correctness Verdict: Correct

Semantic Alignment:
The implementation correctly fulfills its semantic intent: clearing the SCALE_HORIZONTAL flag. The function is the inverse of set_ui_tile_as__scaling_horizontally (which sets the same bit via |=). The operation `p_ui_tile->ui_tile_flags &= ~UI_TILE_FLAG__SCALE_HORIZONTAL` uses bitwise AND with the complement of the flag, which is the standard idiom for clearing a single bit in a flags field. This matches the pattern used by all other "set_*_as__not_*" functions in this header (e.g., set_ui_tile_as__not_scaling_vertically, set_ui_tile_as__unflipped_horizontally, set_ui_tile_as__unflipped_vertically).

Implementation Correctness:
Type compatibility — UI_TILE_FLAG__SCALE_HORIZONTAL is BIT(1), which expands to (1U << 1), an unsigned int (u32). The ui_tile_flags field is a 6-bit bitfield of underlying type UI_Tile_Flags (u16). The ~ operator produces a u32 (0xFFFFFFFD), which is then ANDed with the promoted bitfield value and stored back. The result is truncated to the 6-bit width of the bitfield. Since the original bitfield value is at most 6 bits (0-63) and the mask 0xFFFFFFFD has all bits set except bit 1, the truncation correctly preserves all bits 0, 2, 3, 4, 5 and clears bit 1. No implicit conversion causes data loss.
Undefined behavior — no broken pointer arithmetic, no null dereference (caller's responsibility), no type punning, no out-of-bounds access. The bitfield width (6) accommodates all defined flags (SCALE_VERTICAL=BIT(0), SCALE_HORIZONTAL=BIT(1), FLIPPED_VERTICAL=BIT(2), FLIPPED_HORIZONTAL=BIT(3), GENERAL_1=BIT(4), GENERAL_2=BIT(5)).
Validation — no validation is needed for this low-level inline utility function. The caller is responsible for ensuring p_ui_tile is valid, consistent with the codebase pattern for all sibling functions in this header.

Side Effects:
Mutates p_ui_tile->ui_tile_flags by clearing the UI_TILE_FLAG__SCALE_HORIZONTAL bit. No other state is modified.
