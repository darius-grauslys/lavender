buffer_input_for__writing — core/source/input/input.c

Buffers a character symbol into the input's circular writing buffer for later consumption via poll_input_for__writing.

Pre-conditions:
1. p_input must be a non-null pointer to a valid, writable Input object.
2. symbol is any char value; no range constraint. A null byte (0) is semantically significant — poll_input_for__writing uses a zero value as a sentinel meaning "no character to read," so buffering 0 will effectively be indistinguishable from an empty slot.

Post-conditions:
1. writing_buffer at the previous value of index_of__writing_buffer__write is set to symbol.
2. index_of__writing_buffer__write is advanced by 1, wrapping modulo MAX_QUANTITY_OF__SYMBOLS_IN__INPUT_WRITING_BUFFER (8) via a bitmask, so it stays within [0, 7].

Correctness Verdict: Correct

Semantic Alignment:
The implementation correctly writes symbol to the circular buffer at the current write index and advances the write index with wraparound. This matches the semantic intent of buffering input for writing. The bitmask MASK(3) = 7 corresponds exactly to the buffer size BIT(3) = 8, producing valid indices [0, 7]. The corresponding read function poll_input_for__writing uses the same masking pattern, confirming the design is consistent.

Implementation Correctness:
- Type compatibility: The parameter char symbol is assigned to unsigned char writing_buffer[...]. This is a well-defined implicit conversion (char to unsigned char; negative char values map to their unsigned equivalent, which is acceptable for character data). index_of__writing_buffer__write is Index__u8 (uint8_t); the expression (index + 1) & MASK(3) yields a u32 result of at most 7, which is safely narrowed back to uint8_t. No truncation issues.
- Undefined behavior: No broken pointer arithmetic, no null dereference, no type punning, no out-of-bounds access. The buffer has exactly MAX_QUANTITY_OF__SYMBOLS_IN__INPUT_WRITING_BUFFER (8) elements (indices 0–7), and the bitmask ensures the write index never exceeds 7.
- Validation: No validation is needed. This is a low-level buffer write function; the caller is responsible for ensuring p_input is valid. The function performs no range-checking on symbol or index overflow detection (e.g., overwriting unconsumed data), which is appropriate for a fixed-size circular buffer of this role.

Side Effects:
- Mutates p_input->writing_buffer at the index held by index_of__writing_buffer__write (before advancement), setting it to symbol.
- Mutates p_input->index_of__writing_buffer__write, advancing it by 1 with power-of-2 wraparound.
