# Function Review: `initialize_ui_tile_span__with_ui_tile_size`

**File of origin:** `core/source/ui/ui_tile_span.c` (lines 54–66)

---

## Semantic

Initializes a `UI_Tile_Span` struct by copying four corner tiles, four edge tiles, and one fill tile from caller-provided arrays/values into the struct, then sets the tile size field to a caller-specified value. This is a variant of `initialize_ui_tile_span` that allows overriding the default tile size of 1 with an arbitrary size.

---

## Pre-conditions

1. `p_ui_tile_span` must be a non-null pointer to a valid, writable `UI_Tile_Span` struct.
2. `ui_tile__corners` must point to a valid array of at least `UI_TILE_SPAN__QUANTITY_OF__CORNERS` (4) `UI_Tile` elements.
3. `ui_tile__edges` must point to a valid array of at least `UI_TILE_SPAN__QUANTITY_OF__EDGES` (4) `UI_Tile` elements.
4. `ui_tile__fill` is passed by value; no pointer constraints apply.
5. `size_of__ui_tile_in__8x8_tiles__u8` is a `Quantity__u8` (`uint8_t`) with no explicit range validation performed by this function; semantically it should represent a valid tile dimension (typically >= 1).

---

## Post-conditions

1. All four corner tiles are copied from `ui_tile__corners[0..3]` into `p_ui_tile_span->ui_tile__corners[0..3]`.
2. All four edge tiles are copied from `ui_tile__edges[0..3]` into `p_ui_tile_span->ui_tile__edges[0..3]`.
3. The fill tile is set: `p_ui_tile_span->ui_tile__fill = ui_tile__fill`.
4. The size field is set to the caller-specified value: `p_ui_tile_span->size_of__ui_tile_in__8x8_tiles__u8 = size_of__ui_tile_in__8x8_tiles__u8`.

---

## Correctness Verdict

**Correct**

---

## Semantic Alignment

The function faithfully fulfills its semantic intent. It delegates to `initialize_ui_tile_span` to copy all tile data (corners, edges, fill) and then overrides the `size_of__ui_tile_in__8x8_tiles__u8` field with the user-provided value instead of the default of 1 that `initialize_ui_tile_span` sets. All struct fields are assigned — no member is omitted and no reordering occurs. The struct `UI_Tile_Span` contains: a union of 4 corner tiles, a union of 4 edge tiles, a fill tile, and a size byte — all are populated by this function (via the delegated call and the final assignment).

### Lavender-Specific Semantics: Initialization ≠ RAII

This function is named with the "initialize" prefix but does **not** perform Lavender-style pool cleanup (resetting to defaults). Instead, it is a **population/initialization-by-construction** function — it sets struct fields to caller-provided values rather than clearing them. This is consistent with the codebase pattern where `initialize_ui_tile_span` (without `_as__empty`) also populates from parameters, while `initialize_ui_tile_span_as__empty` performs the true Lavender-style reset-to-defaults for pool reuse. The naming convention is internally consistent: `_as__empty` variants clear/reset, non-`_as__empty` variants construct with provided data.

---

## Implementation Correctness

- **Type compatibility:** The parameter `size_of__ui_tile_in__8x8_tiles__u8` is of type `Quantity__u8`, which is a typedef for `uint8_t`. The struct field `size_of__ui_tile_in__8x8_tiles__u8` is of type `u8`, which is also a typedef for `uint8_t`. The types match exactly — no implicit conversions or truncation.
- **Undefined behavior:** No pointer arithmetic, no null dereference (null-checking is the caller's responsibility), no type punning, and no out-of-bounds access. The delegated `initialize_ui_tile_span` uses loop bounds of `UI_TILE_SPAN__QUANTITY_OF__CORNERS` (4) and `UI_TILE_SPAN__QUANTITY_OF__EDGES` (4), which match the array sizes in both the parameter declarations and the struct definition.
- **Validation:** No input validation is performed on the size parameter or pointer arguments. This is appropriate for this function's role as a low-level struct initializer — validation of semantic correctness (e.g., size >= 1) is the caller's responsibility.

---

## Side Effects

- **Mutates** `p_ui_tile_span`: copies all four corner tiles, all four edge tiles, the fill tile, and sets the `size_of__ui_tile_in__8x8_tiles__u8` field to the provided value. No other memory or global state is affected.
