is_ui_tile_map__wrapper__valid — core/include/ui/ui_tile_map.h

Checks whether a UI_Tile_Map__Wrapper is in a valid state for use by verifying that its data pointer is non-null, its width and height are positive, and its tile map size category is within the valid range.

Pre-conditions:
1. p_ui_tile_map__wrapper must be a non-null pointer to a valid, accessible UI_Tile_Map__Wrapper struct (the function dereferences it directly without a null guard).
2. The struct fields may have any values — the function is designed to validate them.

Post-conditions:
1. Returns true if and only if all of the following hold: p_ui_tile_data is non-null, width_of__ui_tile_map > 0, height_of__ui_tile_map > 0, and catagory_size_of__ui_tile_map is strictly greater than UI_Tile_Map_Size__None (0) and strictly less than UI_Tile_Map_Size__Unknown (4).
2. Returns false otherwise.
3. No mutation occurs — the function is a pure query.

Correctness Verdict: Correct

Semantic Alignment:
The implementation faithfully fulfills the semantic intent of validating a UI_Tile_Map__Wrapper. It delegates to three helper functions: is_ui_tile_map__wrapper_with__data (checks p_ui_tile_data is non-null), is_ui_tile_map__wrapper_with__valid_size (checks width > 0, height > 0, and delegates to category check), and is_ui_tile_map__wrapper_with__valid_size_catagory (checks the category enum is within the valid range). The combination via logical AND correctly expresses "all conditions must be satisfied." The enum bounds check (> UI_Tile_Map_Size__None and < UI_Tile_Map_Size__Unknown) correctly accepts Small (1), Medium (2), and Large (3) while rejecting None (0) and Unknown (4). The width/height > 0 check correctly rejects zero-dimension maps.

Implementation Correctness:
Type compatibility — the parameter type (UI_Tile_Map__Wrapper *) matches the struct pointer used throughout. All field accesses use the correct types (pointer, u32, enum). No implicit conversions or truncation.
Undefined behavior — no pointer arithmetic, no type punning, no out-of-bounds array access. The function dereferences p_ui_tile_map__wrapper without a null check, but this is consistent with the codebase convention for low-level inline helpers (all three delegate functions share the same pattern). The caller is responsible for ensuring the pointer is valid.
Validation — the validation is appropriate for a predicate function. It checks all four struct fields (p_ui_tile_data, width_of__ui_tile_map, height_of__ui_tile_map, catagory_size_of__ui_tile_map) for validity, matching the struct definition exactly.

Side Effects:
No side effects — the function is a pure query. It reads struct fields and returns a boolean without modifying any state.
