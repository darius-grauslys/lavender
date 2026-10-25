set_tile_logic_record_as__sight_blocking — core/include/world/tile_logic_record.h

Sets the IS_SIGHT_BLOCKING flag on a Tile_Logic_Record's flags field via bitwise OR-assignment.

Pre-conditions:
1. p_tile_logic_record must be a non-null pointer to a valid, writable Tile_Logic_Record object. No null check is performed; passing NULL results in undefined behavior.
2. The pointed-to Tile_Logic_Record does not need to be in any particular initial state; the function only sets a single flag bit regardless of prior flag values.

Post-conditions:
1. The tile_logic_flags__u8 field of the Tile_Logic_Record has the TILE_LOGIC_FLAG__IS_SIGHT_BLOCKING bit (BIT(1)) set. All other bits remain unchanged.
2. The function returns true (the resulting flags value is always non-zero because the sight-blocking bit is set).

Correctness Verdict: Correct

Semantic Alignment:
The implementation correctly sets the IS_SIGHT_BLOCKING flag using bitwise OR-assignment (|=), which is the appropriate operation for setting a single bit in a bitfield. The flag constant TILE_LOGIC_FLAG__IS_SIGHT_BLOCKING is BIT(1) = 2, which is non-zero, so the resulting flags value is always non-zero and the function always returns true. This is consistent with the pattern used by the sibling "set" functions in the same file (e.g., set_tile_logic_record_as__unpassable, set_tile_logic_record_as__without_ground).

Implementation Correctness:
Type compatibility — tile_logic_flags__u8 is of type Tile_Logic_Flags__u16 (uint16_t), and TILE_LOGIC_FLAG__IS_SIGHT_BLOCKING is BIT(1) = (1U << 1) = 2U (unsigned int). The unsigned int value 2 fits within uint16_t with no truncation. The usual arithmetic conversions promote uint16_t to int, then to unsigned int for the OR operation, and the result is truncated back to uint16_t — all well-defined with no data loss. The return value (uint16_t) is implicitly converted to bool, which is well-defined: any non-zero value becomes true.
Undefined behavior — no pointer arithmetic, no null dereference (assuming the pre-condition is met), no type punning, no out-of-bounds access.
Validation — no validation is needed for this low-level inline function; it is the caller's responsibility to ensure p_tile_logic_record is valid, consistent with the pattern of all sibling functions in the file.

Side Effects:
Mutates the tile_logic_flags__u8 field of the pointed-to Tile_Logic_Record by setting the IS_SIGHT_BLOCKING bit. This is the function's only observable side effect.