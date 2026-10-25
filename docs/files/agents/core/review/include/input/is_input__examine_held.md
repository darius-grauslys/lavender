# Function Review: is_input__examine_held

## 1. Header
- **Function name:** `is_input__examine_held`
- **File of origin:** `core/include/input/input.h`

## 2. Semantic
Returns whether the "examine" input is currently held, by testing the `INPUT_EXAMINE` bit in the held input flags.

## 3. Pre-conditions
1. `p_input` must be a non-null pointer to an initialized `Input` struct. Dereferencing a null pointer is undefined behavior.

## 4. Post-conditions
1. Returns `true` if the `INPUT_EXAMINE` bit is set in `p_input->input_flags__held`.
2. Returns `false` otherwise.
3. The `Input` struct pointed to by `p_input` is not modified.

## 5. Correctness Verdict
Correct

## 6. Semantic Alignment
The implementation fulfills the semantic intent of the function name. The function reads `p_input->input_flags__held` and tests the `INPUT_EXAMINE` bit, which correctly reflects whether the examine action is currently being held. This is consistent with all sibling `is_input__*_held` accessors (e.g., `is_input__forward_held`, `is_input__use_held`) that follow the identical pattern.

## 7. Implementation Correctness
- **Type compatibility:** `input_flags__held` is `Input_Flags__u32` (a typedef for `uint32_t`, see `defines.h:1155`). `INPUT_EXAMINE` is an `int`-typed preprocessor macro (`#define INPUT_EXAMINE (INPUT_USE_SECONDARY<<1)`, see `platform_defaults.h:212`). The bitwise AND promotes the `int` operand to `uint32_t` per the usual arithmetic conversions, yielding a `uint32_t` result. This value is implicitly converted to the `bool` return type: any nonzero value becomes `true`, zero becomes `false`. This is well-defined behavior in C (per `<stdbool.h>`, which is included transitively via `defines.h:7`). No lossy conversion occurs because the boolean result only depends on whether the value is zero or nonzero. ✓
- **Undefined behavior:** No pointer arithmetic, no out-of-bounds access, no type punning. The only dereference is `p_input->input_flags__held`, which is safe under the stated pre-condition that `p_input` is non-null. ✓
- **Validation:** No null-pointer check is performed. This is intentional and consistent with the entire `is_input__*` family of accessors, all of which assume a valid non-null `Input` pointer. Validation is the caller's responsibility and is documented via the pre-condition. ✓

## 8. Side Effects
No side effects. The function is a pure read-only query: it only reads `p_input->input_flags__held` and does not mutate any state (the `Input` struct, global state, or any other observable state).
