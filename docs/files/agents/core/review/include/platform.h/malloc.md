malloc — core/include/platform.h

Declares a platform-dependent memory allocation function that allocates a block of memory of the specified size in bytes and returns a pointer to the beginning of the block. The implementation is provided by a backend (e.g., OpenGL, nds) and is not found in core.

Pre-conditions:
1. size must be a valid unsigned long representing the number of bytes to allocate.
2. The caller must not assume the returned pointer is aligned beyond the platform's implementation-defined guarantee.
3. The caller is responsible for ensuring the allocated memory is eventually freed using the corresponding free function.

Post-conditions:
1. On success, returns a pointer to a newly allocated block of at least size bytes, suitably aligned for any built-in type.
2. On failure (insufficient memory), returns NULL.
3. The contents of the allocated block are indeterminate (uninitialized).

Correctness Verdict: Correct

Semantic Alignment:
The declaration matches the standard C library malloc signature and semantic intent: allocate size bytes of memory and return a void pointer. No struct initialization or field assignment is involved. The function is declared as a platform-dependent stub, consistent with the file's purpose of hosting backend-implemented functions.

Implementation Correctness:
Type compatibility — the parameter type (unsigned long) matches the standard malloc signature. The return type (void *) is compatible with all object pointer types.
No undefined behavior — this is a declaration, not an implementation; no pointer arithmetic, null dereference, type punning, or out-of-bounds access can occur at this level.
Validation — no validation is performed or needed in a declaration; the responsibility for handling NULL returns and valid size arguments lies with the caller.

Side Effects:
No side effects — this is a function declaration with no body. The actual side effects (memory allocation) occur in the platform-specific implementation, which is out of scope for this review.
