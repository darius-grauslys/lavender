ui_tile_map__large_to__ui_tile_map_wrapper — core/include/ui/ui_tile_map.h

Constructs a UI_Tile_Map__Wrapper from a UI_Tile_Map__Large by delegating to get_ui_tile_map__wrapper, passing the large struct's tile data array, a pointer to its flags, the large width/height constants, and the Large size category.

Pre-conditions:
1. p_ui_tile_map__large must be a non-null pointer to a valid, properly initialized UI_Tile_Map__Large struct.

Post-conditions:
1. Returns a UI_Tile_Map__Wrapper value by copy, with p_ui_tile_data pointing to p_ui_tile_map__large->ui_tile_data__large, width_of__ui_tile_map set to UI_TILE_MAP__LARGE__WIDTH, height_of__ui_tile_map set to UI_TILE_MAP__LARGE__HEIGHT, and catagory_size_of__ui_tile_map set to UI_Tile_Map_Size__Large.
2. The original UI_Tile_Map__Large struct is not modified.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly extracts the tile data pointer, flags pointer, dimensions, and size category from the UI_Tile_Map__Large struct and passes them to get_ui_tile_map__wrapper, which constructs the UI_Tile_Map__Wrapper. The semantic intent — converting a large tile map struct into a generic wrapper — is fulfilled. Note that get_ui_tile_map__wrapper receives p_ui_tile_map__flags as a parameter but does not store it in the returned UI_Tile_Map__Wrapper (the struct has no flags field); this is a design characteristic of get_ui_tile_map__wrapper, not a defect in this function.

Implementation Correctness:
Type compatibility — p_ui_tile_map__large->ui_tile_data__large is of type UI_Tile_Raw[UI_TILE_MAP__LARGE__WIDTH * UI_TILE_MAP__LARGE__HEIGHT], which decays to UI_Tile_Raw* when passed as an argument, matching the UI_Tile_Raw *p_ui_tile_data parameter. &p_ui_tile_map__large->ui_tile_map__flags is of type UI_Tile_Map__Flags*, matching the UI_Tile_Map__Flags *p_ui_tile_map__flags parameter. UI_TILE_MAP__LARGE__WIDTH and UI_TILE_MAP__LARGE__HEIGHT are Quantity__u32 constants. UI_Tile_Map_Size__Large is of type UI_Tile_Map_Size. All types match exactly with no implicit conversions or truncation.
No undefined behavior — no null dereference occurs assuming the pre-condition (non-null pointer) is met. The array-to-pointer decay of ui_tile_data__large is well-defined. No type punning, no out-of-bounds access.
No validation is needed in this function — it is a low-level conversion wrapper. Ensuring p_ui_tile_map__large is non-null and valid is the caller's responsibility.

Side Effects:
No side effects — the function is pure. It reads from the UI_Tile_Map__Large struct and returns a UI_Tile_Map__Wrapper by value without modifying any state.
