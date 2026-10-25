set_ui_tile_as__not_scaling_vertically — core/include/ui/ui_tile.h

Clears the UI_TILE_FLAG__SCALE_VERTICAL bit in a UI_Tile's flags, indicating the tile should not scale vertically.

Pre-conditions:
1. p_ui_tile must be a non-null pointer to a writable UI_Tile object.

Post-conditions:
1. The UI_TILE_FLAG__SCALE_VERTICAL bit (BIT(0)) in p_ui_tile->ui_tile_flags is cleared (set to 0).
2. All other bits in ui_tile_flags remain unchanged.

Correctness Verdict: Correct

Semantic Alignment:
The implementation correctly clears the SCALE_VERTICAL flag using bitwise AND with the complement of the flag mask (~UI_TILE_FLAG__SCALE_VERTICAL). This matches the semantic intent of "not scaling vertically." The pattern is consistent with the sibling function set_ui_tile_as__not_scaling_horizontally, which uses the same idiom for the SCALE_HORIZONTAL flag.

Implementation Correctness:
Type compatibility — p_ui_tile is a UI_Tile * and ui_tile_flags is of type UI_Tile_Flags (u16). UI_TILE_FLAG__SCALE_VERTICAL is BIT(0) = 1U, which is compatible with u16. The bitwise AND-assignment operates on compatible types with no implicit conversions or truncation.
No undefined behavior — no pointer arithmetic, no null dereference (pre-condition ensures non-null), no type punning, no out-of-bounds access.
No validation is needed — this is a low-level flag manipulation function. The caller is responsible for ensuring p_ui_tile is valid.

Side Effects:
Mutates p_ui_tile->ui_tile_flags by clearing the UI_TILE_FLAG__SCALE_VERTICAL bit. No other side effects.
