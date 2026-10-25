get_inventory_container__z_from__uuid — core/include/inventory/inventory.h

Extracts the 3-bit Z-axis component from a 32-bit inventory container UUID.

Pre-conditions:
1. uuid is any valid Identifier__u32 (uint32_t) value. No null check or validation is needed since it is passed by value.

Post-conditions:
1. Returns a u16 containing the 3-bit Z-axis value (range 0–7) extracted from bits 22–24 of the UUID.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly extracts the Z-axis component from the UUID. The UUID layout (documented in defines.h) is:
  [31..26] [25] [24..22] [21..11] [10..0]
    item_stack  entity/container flag  z-axis  x-axis  y-axis

`UUID_MASK__INVENTORY__CONTAINER__Z_AXIS` is defined as `MASK(3) << 22`, which selects bits 22–24. `UUID_BIT_SHIFT__INVENTORY__CONTAINER__Z_AXIS` is 22. The function first masks the UUID with this mask to isolate the Z-axis bits, then right-shifts by 22 to bring the value to the least-significant position. This correctly produces the 3-bit Z-axis value (0–7).

The computation matches the semantic intent: extracting the Z-axis component from the UUID.

Implementation Correctness:
Type compatibility — the parameter `uuid` is `Identifier__u32` (uint32_t), and the mask and shift operations are performed on u32 values. The result is implicitly converted to the return type `u16`, which is safe since the extracted value is at most 7 (3 bits), well within u16 range.
No undefined behavior — no pointer arithmetic, no null dereference, no out-of-bounds access, no type punning. The bitwise operations are well-defined on u32 values.
No validation is needed — this is a pure extraction function operating on a value parameter.

Side Effects:
No side effects — the function is pure. It reads only its input parameter and returns a computed value.
