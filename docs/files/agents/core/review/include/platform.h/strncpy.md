strncpy — core/include/platform.h, line 177

Copies up to n bytes from src to dest; if src is shorter than n, pads the remainder of dest with null bytes. Does NOT null-terminate dest if strlen(src) >= n (the standard strncpy gotcha).

Pre-conditions:
1. dest must be a non-null pointer to a writable buffer of at least n bytes.
2. src must be a non-null pointer to a null-terminated character array; passing NULL is undefined behavior per ISO C.
3. The memory regions pointed to by src and dest must not overlap.
4. n is the maximum number of bytes to copy (not the required destination buffer size in bytes if src is longer).

Post-conditions:
1. The dest buffer contains the first n bytes taken from src. If strlen(src) < n, the remaining bytes (strlen(src)+1 through n-1) are set to '\0'.
2. If strlen(src) >= n, dest is NOT null-terminated.
3. Returns dest (same pointer passed in).

Correctness Verdict: Correct

Semantic Alignment:
The declaration `char *strncpy(char *dest, const char *src, size_t n)` precisely matches the ISO C standard signature (C89 through C23). There is no Lavender-specific implementation — the header re-declares the system libc function as part of the platform abstraction layer (see surrounding declarations: free, malloc, memcpy, memset, abs, srand, rand, strncmp, strnlen). No divergence from standard semantics exists in any Lavender source.

Implementation Correctness:
- Type compatibility: All parameter and return types match the C standard exactly — `char *` (return and dest), `const char *` (src), `size_t` (n). No implicit conversions or truncation.
- Undefined behavior: The declaration introduces no undefined behavior itself. However, call sites that rely on null-termination after strncpy must first zero the destination buffer (see world.c:336 which correctly does memset before strncpy) or verify strlen(src) < n, otherwise they risk operating on a non-terminated buffer.
- Validation: No validation is needed — this is a standard library function re-declared for platform abstraction. Caller responsibility governs pointer validity and buffer sizing.

Side Effects:
Writes up to n bytes into the dest buffer. Does not modify src. No global state changes, no allocation or deallocation. (The declaration itself has no side effects; the function call writes to dest.)
