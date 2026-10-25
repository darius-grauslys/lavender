set_ui_tile_to__ui_tile_raw — core/include/ui/ui_tile.h

Writes the endian-proof raw representation of a UI_Tile into an output UI_Tile_Raw.

Pre-conditions:
1. p_ui_tile must be a non-null pointer to a valid, initialized UI_Tile struct.
2. p_ui_tile_raw must be a non-null pointer to a writable UI_Tile_Raw (u16) value.

Post-conditions:
1. *p_ui_tile_raw is overwritten with the packed raw value derived from (*p_ui_tile) via get_ui_tile_raw_from__ui_tile.
2. p_ui_tile is not modified (read-only access via const-correct callee).

Correctness Verdict: Correct

Semantic Alignment:
The function correctly fulfills its intent: it extracts the endian-proof raw form of a UI_Tile and stores it into the provided UI_Tile_Raw output. The callee get_ui_tile_raw_from__ui_tile packs the 10-bit tile kind (UI_TILE_KIND__BIT_COUNT) into the lower bits and, when UI_TILE__IS_NOT__SAVING_FLAGS_TO__RAW is not defined, packs the 6-bit ui_tile_flags (UI_TILE__QUANTITY_OF__FLAGS) into the upper bits via a left shift of UI_TILE_KIND__BIT_COUNT. This matches the UI_Tile struct layout exactly (10 + 6 = 16 bits, matching UI_Tile_Raw which is u16). The function is a thin wrapper that delegates correctly and writes the result to the output pointer.

Implementation Correctness:
Type compatibility — p_ui_tile_raw is of type UI_Tile_Raw* (pointer to u16), and the value assigned to *p_ui_tile_raw is the return value of get_ui_tile_raw_from__ui_tile, which returns UI_Tile_Raw (u16). Types match exactly. No implicit conversions or truncation.
Undefined behavior — no pointer arithmetic, no null dereference (assuming pre-conditions hold), no type punning, no out-of-bounds access. The function dereferences p_ui_tile_raw to write, and passes p_ui_tile to the callee which accesses it via a const pointer. Both accesses are within the bounds of their respective types.
Validation — no validation is needed or expected. This is a low-level inline setter; ensuring pointer validity is the caller's responsibility.

Side Effects:
*p_ui_tile_raw is mutated (overwritten with the packed raw representation of the UI_Tile). p_ui_tile is read but not modified.
