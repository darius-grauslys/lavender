get_inventory_container__x_from__uuid — core/include/inventory/inventory.h

Extracts the X-axis coordinate from a container UUID by masking and right-shifting the X-axis bitfield.

Pre-conditions:
1. uuid is an Identifier__u32 (uint32_t) representing a valid container UUID. No specific validity constraint beyond being a 32-bit unsigned integer.

Post-conditions:
1. Returns a u16 containing the X-axis value stored in bits 11–21 of the UUID (range 0–2047). All other bits in the return value are guaranteed to be zero.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly extracts the X-axis coordinate from the container UUID. The UUID layout for containers allocates bits 11–21 (11 bits) for the X-axis value, with UUID_BIT_SHIFT__INVENTORY__CONTAINER__X_AXIS = 11 and UUID_MASK__INVENTORY__CONTAINER__X_AXIS = (MASK(11) << 11) = 0xFFE00. The implementation masks the UUID to isolate bits 11–21, then right-shifts by 11 to produce the value in the range 0–2047. This is the proper inverse of set_inventory_container__x_in__uuid, which writes the X value via (x << 11) masked into the same bitfield. The sibling getters (get_inventory_container__y_from__uuid and get_inventory_container__z_from__uuid) follow the same pattern, and this function is consistent with them.

Implementation Correctness:
Type compatibility — uuid is Identifier__u32 (uint32_t). The mask UUID_MASK__INVENTORY__CONTAINER__X_AXIS is computed as (MASK(11) << 11), where MASK(n) = ((u32)BIT(n) - 1), so the mask is u32. The bitwise AND of two u32 values yields u32. The right-shift by 11 (an int) on a u32 yields u32. The result is then implicitly converted to u16 for the return. Since the masked-and-shifted value can be at most 0x7FF (2047), it fits in u16 without truncation. No data loss occurs.
No undefined behavior — no pointer arithmetic, no null dereference, no type punning, no out-of-bounds access. The shift amount (11) is well-defined for a u32 value. The right operand of >> is non-negative and less than the bit-width of the left operand.
No validation is needed — this is a pure bit-extraction utility. The caller is responsible for passing a UUID that was constructed as a container UUID.

Side Effects:
No side effects — this is a pure function. It reads only from its parameter and returns a computed value. No memory is mutated, no I/O is performed.
