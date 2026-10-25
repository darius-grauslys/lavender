get_rooms_in__structure — core/include/world/structures/structure.h

Copies the structure's internal room pointer array into the caller-provided output array, up to the quantity of rooms currently in the structure.

Pre-conditions:
1. p_structure must be a non-null pointer to a valid Structure object.
2. ptr_array_of__rooms must be a non-null pointer to a writable array of at least ROOMS_IN_STRUCTURE__MAX_QUANTITY_OF (8) Room* elements.
3. The caller is responsible for ensuring the output array has sufficient capacity.

Post-conditions:
1. The output ptr_array_of__rooms is populated with Room* pointers copied from p_structure->ptr_array_of__rooms, for indices 0 through (p_structure->quantity_of__rooms_in__structure - 1).
2. If quantity_of__rooms_in__structure < ROOMS_IN_STRUCTURE__MAX_QUANTITY_OF, the element at index quantity_of__rooms_in__structure is set to NULL.
3. Elements at indices greater than quantity_of__rooms_in__structure are left undefined (as documented in the header comment).

Correctness Verdict: Incorrect

Semantic Alignment:
The function's documented semantic intent is to copy the room pointers from the Structure's internal ptr_array_of__rooms into the caller-provided output array. However, the function has no implementation — it is declared in the header (core/include/world/structures/structure.h, line 24) but is not defined in any source file. This means the function cannot fulfill its documented semantic intent. The documentation states it "Returns quantity of rooms in the structure" but the function signature returns void, so it does not return a quantity either. The quantity must be obtained separately via get_quantity_of__rooms_in__structure().

Implementation Correctness:
No implementation exists, so type compatibility, undefined behavior, and validation concerns cannot be assessed against actual code. If implemented, the parameter Structure_Ptr_Array_Of__Rooms (which is Room*[8]) would decay to Room** in the function signature, allowing the function to write into the caller's array. A correct implementation would iterate from 0 to quantity_of__rooms_in__structure - 1, copying each Room* pointer, then set the next index to NULL if the count is less than ROOMS_IN_STRUCTURE__MAX_QUANTITY_OF.

Side Effects:
No side effects — the function only writes to the caller-provided ptr_array_of__rooms output parameter. (Note: implementation is absent, so this describes the intended behavior.)
