# copy_into_ui_tile_map

**File of origin:** `core/source/ui/ui_tile_map.c` (lines 213-224)

## Semantic

Copies a raw byte region of tile data (`length` bytes from `p_ui_tile__data`) into the tile map's backing data buffer starting at a byte `offset`.

## Pre-conditions

1. `p_ui_tile_map__wrapper` must be non-null.
2. `p_ui_tile_map__wrapper->p_ui_tile_data` must be a valid, non-null pointer to a sufficiently large allocated buffer.
3. `p_ui_tile__data` must be a valid, non-null pointer to at least `length` bytes of readable data.
4. `offset + length` must not exceed the total allocated size (in bytes) of the buffer pointed to by `p_ui_tile_map__wrapper->p_ui_tile_data`. The caller is responsible for ensuring this; the function performs no bounds checking.

## Post-conditions

1. `length` bytes from `p_ui_tile__data` are copied into the tile map's data buffer starting at byte offset `offset`.
2. The rest of the tile map's data buffer is unchanged (only the bytes in `[offset, offset + length)` are modified).

## Correctness Verdict

**Correct**

## Semantic Alignment

The implementation faithfully fulfills the semantic intent. The function casts `p_ui_tile_data` (of type `UI_Tile_Raw *`, i.e., `u16 *`) to `u8 *` to perform byte-level pointer arithmetic with the `offset` parameter. This is correct because `offset` and `length` are in units of bytes, not in units of `UI_Tile_Raw` elements. The cast to `u8 *` ensures that the offset is applied at the byte level rather than scaled by `sizeof(UI_Tile_Raw)`.

The redundant cast of `p_ui_tile__data` to `(u8*)` is harmless — `memcpy` accepts `void *` parameters, so the cast does not change the actual memory being copied.

## Implementation Correctness

- **Type compatibility:** The cast from `UI_Tile_Raw *` (`u16 *`) to `u8 *` is a valid pointer cast for byte-level arithmetic. `memcpy` receives `void *` parameters, so all pointer types are compatible.
- **Undefined behavior:** No broken pointer arithmetic, no null dereference (assuming pre-conditions hold), no type punning, no out-of-bounds access (assuming pre-conditions hold). The pointer arithmetic `((u8*)p_ui_tile_data) + offset` is well-defined as long as the resulting pointer stays within (or one past) the allocated object.
- **Validation:** The function performs no validation of its parameters. This is acceptable for a low-level utility function — bounds checking is the caller's responsibility. This is consistent with the function's role as a raw memory copy primitive. Other higher-level functions in the same file (e.g., `fill_ui_tile_map_in__this_region`) do perform bounds checking, but `copy_into_ui_tile_map` operates at a lower level and intentionally delegates validation to the caller.

## Side Effects

- Mutates the memory region pointed to by `p_ui_tile_map__wrapper->p_ui_tile_data`, overwriting `length` bytes starting at byte offset `offset` with the contents of `p_ui_tile__data`.
- Does not modify `p_ui_tile_map__wrapper` struct fields (width, height, flags, etc.).
- Does not modify `p_ui_tile__data`.
