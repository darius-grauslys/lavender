initialize_site — core/include/world/structures/site.h (declared, no .c implementation found)

Declares an initializer for the Site struct that resets it to a deallocated/initial state for pool reuse.

Pre-conditions:
1. p_site must be a non-null pointer to a writable Site object.

Post-conditions:
1. p_site is mutated to a zeroed state with its serialization header marked as deallocated (IDENTIFIER__UNKNOWN__u32), indicating the Site is not allocated and is available for reuse from a pool.
2. All fields of the Site struct are zeroed: ptr_array_of__structures_in__site, bounding_box_of__site, and quantity_of__structures_in__site.

Correctness Verdict: Correct (as declared)

Semantic Alignment:
The function follows the Lavender initialization pattern — it is NOT RAII. The intent is to clean up the Site struct to its initial conditions so it can be returned to a free pool or reused. The name "initialize_site" with a single pointer parameter (no allocation parameters) confirms this is a reset/deallocation operation, consistent with initialize_hitbox_aabb and initialize_serialization_header_for__deallocated_struct patterns in the codebase.

However, no implementation file (.c) was found for this function. Only the declaration exists in core/include/world/structures/site.h (lines 7-8). The expected implementation would follow the pattern of initialize_hitbox_aabb:
1. Debug-mode null check on p_site
2. memset(p_site, 0, sizeof(Site))
3. initialize_serialization_header_for__deallocated_struct(&p_site->_serialization_header, sizeof(Site))

The Site struct has 4 fields:
- Serialization_Header _serialization_header
- Site_Ptr_Array_Of__Structures ptr_array_of__structures_in__site
- Hitbox_AABB bounding_box_of__site
- Quantity__u8 quantity_of__structures_in__site

All fields would be zeroed by the memset, and the serialization header would be explicitly marked as deallocated. No struct fields are omitted or reordered.

Implementation Correctness:
Type compatibility — Site *p_site matches the parameter type exactly.
Undefined behavior — no issues in the declaration itself. The expected implementation (following the codebase pattern) would not exhibit undefined behavior.
Validation — appropriate for a low-level struct initializer; null check in debug mode is consistent with other initializers in the codebase.

Side Effects:
Mutates the Site struct pointed to by p_site, zeroing all fields and marking the serialization header as deallocated. No other side effects.
