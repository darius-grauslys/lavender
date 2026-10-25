PLATFORM_opendir — core/include/platform.h

Opens the directory identified by the null-terminated path string and returns an opaque, heap-allocated handle on which a platform-specific OS directory handle is stored; returns NULL on failure. Platform-abstraction equivalent of POSIX opendir(3); opaque in the header, implemented per-platform (unix/nds wrap opendir DIR * into PLATFORM_Directory.p_UNIX_dir; win64 wraps FindFirstFile HANDLE into PLATFORM_Directory.handle; test stubs return 0 unconditionally for test isolation). This is an RAII-style resource-acquisition function (acquires an OS handle and allocates the wrapper struct), not a Lavender-style "init" that resets a struct for pool reuse.

Pre-conditions:
1. p_c_str is a non-null pointer to a null-terminated C string naming the directory to open. The function does not null-check the argument (matching POSIX opendir semantics); passing NULL is undefined behavior (POSIX opendir(NULL) and Windows FindFirstFile(NULL,...) are both invalid).
2. The target directory must exist and be accessible (search permission) for a non-null handle to be returned.
3. The caller owns the returned allocation and is responsible for releasing it via PLATFORM_closedir (which frees the struct and closes the OS handle).
4. The caller must NULL-check the returned pointer; every call site in world_directory.c already does (`if (!(p_dir = PLATFORM_opendir(...)))`).

Post-conditions:
1. On success: returns a non-null PLATFORM_Directory * pointing to a heap allocation whose platform-specific handle member (p_UNIX_dir on unix/nds, handle on win64) holds a valid open OS directory handle.
2. On OS-level open failure (path does not exist, is inaccessible, or — on win64 — is not a directory): returns NULL (0) and performs no allocation (no leak); the underlying OS opendir/FindFirstFile failure is detected before malloc.
3. The caller owns the returned allocation and is responsible for freeing it via PLATFORM_closedir; there is no double-open protection and the handle is opaque.

Correctness Verdict: Correct

Semantic Alignment:
The implementation faithfully realizes the semantic intent. Each platform delegates to the correct OS primitive — POSIX opendir on unix/nds (DIR *) and FindFirstFile on win64 (HANDLE) — checks the OS result, then wraps the OS handle in a freshly allocated, opaque PLATFORM_Directory struct. The three production implementations (sdl/unix, sdl/win64, nds) follow the identical acquire-check-allocate-populate-return pattern, and the test stubs (tests/core/source/PLATFORM.c:347, tests/templates/source/PLATFORM.c:347) return 0 unconditionally by design. The function is an explicit acquisition-and-allocation routine (RAII-style), which is the correct counterpart to PLATFORM_closedir's release-and-deallocate; this is not a Lavender "init" (pool reset) function. The semantic intent — open a directory, return an opaque handle, NULL on failure — is fully realized.

One semantic note (not a defect): on win64, FindFirstFile is not directory-specific and will also match regular files, so a file path may yield a non-null handle. This is the conventional win32 directory-enumeration idiom and is consistent with the abstraction's win32 design; it is not flagged by the peer PLATFORM_closedir review.

Implementation Correctness:
Type compatibility — the declaration `PLATFORM_Directory *PLATFORM_opendir(const char *p_c_str)` in platform.h:287 matches every definition exactly across all translation units. PLATFORM_Directory is an opaque typedef (defines_weak.h:422); each platform's .c file defines the concrete struct inline (`{ DIR *p_UNIX_dir; }` in sdl/unix unix_filesystem.c:21 and nds_filesystem.c:18, `{ HANDLE handle; }` in win64_file_system.c:18). The OS return types (DIR * from opendir, HANDLE from FindFirstFile) are assigned directly to the matching platform-specific fields — no implicit conversions, truncation, or mismatches. `return 0;` is a valid null-pointer constant in C and is consistent with the codebase's return-NULL style.

Undefined behavior — the success and OS-failure paths are clean: the OS result is checked before any deref/allocation (so a failed opendir/FindFirstFile returns 0 with no dereference and no leak). There is no pointer arithmetic, type punning, or out-of-bounds access. No issue found on these paths.

Caveat (defensive hardening gap, not a primary-logic defect): the return value of malloc is not checked before `p_dir->p_UNIX_dir = p_UNIX_dir;` (and `p_dir->handle = hFind;` on win64). If malloc returned NULL, the subsequent member write would dereference a null pointer. This deviates from the codebase's own allocation convention — e.g. hitbox_aabb_manager.c:39-43 checks malloc, logs via debug_error, and returns 0 on failure. In practice the engine assumes allocations succeed (memory exhaustion is not otherwise a handled condition here, and on malloc failure the process is typically being OOM-killed anyway), so this is an extremely rare edge case rather than a logic bug; nevertheless, adding the `if (!p_dir) { return 0; }` guard would align PLATFORM_opendir with the established codebase pattern and remove the latent undefined-behavior path. On the success/OS-failure paths the function is fully correct.

Validation — checking the OS open result (and returning NULL on failure) is appropriate validation for this function's role; the OS call itself is the source of truth for path validity. Null-checking p_c_str is not performed, consistent with POSIX opendir semantics — it is the caller's responsibility, and all call sites pass concrete path strings. No further validation is in scope.

Side Effects:
1. Acquires an OS-level directory handle (POSIX opendir / Windows FindFirstFile) tied to the path.
2. Allocates a PLATFORM_Directory struct on the heap via malloc and stores the OS handle in its platform-specific field.
3. On the OS-failure path, performs no allocation and leaves no OS handle open (the failed opendir/FindFirstFile result is discarded before any allocation).
4. Does not modify any global state, the input string, or any caller-visible memory beyond the single returned pointer.
