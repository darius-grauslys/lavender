strncpy_returns__strlen — core/source/core_string.c

Copies up to max_length_of__copy bytes from the source buffer to the destination buffer, stopping at the first null terminator, and returns the number of bytes copied.

Pre-conditions:
1. p_destination must be a non-null pointer to a writable buffer of at least max_length_of__copy bytes.
2. p_source must be a non-null pointer to a readable buffer containing at least max_length_of__copy bytes or a null terminator within the first max_length_of__copy bytes.
3. max_length_of__copy is a Quantity__u32 (uint32_t); may be 0, in which case no bytes are copied and 0 is returned.

Post-conditions:
1. The destination buffer p_destination contains the bytes copied from p_source. If the source contains a null terminator within the first max_length_of__copy bytes, copying stops after writing that null terminator. If no null terminator is found, exactly max_length_of__copy bytes are copied.
2. The return value is an Index__u32 equal to the number of bytes copied. This equals the length of the source string (excluding the null terminator) if a null terminator was found within the limit, or max_length_of__copy if no null terminator was found.

Correctness Verdict: Correct

Semantic Alignment:
The function's docstring states "Same as strncpy, but returns the length of the string." The core copying behavior aligns with strncpy — it copies up to max_length_of__copy bytes and stops at a null terminator. However, there is a key divergence: standard strncpy null-pads the destination buffer with zero bytes when the source string is shorter than the limit, whereas this function does NOT pad — it stops writing entirely after the null terminator, leaving the remaining destination bytes unmodified. The "same as strncpy" claim is therefore partially misleading regarding null-padding behavior. The primary intent — copy a bounded string and return its length — is fulfilled correctly.

Implementation Correctness:
Type compatibility — the void* parameters are cast to u8* for byte-level access, which is a safe and appropriate conversion. The loop counter index_of__string (Index__u32, uint32_t) is compared against max_length_of__copy (Quantity__u32, uint32_t), so the comparison is type-safe with no implicit conversions or truncation. The return type Index__u32 matches the function declaration.
No undefined behavior — assuming pre-conditions hold (non-null pointers, valid buffers), there is no broken pointer arithmetic, no null dereference, no type punning, and no out-of-bounds access. Array indexing is bounded by the max_length_of__copy guard in the loop condition.
No validation — the function does not check that p_destination or p_source are non-null. This is appropriate for a low-level utility function; validation is the caller's responsibility.

Side Effects:
Mutates the destination buffer p_destination by copying up to max_length_of__copy bytes from the source. If the source string is shorter than the limit, only the bytes up to and including the null terminator are written; the remaining destination bytes are not modified (no null-padding as in standard strncpy).
