# Function Review: `poll_world_for__scrolling`

## File of Origin
`core/source/world/world.c` (lines 175–181)

## Semantic
Polls the world for scrolling behavior — presumably checking player position, input state, or viewport boundaries to determine whether the world view should scroll and, if so, updating the graphics window's viewport accordingly. The function is intended to return a boolean indicating whether scrolling occurred. The current implementation is a **stub** that aborts execution.

## Pre-conditions
1. `p_game` — must be non-null. No validation is performed.
2. `p_world` — must be non-null. No validation is performed.
3. `p_gfx_window` — must be non-null. No validation is performed.

## Post-conditions
None meaningful. The function calls `debug_abort` (which invokes `PLATFORM_abort`) and never reaches the `return false` statement. No state is modified.

## Correctness Verdict
**Incorrect**

## Semantic Alignment
The implementation does **not** fulfill the semantic intent. The function body consists solely of a `debug_abort("poll_world_for__scrolling, impl")` call, indicating the scrolling logic has not been implemented. The `return false` on line 180 is unreachable dead code because `debug_abort` calls `PLATFORM_abort()`, which terminates the program and never returns.

## Implementation Correctness
- **Unreachable code:** The `return false;` statement after `debug_abort` is dead code. `debug_abort` (defined in `core/source/debug/debug.c`) calls `PLATFORM_abort()`, which does not return. The `return false` can never execute.
- **No parameter validation:** The function does not validate that `p_game`, `p_world`, or `p_gfx_window` are non-null. While this may be acceptable if callers are expected to guarantee non-null arguments, the function's role as a polling function suggests it should at minimum guard against null pointers before dereferencing them (once the stub is replaced with real logic).
- **Type compatibility:** The return type is `bool`, and `false` is a valid `bool` value, so there is no type mismatch. However, since the return is unreachable, this is moot.
- **Undefined behavior:** No undefined behavior is present in the current stub. The `debug_abort` call with a string literal is well-formed.

## Side Effects
- **Program termination:** The function calls `debug_abort`, which prints an abort message and invokes `PLATFORM_abort()`, terminating the program. This is the only observable side effect.
- No mutations to `p_game`, `p_world`, or `p_gfx_window` occur.
