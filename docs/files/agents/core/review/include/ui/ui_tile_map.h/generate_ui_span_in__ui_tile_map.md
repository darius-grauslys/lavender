generate_ui_span_in__ui_tile_map — core/source/ui/ui_tile_map.c

Renders a UI_Tile_Span into a UI_Tile_Map__Wrapper at a specified position, scaling each span tile by the span's 8x8 tile size and clipping out-of-bounds regions.

Pre-conditions:
1. p_ui_tile_map__wrapper must be a non-null pointer to a valid UI_Tile_Map__Wrapper with allocated p_ui_tile_data and non-zero width and height.
2. p_ui_tile_span must be a non-null pointer to a valid UI_Tile_Span with size_of__ui_tile_in__8x8_tiles__u8 set to a positive value.
3. width_of__ui_tile_span__u32 and height_of__ui_tile_span__u32 define the span dimensions in logical tiles (not 8x8 tiles).
4. index_x__u32 is the starting x position in the tile map (from the left). Must be less than the tile map width to produce any visible output.
5. index_y__u32 is the starting y position in the tile map (from the bottom). Must be less than the tile map height to produce any visible output.
6. The sum index_x__u32 + (width_of__ui_tile_span__u32 * size_of__ui_tile_in__8x8_tiles__u8) must not overflow u32.
7. The sum index_y__u32 + (height_of__ui_tile_span__u32 * size_of__ui_tile_in__8x8_tiles__u8) must not overflow u32.

Post-conditions:
1. p_ui_tile_map__wrapper->p_ui_tile_data is mutated: in-bounds tiles of the span are written to the tile map at the computed (x, y) positions using row-major indexing (x + y * width).
2. Out-of-bounds tiles (where x >= width or y >= height after unsigned wraparound) are skipped via the continue statements.
3. p_ui_tile_span is read but not modified.
4. p_ui_tile_map__wrapper's width, height, and p_ui_tile_data pointer are read but not modified.

Correctness Verdict: Correct

Semantic Alignment:
The function fulfills its semantic intent. It iterates over the span's tiles in 8x8 tile units (width * size to height * size), computes the corresponding (x, y) position in the tile map, and writes the appropriate UI_Tile_Raw value retrieved from the span via get_ui_tile_of__ui_tile_span and get_ui_tile_raw_from__ui_tile.

The y-coordinate is computed as height - (index_y__u32 + y_offset) - 1, which renders the span from bottom to top. This is consistent with the span's internal coordinate system where index_y_of__ui_tile_span__u32 = 0 corresponds to the bottom edge (as seen in get_ui_tile_of__ui_tile_span where is_on_bottom_edge = index_y == 0).

The x-coordinate is computed as index_x__u32 + x_offset, rendering left to right, consistent with the span's x coordinate system where index_x_of__ui_tile_span__u32 = 0 is the left edge.

The tile map indexing uses row-major order (x + y * width), which is the correct layout for the p_ui_tile_data array as evidenced by fill_ui_tile_map and fill_ui_tile_map_in__this_region.

Implementation Correctness:
Type compatibility — all parameter types match their usage. Index__u32 (uint32_t) is used for loop indices and computed coordinates. Quantity__u32 (uint32_t) is used for span dimensions. u32 is used for computed x and y coordinates. All are compatible.

Undefined behavior — no null dereference (assumes valid input per codebase convention), no out-of-bounds access (bounds checks via continue are present for both x and y), no type punning, no broken pointer arithmetic. The unsigned underflow in the y computation (height - (start + offset) - 1) is handled correctly: when start + offset >= height, the result wraps to a large unsigned value that is caught by the y >= height check.

Validation — no validation of pointer parameters, consistent with the codebase convention (e.g., fill_ui_tile_map, fill_ui_tile_map_in__this_region). The caller is responsible for ensuring p_ui_tile_map__wrapper and p_ui_tile_span are valid.

Side Effects:
Mutates p_ui_tile_map__wrapper->p_ui_tile_data by writing UI_Tile_Raw values to in-bounds positions. No other side effects. Does not modify p_ui_tile_span or any fields of p_ui_tile_map__wrapper other than the p_ui_tile_data array contents.
