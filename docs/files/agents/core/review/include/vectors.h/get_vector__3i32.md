# get_vector__3i32

**File of origin:** `core/include/vectors.h`

## Semantic

Constructs and returns a `Vector__3i32` struct from three signed 32-bit integer components (`x`, `y`, `z`). This is a pure factory/constructor function that packs three scalar values into the corresponding fields of a 3-component integer vector.

## Pre-conditions

1. `x`, `y`, and `z` are valid `Signed_Index__i32` (`int32_t`) values. No range restrictions are imposed by the function itself.
2. No pointer parameters; all inputs are passed by value. No null-check requirements.

## Post-conditions

1. Returns a `Vector__3i32` struct where `.x__i32` equals the `x` argument, `.y__i32` equals the `y` argument, and `.z__i32` equals the `z` argument.
2. All three fields of the returned struct are explicitly assigned; no field is omitted or left uninitialized.
3. The returned struct is a new, independent value — no aliasing or shared state.

## Correctness Verdict

**Correct**

## Semantic Alignment

The implementation fully fulfills the semantic intent. The function constructs a `Vector__3i32` by assigning each parameter to its corresponding struct field (`x→x__i32`, `y→y__i32`, `z→z__i32`). The struct initializer uses positional initialization matching the declared field order (`x__i32`, `y__i32`, `z__i32`), so no reordering occurs. All struct fields are assigned — none omitted.

## Implementation Correctness

- **Type compatibility:** All three parameters are `Signed_Index__i32` (`int32_t`), which exactly matches the type of each corresponding field in `Vector__3i32` (also `Signed_Index__i32`). No implicit conversions, truncation, or sign mismatches occur.
- **Undefined behavior:** None. The function performs no pointer dereference, no array indexing, no type punning, and no arithmetic that could overflow. It simply returns a stack-initialized struct by value.
- **Validation:** No validation is needed or appropriate for this role — it is a trivial value constructor. Validation of vector component ranges (if ever required) is the caller's responsibility.

## Side Effects

No side effects. The function is pure: it reads only its parameters and returns a new `Vector__3i32` value without modifying any global state, memory, or I/O.
