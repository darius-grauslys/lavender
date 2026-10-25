ui_tile_map__small_to__ui_tile_map_wrapper — core/include/ui/ui_tile_map.h

Wraps a UI_Tile_Map__Small struct into a UI_Tile_Map__Wrapper by delegating to get_ui_tile_map__wrapper, supplying the small tile map's data array, flags pointer, and fixed dimension constants.

Pre-conditions:
1. p_ui_tile_map__small must be a non-null pointer to a valid, allocated UI_Tile_Map__Small struct.
2. The ui_tile_data__small array within the struct is a fixed-size array and is always valid if the struct is valid.
3. The ui_tile_map__flags field is accessible and its address is taken for the get_ui_tile_map__wrapper call.

Post-conditions:
1. Returns a UI_Tile_Map__Wrapper struct by value with the following fields populated:
   - p_ui_tile_data points to the ui_tile_data__small array of the input struct.
   - width_of__ui_tile_map is set to UI_TILE_MAP__SMALL__WIDTH.
   - height_of__ui_tile_map is set to UI_TILE_MAP__SMALL__HEIGHT.
   - catagory_size_of__ui_tile_map is set to UI_Tile_Map_Size__Small.
2. The input struct is not modified.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly delegates to get_ui_tile_map__wrapper, which constructs a UI_Tile_Map__Wrapper via positional struct initialization. The UI_Tile_Map__Wrapper struct has exactly four fields (p_ui_tile_data, width_of__ui_tile_map, height_of__ui_tile_map, catagory_size_of__ui_tile_map), and get_ui_tile_map__wrapper initializes all four — no member is omitted and no reordering occurs. The values are correctly sourced: the tile data array pointer and flags pointer come from the input UI_Tile_Map__Small struct, and the dimensions and size category come from the appropriate constants and enum value for the Small size.

Implementation Correctness:
Type compatibility — all argument types match their parameter types exactly:
  - p_ui_tile_map__small->ui_tile_data__small is UI_Tile_Raw[] which decays to UI_Tile_Raw *, matching the UI_Tile_Raw * parameter.
  - &p_ui_tile_map__small->ui_tile_map__flags is UI_Tile_Map__Flags * (uint8_t *), matching the UI_Tile_Map__Flags * parameter.
  - UI_TILE_MAP__SMALL__WIDTH and UI_TILE_MAP__SMALL__HEIGHT are integer macro constants compatible with Quantity__u32 (uint32_t).
  - UI_Tile_Map_Size__Small is an enum value of type UI_Tile_Map_Size, matching the parameter type.
  No implicit conversions or truncation occur.
No undefined behavior — no pointer arithmetic, no null dereference (null pointer would be a precondition violation by the caller), no type punning, no out-of-bounds access.
No validation is performed, which is appropriate for a low-level inline conversion function. The caller is responsible for ensuring p_ui_tile_map__small is valid.
Note: get_ui_tile_map__wrapper accepts a UI_Tile_Map__Flags * parameter but does not use it in the struct initializer, as UI_Tile_Map__Wrapper has no flags field. This is a design decision in get_ui_tile_map__wrapper, not a bug in this function.

Side Effects:
No side effects. The function only reads from the input struct and returns a new UI_Tile_Map__Wrapper value by copy. No state is mutated.
