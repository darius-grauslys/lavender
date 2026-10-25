set_inventory_container__y_in__uuid — core/include/inventory/inventory.h, lines 166-171

Sets the Y-axis component of a container UUID identifier.

Pre-conditions:
1. p_uuid must be a non-null pointer to a writable Identifier__u32 (u32).
2. y is a u16; only the lower 11 bits are significant. Values exceeding 11 bits are silently truncated by the mask.
3. The UUID layout reserves bits [10..0] for the Y-axis component (per the layout comment in defines.h: [31..26] item_stack, [25] entity/container flag, [24..22] z-axis, [21..11] x-axis, [10..0] y-axis).

Post-conditions:
1. The Y-axis bits [10..0] of *p_uuid are cleared and then set to the lower 11 bits of y.
2. All other bits of *p_uuid are preserved (the clear-and-set pattern only affects the Y-axis field).

Correctness Verdict: Correct

Semantic Alignment:
The function correctly implements bit-field insertion for the Y-axis component of a container UUID. The Y-axis occupies bits [10..0], which means the bit shift is 0. The implementation `*p_uuid |= (UUID_MASK__INVENTORY__CONTAINER__Y_AXIS & y)` is equivalent to `*p_uuid |= (UUID_MASK__INVENTORY__CONTAINER__Y_AXIS & (y << 0))`, matching the pattern used by the X and Z setters (which use explicit left-shifts because their fields are at non-zero bit offsets). The companion getter `get_inventory_container__y_from__uuid` also omits a right-shift, confirming this is intentional and consistent. The clear-then-set pattern ensures only the Y-axis bits are modified, leaving all other UUID fields intact.

Implementation Correctness:
Type compatibility — p_uuid is Identifier__u32 * (u32 pointer), matching the u32 UUID type. The parameter y is u16, which is wider than the 11-bit field; the mask UUID_MASK__INVENTORY__CONTAINER__Y_AXIS (MASK(11) = 0x7FF) truncates to 11 bits. No implicit conversion issues arise because the mask handles truncation explicitly.
Undefined behavior — no pointer arithmetic, no null dereference (caller must provide non-null p_uuid), no type punning, no out-of-bounds access. The bitwise operations are well-defined for u32.
Validation — no validation is needed within this function; it is a low-level bit manipulation helper. The caller (get_uuid_for__container) is responsible for providing valid inputs.

Side Effects:
Mutates the u32 value pointed to by p_uuid: clears bits [10..0] and writes the lower 11 bits of y into them. All other bits are preserved.
