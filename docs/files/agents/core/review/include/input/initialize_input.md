initialize_input — core/source/input/input.c

Zeros out the entire Input struct, resetting it to its initial/default state. This is a Lavender-style pool cleanup (not RAII).

Pre-conditions:
1. p_input must be a non-null pointer to a writable Input struct of sufficient size.

Post-conditions:
1. All bytes of the Input struct are set to 0 via memset(p_input, 0, sizeof(Input)).
2. All input flags (input_flags__pressed, input_flags__held, input_flags__released, input_flags__pressed_old) become 0 (INPUT_NONE).
3. Both cursor vectors (cursor__3i32, cursor__old__3i32) are fully zeroed.
4. The writing_buffer array is fully zeroed — all slots are empty (0).
5. last_symbol is 0.
6. Both buffer indices (index_of__writing_buffer__read, index_of__writing_buffer__write) are 0.
7. input_mode__u8 is 0 (INPUT_MODE__NORMAL), since INPUT_MODE__NORMAL is defined as 0.

Correctness Verdict: Correct

Semantic Alignment:
The function performs a full zero-initialization of the Input struct. According to the Lavender initialization semantics, this is a pool cleanup operation — the struct is being cleared/reset to default conditions so it can be returned to a free pool or reused, not a resource acquisition (RAII). The call memset(p_input, 0, sizeof(Input)) correctly zeroes every field without omission or reordering, matching the semantic intent. The zero value is consistent with the default sentinel values used throughout the Input struct (e.g., INPUT_NONE is 0, INPUT_MODE__NORMAL is 0, empty writing_buffer slots are 0).

Implementation Correctness:
Type compatibility — p_input is Input *; the first argument to memset is void *, so Input * is implicitly convertible. The fill byte is 0 (int), matching memset's int parameter. sizeof(Input) is size_t, matching memset's size parameter. No implicit conversions or truncation. Undefined behavior — no pointer arithmetic, no null dereference (assuming p_input is valid), no type punning. memset covers exactly sizeof(Input) bytes with no out-of-bounds access. Validation — no validation is performed; this is consistent with the Lavender pattern for low-level struct initializers where the caller is responsible for providing a valid pointer.

Side Effects:
Mutates the entire Input struct by zero-filling all of its memory. All flags, cursor positions, the writing buffer, buffer indices, and the input mode are reset to their default (zero) values.
