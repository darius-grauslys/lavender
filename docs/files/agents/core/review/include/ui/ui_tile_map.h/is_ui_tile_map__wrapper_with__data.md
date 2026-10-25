is_ui_tile_map__wrapper_with__data — core/include/ui/ui_tile_map.h, lines 84-88

Checks whether a UI_Tile_Map__Wrapper has a non-null tile data pointer.

Pre-conditions:
1. p_ui_tile_map__wrapper must be a non-null pointer to a valid UI_Tile_Map__Wrapper object.

Post-conditions:
1. Returns true if p_ui_tile_data is non-null, false otherwise.

Correctness Verdict: Correct

Semantic Alignment:
The function's intent is to determine whether the wrapper has associated tile data. It accesses the p_ui_tile_data field of the UI_Tile_Map__Wrapper struct and returns its truthiness. This correctly reflects whether tile data is present.

Implementation Correctness:
Type compatibility — The function returns bool, but the expression p_ui_tile_map__wrapper->p_ui_tile_data is of type UI_Tile_Raw * (pointer to u16). In C, returning a pointer in a boolean context is valid and well-defined: a non-null pointer converts to true, and a null pointer converts to false. This is an implicit conversion but is semantically correct and idiomatic for pointer-to-boolean checks.
No undefined behavior — No pointer arithmetic, no null dereference (assuming the pre-condition holds), no type punning, no out-of-bounds access.
No validation of p_ui_tile_map__wrapper for null — this is acceptable as validation is the caller's responsibility, consistent with the pattern seen in other inline accessor functions in this header (e.g., is_ui_tile_map__wrapper_with__valid_size, get_width_of__p_ui_tile_map__wrapper).

Side Effects:
No side effects — the function is a pure query that reads the p_ui_tile_data field of the pointed-to struct without modifying any state.
