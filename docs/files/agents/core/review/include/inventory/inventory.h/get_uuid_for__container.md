get_uuid_for__container — core/include/inventory/inventory.h

Constructs a 32-bit container UUID from a 3D tile vector by encoding the x, y, and z coordinates into their respective bit fields and clearing the entity/container flag to indicate a container.

Pre-conditions:
1. tile_vector__3i32 is passed by value, so no null check is required.
2. The coordinate fields (x__i32, y__i32, z__i32) are int32_t values that will undergo implicit narrowing conversion to u16 when passed to the setter functions. The caller is responsible for ensuring coordinate values are non-negative and within the valid range for the UUID bit fields (x and y: 11 bits, z: 3 bits).
3. The uuid local variable is initialized to 0, ensuring all bits are cleared before encoding.

Post-conditions:
1. Returns an Identifier__u32 with the following bit layout:
   - Bits [10..0] (y-axis): set to tile_vector__3i32.y__i32, masked to 11 bits.
   - Bits [21..11] (x-axis): set to tile_vector__3i32.x__i32, shifted left by 11 and masked to 11 bits.
   - Bits [24..22] (z-axis): set to tile_vector__3i32.z__i32, shifted left by 22 and masked to 3 bits.
   - Bit [25] (entity/container flag): cleared to 0, indicating a container.
   - Bits [31..26] (item stack index): remain 0, as no item stack information is encoded.
2. The returned UUID is a pure value with no side effects on the input or any external state.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly constructs a container UUID by delegating to four setter functions:
- set_inventory_container__y_in__uuid encodes y into bits [10..0] (no shift needed, as y occupies the least significant 11 bits).
- set_inventory_container__x_in__uuid encodes x into bits [21..11] (shifted left by 11).
- set_inventory_container__z_in__uuid encodes z into bits [24..22] (shifted left by 22).
- set_inventory_uuid_flag_for__container clears bit 25 to mark the UUID as a container.

The bit layout matches the documented UUID format:
  [31..26] [25] [24..22] [21..11] [10..0]
                 z-axis   x-axis   y-axis

The entity/container flag is correctly cleared (0 = container) via set_inventory_uuid_flag_for__container, which performs `*p_uuid &= ~UUID_BIT__INVENTORY_IS__ENTITY_OR__CONTAINER`. The round-trip is consistent with the getter functions get_inventory_container__x_from__uuid, get_inventory_container__y_from__uuid, and get_inventory_container__z_from__uuid, which extract the same bit fields with matching masks and shifts.

Implementation Correctness:
Type compatibility — The Tile_Vector__3i32 struct has int32_t fields (x__i32, y__i32, z__i32), which are implicitly converted to u16 (uint16_t) when passed to the setter functions. This is a narrowing conversion, but the setter functions mask the values to their respective bit widths (11 bits for x/y, 3 bits for z), so no out-of-bounds writes to the UUID occur. The conversion is safe for non-negative values within range.
Undefined behavior — No undefined behavior. No pointer arithmetic, no null dereference (uuid is a local variable), no type punning, no out-of-bounds access. The masking in each setter ensures only valid bits are modified.
Validation — No validation is performed, which is appropriate for this low-level inline function. The setter functions' masking handles truncation of out-of-range values. The caller is responsible for providing valid tile coordinates.

Side Effects:
No side effects. The function operates entirely on a local Identifier__u32 variable and returns it by value. No memory is written to, no global state is modified, and no I/O occurs.
