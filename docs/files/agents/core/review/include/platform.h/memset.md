memset — core/include/platform.h

Fills the first n bytes of a memory buffer with a constant byte value.

Pre-conditions:
1. The first argument (void *s) must point to a writable memory region of at least n bytes when n > 0. If n == 0, the pointer is not dereferenced and need not be valid.
2. The second argument (int c) is any integer; it is converted to an unsigned char and written to each byte, so only the low 8 bits are meaningful.
3. The third argument (unsigned long n) is the number of bytes to fill; it must not exceed the number of writable bytes available from s.

Post-conditions:
1. The first n bytes of the buffer pointed to by s are set to the value of c (interpreted as an unsigned char).
2. The function returns s (a pointer to the base of the filled buffer).

Correctness Verdict: Correct

Semantic Alignment:
memset fulfills its semantic intent. The declaration matches the standard C library memset: it fills a contiguous byte range with a constant value and returns the base pointer. No Lavender-specific deviation from the documented behavior is present.

Implementation Correctness:
- Type compatibility — the byte-count parameter is declared `unsigned long`, not the standard `size_t`. On the target platform (Linux x86-64) `size_t` is `unsigned long`, so the two are identical and no truncation or implicit conversion hazard arises. This matches the engine's consistent convention for the memory primitives (malloc, memcpy all use `unsigned long`). Callers such as enum_map (enum_map.h:47,87) pass `sizeof(name)` (a `size_t`) as the count; that value is widened into `unsigned long` exactly, so no data is lost.
- No implementation exists in the Lavender codebase — memset is a C standard-library function declared here only to express the engine's signature convention. The header itself (platform.h:13-19) states these prototypes are not implemented in core and are resolved by the backend/toolchain.
- No undefined behavior in the declaration itself; UB can only arise at runtime from misuse (e.g., an invalid or too-small s), which is the caller's responsibility for a low-level primitive.
- No validation is needed — like all the standard-library entries grouped under SECTION_core, this is a trusted low-level utility; guarding the pointer would defeat its purpose.

Side Effects:
Writes `c` (as an unsigned char) into each of the first `n` bytes of the buffer pointed to by the first argument. No other memory is touched. The function returns the first argument; it has no global or observable side effects beyond the buffer write.
