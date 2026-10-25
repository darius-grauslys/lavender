get_inventory_container__y_from__uuid — core/include/inventory/inventory.h

Extracts the Y-axis container coordinate from a 32-bit inventory UUID by masking with UUID_MASK__INVENTORY__CONTAINER__Y_AXIS.

Pre-conditions:
1. uuid is any Identifier__u32 (uint32_t); no range or validity constraint is required.
2. No pointer parameters; the function takes uuid by value, so no null-check applies.

Post-conditions:
1. Returns a u16 containing the Y-axis container coordinate stored in bits 10–0 of uuid. The returned value is at most MASK(11) = 2047, which fits within u16.

Correctness Verdict: Correct

Semantic Alignment:
The UUID layout is documented as:
```
/// [31..26] [25] [24..22] [21..11] [10..0]
///  item_stack  flag  z-axis  x-axis  y-axis
```
The Y-axis occupies the lowest 11 bits (bits 10–0). UUID_MASK__INVENTORY__CONTAINER__Y_AXIS is defined as MASK(11), which is exactly bits 0–10. Masking with this value directly extracts the Y-axis field into its correct position, so no right-shift is needed. This is consistent with the companion setter set_inventory_container__y_in__uuid, which writes y directly into bits 0–10 without a left-shift. The Z and X getters do require right-shifts because their fields are at higher bit positions (Z at bits 22–24, X at bits 11–21), but the Y getter correctly omits the shift because its field is already at the lowest bits.

Implementation Correctness:
Type compatibility — uuid is Identifier__u32 (uint32_t) and the mask UUID_MASK__INVENTORY__CONTAINER__Y_AXIS is MASK(11) = 0x7FF, so (uuid & mask) yields a value in [0, 2047], which fits losslessly in the u16 return type. No implicit conversion or truncation occurs.
Undefined behavior — no pointer dereference, no null access, no out-of-bounds indexing, no type punning. The function is pure arithmetic on a value parameter.
Validation — no validation is needed; the function performs a bit extraction and accepts any 32-bit input.

Side Effects:
No side effects — the function is pure: it reads only its value parameter and returns a computed u16.