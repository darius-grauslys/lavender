initialize_ui_tile_map__medium_as__deallocated — core/source/ui/ui_tile_map.c

Resets a UI_Tile_Map__Medium struct to its deallocated/initial state by clearing the flags and zeroing the entire tile data array.

Pre-conditions:
1. p_ui_tile_map__medium must be a non-null pointer to a writable UI_Tile_Map__Medium object.
2. The struct fields (ui_tile_map__flags and ui_tile_data__medium) are assumed to be uninitialized or in any prior state; this function does not read them.
3. UI_TILE_MAP__MEDIUM__WIDTH and UI_TILE_MAP__MEDIUM__HEIGHT must be defined (platform-specific constants, expected to be positive integers).

Post-conditions:
1. p_ui_tile_map__medium->ui_tile_map__flags is set to UI_TILE_MAP__FLAGS__NONE (0), clearing the IS_ALLOCATED flag.
2. p_ui_tile_map__medium->ui_tile_data__medium is zeroed — every UI_Tile_Raw element is set to 0, which corresponds to UI_Tile_Kind__None (0).

Correctness Verdict: Correct

Semantic Alignment:
This function performs Lavender-style initialization (pool cleanup / reset to deallocated state), NOT RAII. The name and the "_as__deallocated" suffix confirm this intent: it resets the struct to a clean, unallocated state suitable for return to a free pool or reuse.

The UI_Tile_Map__Medium struct has exactly two fields:
  1. UI_Tile_Map__Flags ui_tile_map__flags
  2. UI_Tile_Raw ui_tile_data__medium[UI_TILE_MAP__MEDIUM__WIDTH * UI_TILE_MAP__MEDIUM__HEIGHT]

Both fields are assigned:
  - ui_tile_map__flags is directly assigned UI_TILE_MAP__FLAGS__NONE.
  - ui_tile_data__medium is zeroed via memset with UI_Tile_Kind__None (value 0).

The memset correctly fills the byte representation of the array. Since UI_Tile_Raw is u16 and UI_Tile_Kind__None is 0, each 16-bit element is zeroed, which is the correct "none" representation. The size calculation sizeof(UI_Tile_Raw) * UI_TILE_MAP__MEDIUM__WIDTH * UI_TILE_MAP__MEDIUM__HEIGHT correctly computes the total byte size of the array.

Implementation Correctness:
Type compatibility — p_ui_tile_map__medium is UI_Tile_Map__Medium*, which matches the parameter type exactly. The assignment of UI_TILE_MAP__FLAGS__NONE (macro for 0) to ui_tile_map__flags (UI_Tile_Map__Flags, a uint8_t) is type-safe. The memset's second argument is UI_Tile_Kind__None (enum, value 0), which is implicitly converted to int as required by memset's signature — this is correct and safe. The third argument is a size_t-compatible expression computing total bytes.
Undefined behavior — no pointer arithmetic, no null dereference (caller provides valid pointer), no type punning, no out-of-bounds access. The memset fills exactly the declared array size.
Validation — no validation is needed. This is a low-level reset function; the caller is responsible for ensuring p_ui_tile_map__medium is a valid pointer.

Side Effects:
Mutates the struct pointed to by p_ui_tile_map__medium: sets ui_tile_map__flags to 0 and zeroes all elements of ui_tile_data__medium. No other observable side effects.