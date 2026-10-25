set_inventory_container__x_in__uuid — core/include/inventory/inventory.h

Sets the X-axis component of a container UUID by clearing the X-axis bitfield and writing the new value into it.

Pre-conditions:
1. p_uuid must be a non-null pointer to a writable Identifier__u32 (u32).
2. x is a u16; only the lower 11 bits are meaningful (the X-axis field is 11 bits wide, bits 11–21). Values exceeding 2047 will be silently truncated by the mask.

Post-conditions:
1. The X-axis bitfield (bits 11–21) of *p_uuid is updated to the value of x (masked to 11 bits, shifted left by 11).
2. All other bits in *p_uuid (item stack index, container/entity flag, Z-axis, Y-axis) are preserved.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly implements a bitfield setter for the X-axis component of the inventory UUID. The UUID layout (from defines.h) is:
  [31..26] [25] [24..22] [21..11] [10..0]
                 z-axis   x-axis   y-axis

The X-axis field occupies bits 11–21 (11 bits), with a bit shift of 11. The function:
- First clears the X-axis bits via `*p_uuid &= ~UUID_MASK__INVENTORY__CONTAINER__X_AXIS`
- Then sets them via `*p_uuid |= (UUID_MASK__INVENTORY__CONTAINER__X_AXIS & (x << UUID_BIT_SHIFT__INVENTORY__CONTAINER__X_AXIS))`

This is consistent with the companion getter `get_inventory_container__x_from__uuid` which extracts the same field by masking and shifting right by 11. The pattern matches the Z-axis setter (`set_inventory_container__z_in__uuid`) which uses the same clear-then-set approach with the appropriate shift.

The `& UUID_MASK__INVENTORY__CONTAINER__X_AXIS` in the second statement is redundant (since the clear already removed those bits and the mask only covers the same range), but it is harmless and serves as defensive programming to ensure no stray bits leak in from the shift.

Implementation Correctness:
Type compatibility — x is u16; during `x << UUID_BIT_SHIFT__INVENTORY__CONTAINER__X_AXIS` (shift of 11), x is promoted to int (at least 32 bits), so no overflow occurs. The result is then ANDed with the u32 mask, producing a u32 value compatible with Identifier__u32. No implicit conversions or truncation beyond the intended field width.
Undefined behavior — no pointer arithmetic, no null dereference (p_uuid null-check is caller's responsibility), no type punning, no out-of-bounds access. The shift amount (11) is well within the range of a 32-bit integer.
Validation — no validation is needed for this low-level bitfield setter. The caller (e.g., get_uuid_for__container) is responsible for ensuring p_uuid is valid and x is within range.

Side Effects:
Mutates *p_uuid by clearing and then setting the X-axis bitfield (bits 11–21). All other bits in the UUID are preserved.
