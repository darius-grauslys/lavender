set_ui_tile_map_flags_as__deallocated — core/include/ui/ui_tile_map.h

Clears the IS_ALLOCATED flag bit from a UI_Tile_Map__Flags value, marking the tile map as deallocated while preserving all other flag bits.

Pre-conditions:
1. p_ui_tile_map__flags must be a non-null pointer to a writable UI_Tile_Map__Flags (uint8_t) object.

Post-conditions:
1. The UI_TILE_MAP__FLAG__IS_ALLOCATED bit (BIT(0)) in *p_ui_tile_map__flags is cleared (set to 0).
2. All other bits in *p_ui_tile_map__flags remain unchanged.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly clears only the IS_ALLOCATED flag bit while preserving all other bits in the flags field. The bitwise AND with the complement of the flag (~BIT(0)) is the standard C idiom for clearing a specific bit. The implementation matches the semantic intent of marking the tile map as deallocated, and is the precise inverse of the companion function set_ui_tile_map_flags_as__allocated, which sets the same bit via |=.

Lavender-Specific Semantics:
This function is a low-level flag manipulation utility, not a Lavender-style initialization function. It does not reset a struct to its initial conditions or return elements to a free pool. The Lavender initialization pattern (setting flags to UI_TILE_MAP__FLAGS__NONE and clearing tile data) is instead handled by the initialize_ui_tile_map__*_as__deallocated functions in core/source/ui/ui_tile_map.c. This function provides granular bit-level control for clearing the IS_ALLOCATED flag, complementing the broader initialization/deallocation pattern.

Implementation Correctness:
- Type compatibility: p_ui_tile_map__flags is UI_Tile_Map__Flags *, which is uint8_t *. UI_TILE_MAP__FLAG__IS_ALLOCATED is BIT(0) which expands to ((1U) << (0)), a 32-bit unsigned int. The ~ operator produces 0xFFFFFFFE (for 32-bit unsigned int). Due to integer promotion, the uint8_t value is promoted to int before the AND operation, then the result is assigned back to uint8_t with truncation. This correctly clears bit 0 and preserves bits 1-7. No implicit conversions or truncation affect correctness.
- Undefined behavior: No pointer arithmetic, no null dereference (null is a pre-condition violation, not UB in this inline function), no type punning, no out-of-bounds access.
- Validation: No validation is needed — this is a low-level flag manipulation function. Null pointer checking is the caller's responsibility, consistent with the codebase pattern for static inline functions (e.g., set_ui_tile_map_flags_as__allocated, is_ui_tile_map_flags__allocated).

Side Effects:
The only side effect is modifying the value pointed to by p_ui_tile_map__flags by clearing the IS_ALLOCATED bit (BIT(0)).
