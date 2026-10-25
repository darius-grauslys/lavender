add_vectors__3i16F8 — core/include/vectors.h, lines 346-354

## Semantic

Performs component-wise addition of two 3-component 16-bit fixed-point (F8) vectors, returning a new vector whose x, y, and z components are the sums of the corresponding input components.

## Pre-conditions

1. `vector_one` is a valid `Vector__3i16F8` struct (passed by value, so always valid).
2. `vector_two` is a valid `Vector__3i16F8` struct (passed by value, so always valid).
3. No pointer parameters are involved; both arguments are passed by value, so null dereference is impossible.
4. Each `i16F8` field is an `int16_t`; the caller is responsible for ensuring that component sums do not overflow the `int16_t` range. Signed integer overflow is undefined behavior in C, but this is a low-level math helper and overflow handling is the caller's responsibility, consistent with sibling functions such as `add_vectors__3i32F4` and `add_vectors__3i32`.

## Post-conditions

1. Returns a new `Vector__3i16F8` where:
   - `.x__i16F8 == vector_one.x__i16F8 + vector_two.x__i16F8`
   - `.y__i16F8 == vector_one.y__i16F8 + vector_two.y__i16F8`
   - `.z__i16F8 == vector_one.z__i16F8 + vector_two.z__i16F8`
2. Neither `vector_one` nor `vector_two` is mutated (both are passed by value).
3. No external state is modified.

## Correctness Verdict

Correct

## Semantic Alignment

The implementation correctly performs component-wise vector addition. Each of the three components (x, y, z) is summed independently, matching the mathematical definition of vector addition. The function constructs and returns a new `Vector__3i16F8` struct with all three fields populated — no field is omitted and no reordering occurs.

## Implementation Correctness

- **Type compatibility**: `i16F8` is a typedef for `int16_t` (defined in `defines_weak.h`). Adding two `int16_t` values triggers integer promotion to `int`, and the result is implicitly narrowed back to `i16F8` (`int16_t`) during struct initialization. This implicit narrowing conversion is consistent with the pattern used by all sibling `add_vectors__*` and `subtract_vectors__*` functions in this file. No truncation occurs for in-range results.
- **Undefined behavior**: Signed integer overflow is technically undefined behavior in C. However, this is a deliberate design choice consistent across the codebase (e.g., `add_vectors__3i32F4`, `add_vectors__3i32`, `subtract_vectors__3i32F4` all use the same pattern). There is no overflow checking, but the engine relies on game logic ensuring values remain within range. No pointer arithmetic, null dereference, type punning, or out-of-bounds access is present.
- **Validation**: No validation is needed or expected. This is a low-level static inline math helper. The caller is responsible for ensuring inputs are within valid ranges.

## Side Effects

No side effects. The function is pure: it takes both operands by value, computes a new vector, and returns it without modifying any input, global state, or memory.
