# fill_ui_tile_map

**File of origin:** `core/source/ui/ui_tile_map.c` (lines 103–123)

## Semantic

Fills every cell of a UI tile map (represented by a `UI_Tile_Map__Wrapper`) with a single `UI_Tile` value, converting the tile to its endian-proof `UI_Tile_Raw` representation and writing it across the full width × height grid in row-major order.

## Pre-conditions

1. `p_ui_tile_map__wrapper` must be non-null.
2. `p_ui_tile_map__wrapper->p_ui_tile_data` must be non-null and point to a buffer of at least `width_of__ui_tile_map * height_of__ui_tile_map` contiguous `UI_Tile_Raw` elements.
3. `p_ui_tile_map__wrapper->width_of__ui_tile_map` and `p_ui_tile_map__wrapper->height_of__ui_tile_map` must accurately reflect the utilized dimensions of the allocated tile data buffer (i.e., they must not exceed the allocation category's maximum dimensions).
4. The wrapper should have been initialized via `initialize_ui_tile_map__wrapper` (or otherwise have its fields set to valid values) before calling this function.

## Post-conditions

1. Every element in `p_ui_tile_map__wrapper->p_ui_tile_data` from index `0` to `width * height - 1` is set to `get_ui_tile_raw_from__ui_tile(&ui_tile)`.
2. `p_ui_tile_map__wrapper->width_of__ui_tile_map` and `p_ui_tile_map__wrapper->height_of__ui_tile_map` are unchanged (the function only writes to the tile data buffer).
3. The `ui_tile_map__flags` field of the underlying `UI_Tile_Map__Small/Medium/Large` is not touched (this function operates solely on the wrapper's data pointer).

## Correctness Verdict

**Correct**

## Semantic Alignment

The implementation fulfills the semantic intent. The function iterates over all rows (`0` to `height - 1`) and all columns (`0` to `width - 1`), computing the linear index as `index_of__x + index_of__y * width_of__ui_tile_map`, which is the standard row-major ordering for a 2D grid stored in a 1D array. Each cell is assigned the raw tile value obtained from `get_ui_tile_raw_from__ui_tile(&ui_tile)`, which packs the tile kind and flags into a `UI_Tile_Raw` (`u16`). The computation matches the intended behavior of filling the entire map with a uniform tile.

## Implementation Correctness

- **Type compatibility:** All types are compatible. `Index__u32` and `Quantity__u32` are both `uint32_t`, so the loop bound comparisons are type-safe. The array index expression uses `uint32_t` arithmetic, which is valid for indexing into a `UI_Tile_Raw *` (`u16 *`) buffer. The result of `get_ui_tile_raw_from__ui_tile` is `UI_Tile_Raw` (`u16`), which matches the element type of `p_ui_tile_data`.
- **Undefined behavior:** No broken pointer arithmetic, no null dereference (provided pre-conditions hold), no type punning, and no out-of-bounds access. The loop bounds use `<` comparisons, so the maximum index written is `(width - 1) + (height - 1) * width = width * height - 1`, which is within bounds for a buffer of `width * height` elements.
- **Validation:** No null-pointer or bounds validation is performed within the function. This is consistent with the codebase design philosophy — validation is the caller's responsibility (a helper `is_ui_tile_map__wrapper__valid` exists for this purpose). The function's role is purely to fill the map, not to validate it.

## Side Effects

- **Mutates:** `p_ui_tile_map__wrapper->p_ui_tile_data[0]` through `p_ui_tile_map__wrapper->p_ui_tile_data[width * height - 1]`, setting each element to the raw representation of `ui_tile`.
- **Does not mutate:** `p_ui_tile_map__wrapper->width_of__ui_tile_map`, `p_ui_tile_map__wrapper->height_of__ui_tile_map`, `p_ui_tile_map__wrapper->catagory_size_of__ui_tile_map`, or any flags fields.
- **No other side effects:** No I/O, no global state modification, no allocations.
