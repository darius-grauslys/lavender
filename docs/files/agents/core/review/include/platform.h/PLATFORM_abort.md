PLATFORM_abort — core/include/platform.h

Terminates program execution via a platform-specific fatal abort mechanism; the function is expected not to return under any backend.

Pre-conditions:
1. None. The function takes no parameters and performs no pointer dereferencing, so no input validation or null-check pre-conditions apply.
2. The caller must be in an execution context where process termination (or platform reset) is acceptable — this is the sole contract, mirrored by its sole core caller, `debug_abort` in `core/source/debug/debug.c`, which invokes it unconditionally as its final action.

Post-conditions:
1. The function does not return; program execution does not continue past this call on any backend.
2. On POSIX/SDL/no_gui/test/template backends (`sdl/source/debug/sdl_debug.c:16`, `no_gui/source/debug/no_gui_debug.c:16`, `tests/core/source/PLATFORM.c:180` and `tests/templates/source/PLATFORM.c:180`), `abort()` from `<stdlib.h>` is called, which raises SIGABRT and produces a core dump (or equivalent platform termination).
3. On the NDS backend (`nds/source/debug/nds_debug.c:15`), a memory-mapped I/O write at address 8192 (`*(uint32_t*)8192 = 100;`) is performed, triggering a hardware/platform reset via the NDS address map rather than a host signal.
4. No Lavender-owned resources (structs, pools, allocated memory) are cleaned up, mutated, or freed by this function; process-level reclamation is delegated to the OS or platform firmware.

Correctness Verdict: Correct

Semantic Alignment:
The function faithfully fulfills its semantic intent as the engine's fatal-abort hook. It is declared in `core/include/platform.h` alongside `PLATFORM_coredump` and `PLATFORM_pre_abort` (lines 69-71) and is contractually expected not to return, as documented in `agents/platform_api.md` (“PLATFORM_abort — called after the message; expected not to return”) and as enforced by `debug_abort` (`core/source/debug/debug.c:95`), which calls it as the final unconditional action. There is no implementation in `core/` itself — this is by design, since the header comment (lines 13-19) states that `PLATFORM_*` functions are implemented by backends such as OpenGL, SDL, nds, or no_gui. No semantic drift or omission is present; each backend's implementation matches the declared intent (host abort on POSIX/SDL/no_gui/test/template; hardware reset on NDS).

Implementation Correctness:
- Type compatibility: The signature is `void PLATFORM_abort(void)`, taking no parameters and returning nothing. The no_gui/sdl/test/template backends call `abort()`, whose prototype is `void abort(void)` — exact match with no implicit conversions or truncation. The NDS backend performs a `uint32_t` store to a fixed absolute address, which is well-typed within the bare-metal NDS address space.
- Undefined behavior: On the standard-library backends, `abort()` is a well-defined C library facility. On the NDS backend, `*(uint32_t*)8192 = 100;` writes to a hardware-mapped address in the NDS physical memory map (the address-8192 region used for platform reset/IRQ vectoring); this is an intentional, platform-specific idiom rather than generic out-of-bounds access. It is confined to a backend whose execution model permits absolute addressing at that location, so it is not portable-platform UB. There is no broken pointer arithmetic, no null dereference, no type punning, and no array out-of-bounds access in any backend.
- Validation: No validation is appropriate or possible — the function has no parameters and performs no computation on caller-supplied data. The decision to invoke a fatal abort is the caller's (`debug_abort`) responsibility; it has 100+ call sites each evaluating a condition and reaching this hook unconditionally.

Side Effects:
- Terminates the process without returning. On POSIX/SDL/no_gui/test/template backends this raises SIGABRT (and a core dump, where the OS supports it) via `abort()`.
- On the NDS backend, triggers a platform reset via a memory-mapped I/O write at address 8192.
- No Lavender-owned data structures, pools, or allocated memory are mutated or freed.
