is_tile_logic_record__sight_blocking — core/include/world/tile_logic_record.h, lines 34-40

Checks whether the sight-blocking flag is set on a Tile_Logic_Record.

Pre-conditions:
1. p_tile_logic_record must be a non-null pointer to a valid, writable Tile_Logic_Record object.
2. The field tile_logic_flags__u8 (actually typed as Tile_Logic_Flags__u16 / uint16_t) may hold any bit pattern.

Post-conditions:
1. Returns true if the TILE_LOGIC_FLAG__IS_SIGHT_BLOCKING bit is set in p_tile_logic_record->tile_logic_flags__u8; returns false otherwise.
2. No state is mutated; the pointed-to struct is read-only.

Correctness Verdict: Correct

Semantic Alignment:
The implementation correctly checks the sight-blocking flag by performing a bitwise AND between the flags field and TILE_LOGIC_FLAG__IS_SIGHT_BLOCKING (defined as BIT(1) = 0x0002). The result of the AND is implicitly converted to bool — any non-zero value becomes true, and zero becomes false. This matches the semantic intent of querying whether the sight-blocking property is set.

Note: The field is named tile_logic_flags__u8 (suggesting uint8_t) but is actually declared as Tile_Logic_Flags__u16 (uint16_t) in the Tile_Logic_Record struct. This is a naming inconsistency but does not affect correctness, since the flag value fits within both u8 and u16 ranges.

Implementation Correctness:
Type compatibility — The parameter is Tile_Logic_Record*, and the field accessed is Tile_Logic_Flags__u16 (uint16_t). TILE_LOGIC_FLAG__IS_SIGHT_BLOCKING is BIT(1) = (1U << 1), an unsigned int. The bitwise AND promotes the uint16_t operand to int/unsigned int per integer promotion rules, and the result is implicitly converted to bool. No truncation or data loss occurs.
Undefined behavior — No pointer arithmetic, no null dereference (caller is responsible for passing a valid pointer, consistent with sibling functions in this file), no type punning, no out-of-bounds access.
Validation — No validation is needed within this function; it is a low-level query accessor. Ensuring p_tile_logic_record is non-null is the caller's responsibility, consistent with the pattern used by is_tile_logic_record__unpassable and other functions in this header.

Side Effects:
No side effects — the function is a pure read query. It does not modify the pointed-to struct or any global state.
