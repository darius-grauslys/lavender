set_tile_logic_record_as__without_ground — core/include/world/tile_logic_record.h

Sets the TILE_LOGIC_FLAG__IS_WITHOUT_GROUND bit in the tile logic record's flags field, marking the tile as lacking ground.

Pre-conditions:
1. p_tile_logic_record must be a non-null pointer to a valid, writable Tile_Logic_Record object.
2. The caller is responsible for ensuring p_tile_logic_record points to allocated memory; no null check is performed (consistent with all sibling functions in this header).

Post-conditions:
1) p_tile_logic_record->tile_logic_flags__u8 has the TILE_LOGIC_FLAG__IS_WITHOUT_GROUND bit set (BIT(2)).
2) The function returns true (the result of |= is always non-zero since at least one bit is set), indicating the flag was successfully applied.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly uses bitwise OR-assignment (|=) to set the IS_WITHOUT_GROUND flag on the tile logic record's flags field. This is the standard pattern for setting a flag bit and matches the semantic intent of marking a tile as without ground. The companion function set_tile_logic_record_as__with_ground correctly clears the same bit using &= ~, confirming the intended usage pattern.

Implementation Correctness:
Type compatibility — tile_logic_flags__u8 is of type Tile_Logic_Flags__u16 (uint16_t), and TILE_LOGIC_FLAG__IS_WITHOUT_GROUND is BIT(2) which expands to (1U) << 2, a uint16_t-compatible value. The |= operation is type-safe with no implicit conversions or truncation.
Undefined behavior — no pointer arithmetic, no null dereference (assuming caller guarantees non-null), no type punning, no out-of-bounds access. The only dereference is of p_tile_logic_record->tile_logic_flags__u8, which is valid if the pointer is valid.
Validation — no validation is performed, but this is appropriate for a low-level inline flag setter. Validation is the caller's responsibility, consistent with all other functions in this header (e.g., set_tile_logic_record_as__unpassable, set_tile_logic_record_as__sight_blocking).

Side Effects:
Mutates p_tile_logic_record->tile_logic_flags__u8 by setting the TILE_LOGIC_FLAG__IS_WITHOUT_GROUND bit (BIT(2)). No other state is modified. No side effects beyond this single field write.
