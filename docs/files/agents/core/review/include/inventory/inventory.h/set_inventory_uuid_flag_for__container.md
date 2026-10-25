set_inventory_uuid_flag_for__container — core/include/inventory/inventory.h

Clears the entity/container discriminator bit in an inventory UUID, marking it as a container.

Pre-conditions:
1. p_uuid must be a non-null pointer to a writable Identifier__u32 (uint32_t) object.
2. The pointed-to value may be any uint32_t; no range constraint is required.

Post-conditions:
1. The bit at position 25 (UUID_BIT__INVENTORY_IS__ENTITY_OR__CONTAINER, defined as BIT(25)) is cleared (set to 0) in the value pointed to by p_uuid.
2. All other bits in the pointed-to value remain unchanged.

Correctness Verdict: Correct

Semantic Alignment:
The function clears the UUID_BIT__INVENTORY_IS__ENTITY_OR__CONTAINER bit, which is the discriminator between entity and container UUIDs. The companion function set_inventory_uuid_flag_for__entity sets this same bit via |=. Clearing the bit here correctly marks the UUID as belonging to a container. The implementation matches the semantic intent exactly: `*p_uuid &= ~UUID_BIT__INVENTORY_IS__ENTITY_OR__CONTAINER` is the standard C idiom for clearing a single bit while preserving all other bits.

Implementation Correctness:
Type compatibility — p_uuid is Identifier__u32 * (i.e., uint32_t *), and UUID_BIT__INVENTORY_IS__ENTITY_OR__CONTAINER is BIT(25) which expands to ((1U) << (25)), a u32 value. The bitwise AND-assignment operates on uint32_t values throughout, with no implicit conversions or truncation.
No undefined behavior — the pointer is dereferenced exactly once; no pointer arithmetic, no type punning, no out-of-bounds access. The ~ operator on a u32 constant produces a well-defined u32 mask.
No validation is needed — this is a low-level bit manipulation. The caller is responsible for ensuring p_uuid is valid.

Side Effects:
Mutates the value pointed to by p_uuid: clears bit 25 (UUID_BIT__INVENTORY_IS__ENTITY_OR__CONTAINER), leaving all other bits intact.
