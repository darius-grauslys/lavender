is_ui_window_record__using_parent_sprite_pool — core/include/ui/ui_window_record.h

Queries whether a UI_Window_Record delegates sprite allocation to its parent by checking if the signed sprite quantity is negative.

Pre-conditions:
1. p_ui_window_record must be a non-null pointer to a valid UI_Window_Record struct. No null check is performed; this is the caller's responsibility, consistent with all other inline query functions in this header.
2. The signed_quantity_of__sprites field (of type Signed_Quantity__i32 / int32_t) must be initialized to a meaningful value.

Post-conditions:
1. Returns true if signed_quantity_of__sprites is less than zero, indicating the UI window uses its parent's sprite pool.
2. Returns false if signed_quantity_of__sprites is greater than or equal to zero, indicating the window either allocates its own sprite pool (positive) or has no sprite pool (zero).

Correctness Verdict: Correct

Semantic Alignment:
The function correctly implements the semantic intent. The signed_quantity_of__sprites field uses a signed quantity convention where:
- Positive values indicate the window allocates its own sprite pool (confirmed by the sibling function is_ui_window_record__allocating_a_sprite_pool, which checks > 0).
- Negative values indicate the window uses its parent's sprite pool.
- Zero likely indicates no sprite pool is allocated or used.

The comparison < 0 correctly identifies the "using parent sprite pool" case. This is consistent with the three-way semantic split of the signed_quantity_of__sprites field across the two sibling query functions (> 0 for allocating, < 0 for using parent pool, and the validity check on function pointers for is_ui_window_record__valid).

Implementation Correctness:
Type compatibility — the parameter UI_Window_Record *p_ui_window_record is a pointer to the correct struct type. The field signed_quantity_of__sprites is of type Signed_Quantity__i32 (int32_t), and the comparison < 0 is perfectly valid for signed integers. No implicit conversions or truncation occur.
Undefined behavior — no pointer arithmetic, no out-of-bounds access, no type punning. The only potential issue is null pointer dereference if p_ui_window_record is null, but this is consistent with all other inline functions in this file (is_ui_window_record__valid, is_ui_window_record__allocating_a_sprite_pool) which also assume non-null pointers. This is an appropriate design for low-level inline query functions.
No validation is performed, which is appropriate for a simple inline query function. The caller is responsible for ensuring the pointer is valid.

Side Effects:
No side effects. This is a pure query function that only reads from the pointed-to struct.
