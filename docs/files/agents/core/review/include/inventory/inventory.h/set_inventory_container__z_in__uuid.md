set_inventory_container__z_in__uuid — core/include/inventory/inventory.h

Sets the Z-axis bits (bits 22-24) of a UUID to the value of z, preserving all other bits.

Pre-conditions:
1. p_uuid must be a non-null pointer to a writable Identifier__u32 (uint32_t) object.
2. z is a u16 (uint16_t) but the Z-axis field is only 3 bits wide (bits 22-24), so valid values are 0-7. Values outside this range are silently truncated by the mask.
3. The caller is responsible for ensuring z is within the valid range for the 3-bit field (0-7).

Post-conditions:
1. The Z-axis bits (bits 22-24) of *p_uuid are set to (z & 0x7) (i.e., the lower 3 bits of z, shifted into position).
2. All other bits of *p_uuid are unchanged.

Correctness Verdict: Correct

Semantic Alignment:
The implementation correctly fulfills the semantic intent of setting the Z-axis bits in the UUID. It first clears the Z-axis bits using `&= ~UUID_MASK__INVENTORY__CONTAINER__Z_AXIS`, then sets them using `|= (UUID_MASK__INVENTORY__CONTAINER__Z_AXIS & (z << UUID_BIT_SHIFT__INVENTORY__CONTAINER__Z_AXIS))`. The mask ensures only the 3-bit field (bits 22-24) is affected, and the shift correctly positions the z value. This matches the sibling functions set_inventory_container__x_in__uuid and set_inventory_container__y_in__uuid, which use the same pattern for their respective axes.

Implementation Correctness:
Type compatibility — z is u16 but the field is only 3 bits wide (0-7). The mask UUID_MASK__INVENTORY__CONTAINER__Z_AXIS (MASK(3) << 22) truncates values > 7, which is the expected behavior for a 3-bit field. The parameter type does not exactly match the field width, but the mask handles truncation correctly.
Potential undefined behavior — the expression `z << 22` where z is u16 (promoted to int) can cause undefined behavior for z >= 512, because shifting a positive signed int into or past the sign bit (bit 31) is UB in C. For example, 512 << 22 = 0x80000000, which sets the sign bit of int. For z in 0-7 (the valid range), no UB occurs. This is the same pattern used in the sibling x-axis setter (x << 11), so it is a consistent design choice. The caller (get_uuid_for__container) passes tile_vector__3i32.z__i32 (i32) which is implicitly converted to u16; valid tile coordinates should be within range.
No validation is needed — this is a low-level bit manipulation function. The caller is responsible for ensuring z is within the valid range (0-7). A defensive fix would be to cast z to Identifier__u32 before the shift: `(Identifier__u32)z << UUID_BIT_SHIFT__INVENTORY__CONTAINER__Z_AXIS`, which would make the shift well-defined for all u16 values.

Side Effects:
Mutates *p_uuid: the Z-axis bits (bits 22-24) are cleared and then set to the lower 3 bits of z. All other bits are preserved.
