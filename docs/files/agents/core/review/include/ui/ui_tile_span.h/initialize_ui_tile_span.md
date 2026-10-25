initialize_ui_tile_span — core/source/ui/ui_tile_span.c

## Semantic
Copies four corner tiles, four edge tiles, and a fill tile into a `UI_Tile_Span` struct, then sets the tile size field to a default of 1.

## Pre-conditions
1. `p_ui_tile_span` must not be NULL.
2. `ui_tile__corners` must point to an array of at least 4 elements (matching `UI_TILE_SPAN__QUANTITY_OF__CORNERS`).
3. `ui_tile__edges` must point to an array of at least 4 elements (matching `UI_TILE_SPAN__QUANTITY_OF__EDGES`).

## Post-conditions
1. `p_ui_tile_span->ui_tile__corners[0..3]` are assigned from `ui_tile__corners[0..3]`.
2. `p_ui_tile_span->ui_tile__edges[0..3]` are assigned from `ui_tile__edges[0..3]`.
3. `p_ui_tile_span->ui_tile__fill` is assigned from `ui_tile__fill`.
4. `p_ui_tile_span->size_of__ui_tile_in__8x8_tiles__u8` is set to 1.

## Correctness Verdict
Correct

## Semantic Alignment
The function performs Lavender-style initialization (not RAII). It populates a struct with provided tile values rather than acquiring any external resource. All fields of the `UI_Tile_Span` struct are assigned: the corners array (4 elements), the edges array (4 elements), the fill tile, and the size field. No struct member is omitted, and no reordering occurs. The loop bounds use the `UI_TILE_SPAN__QUANTITY_OF__CORNERS` (4) and `UI_TILE_SPAN__QUANTITY_OF__EDGES` (4) macros, which exactly match the array dimensions declared in the struct definition.

## Implementation Correctness
- Type compatibility: The parameters `ui_tile__corners[4]` and `ui_tile__edges[4]` are arrays of `UI_Tile`, and the struct fields `ui_tile__corners` and `ui_tile__edges` are also arrays of `UI_Tile`. Assignment is type-exact with no implicit conversion or truncation.
- The `ui_tile__fill` parameter is `UI_Tile`, matching the struct field `ui_tile__fill` (also `UI_Tile`). No conversion occurs.
- The `size_of__ui_tile_in__8x8_tiles__u8` field is `u8`, and the literal `1` is an `int` that is implicitly converted to `u8`. This is safe as the value 1 fits in a `u8` with no truncation.
- No undefined behavior: no null pointer dereference (caller's responsibility to pass valid pointers), no out-of-bounds access (loop bounds match array sizes), no type punning.
- Validation: the function does not validate its parameters, which is consistent with the Lavender engine convention where validation is the caller's responsibility.

## Side Effects
- Mutates `p_ui_tile_span` by writing to all of its fields: `ui_tile__corners`, `ui_tile__edges`, `ui_tile__fill`, and `size_of__ui_tile_in__8x8_tiles__u8`.
- Does not read from or modify any other memory.
- Does not perform any I/O or call any external functions.