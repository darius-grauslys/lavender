get_ui_tile_of__ui_tile_span — core/source/ui/ui_tile_span.c, lines 68-116

Returns a const pointer to the UI_Tile within a UI_Tile_Span that corresponds to a given (x, y) position within the span's grid, selecting corners, edges, or fill based on the position's location relative to the grid border.

Pre-conditions:
1. p_ui_tile_span must be a non-null pointer to a valid UI_Tile_Span struct.
2. width_of__ui_tile_span__u32 must be greater than 0.
3. height_of__ui_tile_span__u32 must be greater than 0.
4. size_of__ui_tile_in__8x8_tiles__u8 (within the struct) must be greater than 0.
5. index_x_of__ui_tile_span__u32 must be within [0, width_of__ui_tile_span__u32 * size_of__ui_tile_in__8x8_tiles__u8 - 1].
6. index_y_of__ui_tile_span__u32 must be within [0, height_of__ui_tile_span__u32 * size_of__ui_tile_in__8x8_tiles__u8 - 1].

Post-conditions:
1. Returns a const pointer to a UI_Tile that is a member of the p_ui_tile_span struct. The specific member depends on the position:
   - (0, 0) → ui_tile__corner__bottom_left
   - (0, maxHeight) → ui_tile__corner__top_left
   - (maxWidth, 0) → ui_tile__corner__bottom_right
   - (maxWidth, maxHeight) → ui_tile__corner__top_right
   - On top or bottom edge (non-corner) → ui_tile__edge__top or ui_tile__edge__bottom
   - On left or right edge (non-corner) → ui_tile__edge__left or ui_tile__edge__right
   - Interior → ui_tile__fill
2. No mutation of p_ui_tile_span occurs; the function is read-only.

Correctness Verdict: Correct

Semantic Alignment:
The implementation correctly fulfills the semantic intent of selecting the appropriate tile from a bordered grid span. The grid's total dimensions are computed as width * tile_size and height * tile_size. The function checks top edge first (highest y), then bottom edge (y == 0), then left edge (x == 0), then right edge (max x), and finally defaults to fill. Corner cases are handled before their respective edges, ensuring corners take priority. All eight named struct members (4 corners, 4 edges) and the fill are accessible through the correct union aliases.

Implementation Correctness:
Type compatibility — index_x_of__ui_tile_span__u32 (Index__u32 / uint32_t) is compared against width_of__ui_tile_span__u32 (Quantity__u32 / uint32_t) multiplied by size_of__ui_tile_in__8x8_tiles__u8 (u8 / uint8_t). The u8 is promoted to uint32_t during multiplication, and the subtraction of 1 is performed in uint32_t arithmetic. No implicit conversions or truncation occur. The return type (const UI_Tile *) matches the address-of operations on struct members of type UI_Tile.
No undefined behavior — no pointer arithmetic, no null dereference (pre-condition requires non-null), no type punning, no out-of-bounds array access. The union member access is well-defined since all members are of the same type (UI_Tile).
No validation is performed within the function — this is appropriate for a low-level query function. The caller is responsible for ensuring pre-conditions hold, including non-zero dimensions and valid indices.

Side Effects:
No side effects — the function is a pure query. It reads from p_ui_tile_span and returns a const pointer into the struct's memory without modifying any state.
