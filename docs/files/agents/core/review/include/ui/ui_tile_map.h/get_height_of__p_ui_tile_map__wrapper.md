get_height_of__p_ui_tile_map__wrapper — core/include/ui/ui_tile_map.h

Returns the height (in tiles) of a UI_Tile_Map__Wrapper.

Pre-conditions:
1. p_ui_tile_map__wraper must be a non-null pointer to a valid UI_Tile_Map__Wrapper struct.

Post-conditions:
1. Returns the value of the height_of__ui_tile_map field (type Quantity__u32) from the pointed-to struct.

Correctness Verdict: Correct

Semantic Alignment:
The implementation correctly returns the height_of__ui_tile_map field of the UI_Tile_Map__Wrapper struct. This is a simple accessor that matches its semantic intent exactly.

Implementation Correctness:
Type compatibility — the return type (Quantity__u32) matches the field type (Quantity__u32) exactly. No implicit conversions or truncation.
Undefined behavior — the function dereferences p_ui_tile_map__wraper without a null check. If the caller passes NULL, this is undefined behavior. However, this is consistent with the codebase pattern: all sibling accessors (get_width_of__p_ui_tile_map__wrapper, get_catagory_size_of__p_ui_tile_map__wrapper, is_ui_tile_map__wrapper_with__data, etc.) follow the same no-null-check convention. Validation is the caller's responsibility.
Validation — no validation is needed for this low-level accessor; the caller is expected to ensure the pointer is valid.

Side Effects:
No side effects. This is a pure read accessor that returns a copy of the struct's height field.
