free — core/include/platform.h

Frees the memory block pointed to by the given pointer, returning it to the platform's memory allocator. This is a standard C library function declared here as a platform-dependent signature.

Pre-conditions:
1. ptr may be NULL — passing NULL is a safe no-op.
2. ptr must be either NULL or a pointer previously returned by malloc (or a compatible allocator) that has not already been freed.
3. The memory block pointed to by ptr must not have been corrupted or modified after allocation.

Post-conditions:
1. If ptr is non-NULL, the memory block it pointed to is deallocated and may be reused by the allocator.
2. If ptr is NULL, no action is taken.
3. After the call, ptr is a dangling pointer and must not be dereferenced.

Correctness Verdict: Correct

Semantic Alignment:
The function is a declaration of the standard C library `free` function. It correctly matches the semantic intent of deallocating a memory block. There is no implementation to review — the actual implementation is provided by the platform/backend (e.g., the C standard library or a platform-specific allocator). The declaration signature `void free(void *)` is the correct and standard signature for this function.

Implementation Correctness:
No implementation exists in the core module — this is a platform-dependent declaration. The signature uses `void *` for the parameter, which is type-compatible with any pointer type returned by `malloc` or other allocation functions. No implicit conversions or truncation issues arise from the declaration itself. The caller is responsible for ensuring the pointer was obtained from a compatible allocator and has not been freed already.

Side Effects:
Deallocates the memory block pointed to by the argument, returning it to the platform's memory allocator for reuse. This modifies the allocator's internal state. Passing NULL results in no side effects.
