get_chunk_y_i32_from__hitbox_aabb — core/include/collisions/core/aabb/hitbox_aabb.h

Returns the chunk-index (signed i32) for the Y component of a Hitbox_AABB's position.

Pre-conditions:
1. `p_hitbox` must be a non-null pointer to a writable `Hitbox_AABB` object in debug builds (the null guard is elided when `NDEBUG` is defined, so the caller must guarantee validity in release builds).
2. No other parameter constraints — the function takes a single pointer parameter.

Post-conditions:
1. Returns a `Signed_Index__i32` representing the chunk Y index derived from the Y coordinate of the hitbox's position vector (obtained by converting the position's i32F4 Y component via `normalize_xyz_i32F4_to__chunk_xyz_i32`).
2. The pointed-to `Hitbox_AABB` is not mutated — the function is read-only.

Correctness Verdict: Correct

Semantic Alignment:
The implementation fulfills the semantic intent. It extracts the position vector via `get_position_3i32F4_of__hitbox_aabb`, then converts that vector's Y component to a chunk index via `get_chunk_y_i32_from__vector_3i32F4`. The chain of delegation matches the intent of returning the Y chunk index for the hitbox.

Implementation Correctness:
- Type compatibility — `get_position_3i32F4_of__hitbox_aabb` returns `Vector__3i32F4`, which is passed by value to `get_chunk_y_i32_from__vector_3i32F4(Vector__3i32F4)`; the argument and parameter types match exactly. `get_chunk_y_i32_from__vector_3i32F4` returns `Signed_Index__i32`, which matches the declared return type of the function exactly. No implicit conversions or truncation.
- Undefined behavior — none. No pointer arithmetic, no null dereference (guarded by `#ifndef NDEBUG`), no type punning, no out-of-bounds access. The null guard returns 0 on invalid input rather than dereferencing.
- Validation — the null check is appropriate for a low-level inline accessor and mirrors the convention used by every sibling function in this header (`get_chunk_x_i32_from__hitbox_aabb`, `get_chunk_z_i32_from__hitbox_aabb`, `get_y_i32_from__hitbox_aabb`, etc.). In release builds the check is elided, so validation responsibility falls to the caller, which is the established pattern here.

Side Effects:
No side effects — the normal (non-null) path performs only a read of `position__3i32F4` followed by a pure computation. The only observable effect is the returned value. (The debug-only null-guard path invokes `debug_error` and returns 0 on a null pointer, but this is the defensive error path, not the function's primary behavior.)

Lavender-Specific Semantics:
This function name does not contain "init"/"initialize"/"reset"; it is a read-only accessor, not an initializer. The "Initialization ≠ RAII" caveat does not apply.
