set_hitbox_aabb__position_with__3i32 — core/source/collisions/core/aabb/hitbox_aabb.c

Sets the Hitbox_AABB position from a plain integer Vector__3i32, converting each component to a fixed-point i32F4 representation (4 fractional bits) and marking the hitbox as dirty.

Pre-conditions:
1. p_hitbox_aabb must be a non-null pointer to a writable Hitbox_AABB object (validated only in debug builds; see Implementation Correctness).
2. position__3i32 is a value parameter of type Vector__3i32; no range constraint is enforced. Each component is a Signed_Index__i32 (int32_t) representing a plain integer position.

Post-conditions:
1. p_hitbox_aabb->position__3i32F4.x__i32F4 is set to position__3i32.x__i32 converted to fixed-point F4 format.
2. p_hitbox_aabb->position__3i32F4.y__i32F4 is set to position__3i32.y__i32 converted to fixed-point F4 format.
3. p_hitbox_aabb->position__3i32F4.z__i32F4 is set to position__3i32.z__i32 converted to fixed-point F4 format.
4. The hitbox dirty flag is set via set_hitbox_aabb_as__dirty.

Correctness Verdict: Incorrect

Semantic Alignment:
The intent is to convert a plain integer position (Vector__3i32, no fractional bits) to the engine's fixed-point representation (i32F4, 4 fractional bits). The conversion method — left-shifting each component by FRACTIONAL_PERCISION_4__BIT_SIZE (4) — is the correct conceptual operation. The function also correctly marks the hitbox as dirty, consistent with the sibling function set_hitbox_aabb__position_with__3i32F4 (lines 77-89). The computation matches the semantic intent, but the implementation contains undefined behavior that violates the intent for negative inputs (see Implementation Correctness).

Implementation Correctness:
Type compatibility — position__3i32.x__i32 is Signed_Index__i32 (int32_t, defines_weak.h:111-119), x__global is i32F4 (int32_t, defines.h:54), and position__3i32F4.x__i32F4 is i32F4 (int32_t, defines_weak.h:76-77). All types are int32_t, so the assignment is well-typed with no implicit conversions or truncation.

Undefined behavior — The function uses a raw left-shift to convert each component:
    x__global << FRACTIONAL_PERCISION_4__BIT_SIZE;
Per the C standard (C11 6.5.7.4), left-shifting a value of signed type with a negative value, or a value whose result cannot be represented in the result type, is undefined behavior. position__3i32 components are Signed_Index__i32, which are frequently negative (e.g., positions in the negative world quadrant). A raw shift on a negative int32_t invokes UB.

The engine explicitly acknowledges this hazard in numerics.h:21-22:
    /// L shift on negative numbers is undefined behavior.
    /// This is an explicit arithmetric definition for L shift on negatives.
and provides two safe alternatives:
    - ARITHMETRIC_L_SHIFT(x, n) macro (numerics.h:23-24), which casts through u32 before shifting.
    - i32_to__i32F4(Signed_Index__i32) helper (numerics.h:69-74), which uses ARITHMETRIC_L_SHIFT internally.
The standard vector conversion function vector_3i32_to__vector_3i32F4 (vectors.h:266-274) correctly uses i32_to__i32F4 for each component.

This function reimplements the same conversion but bypasses the safe macro/helper, introducing UB for negative inputs. This is a real correctness defect, not merely theoretical — positions in this engine are routinely negative.

Validation — The debug-only null check for p_hitbox_aabb (#ifndef NDEBUG) is consistent with the codebase pattern (e.g., set_hitbox_aabb__position_with__3i32F4 at lines 80-85). In release builds (NDEBUG defined), a null p_hitbox_aabb would cause a null pointer dereference. This is the established convention and not flagged as a separate bug.

Side Effects:
Mutates p_hitbox_aabb->position__3i32F4 (sets x, y, z components). Sets the hitbox dirty flag via set_hitbox_aabb_as__dirty(p_hitbox_aabb), which writes to p_hitbox_aabb->hitbox_aabb_flags__u8. Does not read or modify position__3i32 (passed by value).

Issues Found:
1. (Critical) Undefined behavior on negative position values: The raw left-shift x__global << 4 is UB when x__global is negative (position__3i32.x__i32 is Signed_Index__i32 and commonly negative). The engine provides ARITHMETRIC_L_SHIFT (numerics.h:23) and i32_to__i32F4 (numerics.h:69) specifically to avoid this. Recommend replacing each shift with i32_to__i32F4(position__3i32.x__i32), or equivalently using ARITHMETRIC_L_SHIFT(x__global, FRACTIONAL_PERCISION_4__BIT_SIZE). Better yet, replace the entire function body with a single call to vector_3i32_to__vector_3i32F4(position__3i32) (vectors.h:266-274) to match the engine's idiomatic conversion and ensure consistency.
