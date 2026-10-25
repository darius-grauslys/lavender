PLATFORM_pre_abort — core/include/platform.h

Performs platform-specific pre-abort setup before `debug_abort` prints its abort message and calls `PLATFORM_abort`; the function is declared in the core header and implemented by each backend, with no implementation residing in `core/` itself — this is by design, as the header comment (lines 13-19) states that all `PLATFORM_*` functions are implemented by backends such as SDL, nds, or no_gui.

Pre-conditions:
1. None. The function takes no parameters (`void PLATFORM_pre_abort(void)`) and performs no pointer dereferencing, so no input validation, null-check, or range-check pre-conditions apply.
2. The caller must be in a debug/abort execution context — specifically `debug_abort` in `core/source/debug/debug.c:82`, which invokes it unconditionally as its first action, before the abort message is printed and before `PLATFORM_abort` is called. The decision to enter the abort path is the caller's responsibility.

Post-conditions:
1. On the standard-library backends (SDL `sdl/source/debug/sdl_debug.c:13`, no_gui `no_gui/source/debug/no_gui_debug.c:13`, test `tests/core/source/PLATFORM.c:177`, template `tests/templates/source/PLATFORM.c:177`), the function is a no-op (empty body) — no state is mutated and no side effects occur; execution proceeds normally to the caller's next statement (the abort message print and subsequent `PLATFORM_abort` call).
2. On the NDS backend (`nds/source/debug/nds_debug.c:11`), the function calls `NDS_initialize_debug__sub()`, which initializes the sub-screen debug console (guarded by `#ifndef NDEBUG`) so that the forthcoming abort message is visible on the NDS secondary display.
3. The function always returns control to the caller — unlike `PLATFORM_abort`, it is not expected to terminate the process; it is explicitly a pre-step, not the terminal action.
4. No Lavender-owned data structures, pools, or allocated memory are cleaned up, mutated, or freed by this function.

Correctness Verdict: Correct

Semantic Alignment:
The function faithfully fulfills its semantic intent as the engine's pre-abort hook. It is declared in `core/include/platform.h` alongside `PLATFORM_coredump` and `PLATFORM_abort` (lines 69-71) and is documented in `agents/platform_api.md` ("Called before abort in debug paths") and in the debug module docs (`agents/core/modules/debug.md`: "PLATFORM_pre_abort (called before the abort: message)"). The documented role — preparing the platform for the abort message and any subsequent hard-abort — is carried out correctly: on backends where it is a no-op, no preparation is needed and the function correctly degrades; on NDS, it initializes the debug sub-screen console specifically so the abort message will be visible before `PLATFORM_abort` triggers a hardware reset. Each backend's implementation matches the declared intent. No semantic drift or omission is present.

Implementation Correctness:
- Type compatibility: The signature is `void PLATFORM_pre_abort(void)`, taking no parameters and returning nothing. All backend implementations match this signature exactly — no implicit conversions, no truncation, no type mismatch.
- Undefined behavior: There is no pointer arithmetic, no null dereference, no type punning, and no out-of-bounds access on any backend. The SDL/no_gui/test/template backends have empty bodies (trivially safe). The NDS backend calls `NDS_initialize_debug__sub()` (defined in the same translation unit at `nds/source/debug/nds_debug.c:35`), which performs `consoleGetDefault()` (a NitroFS/libnds call returning a pointer to a default console) and `consoleInit` on it — both are well-typed libnds APIs. The `#ifndef NDEBUG` guard means the console initialization is compiled out in release builds, which is the intended behavior.
- Validation: No validation is appropriate or possible — the function has no parameters and performs no computation on caller-supplied data. The decision to invoke pre-abort setup is the caller's (`debug_abort`) responsibility.

Side Effects:
- On the NDS backend: initializes the sub-screen debug console via `NDS_initialize_debug__sub()`, configuring a text background for the secondary display so the abort message is visible before the hardware reset triggered by `PLATFORM_abort`. This is compiled out when `NDEBUG` is defined.
- On all other backends (SDL, no_gui, test, template): no side effects (empty body).
- No Lavender-owned data structures, pools, or allocated memory are mutated or freed.
- The function always returns (never terminates the process); termination is the responsibility of the subsequent `PLATFORM_abort` call.
