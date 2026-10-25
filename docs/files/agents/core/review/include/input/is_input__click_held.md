# Function Review: `is_input__click_held`

**File of origin:** `core/include/input/input.h`

## Semantic

Returns whether the click input is currently held **and** the cursor has remained
stationary since the previous frame — i.e. a click held without an associated
drag. It is the logical inverse (cursor-wise) of `is_input__click_dragged`.

## Pre-conditions

1. `p_input` must be a non-null pointer to a valid, populated `Input` struct
   (convention in this header: all `is_input__*` accessors forgo null checks;
   validation is the caller's responsibility, consistent with the rest of the
   file).
2. The `Input` struct must have been advanced by `poll_input` (or equivalent) for
   the current frame so that `input_flags__held`, `cursor__3i32`, and
   `cursor__old__3i32` reflect frame-coherent state.

## Post-conditions

1. Returns `true` if and only if the `INPUT_CLICK` bit is set in
   `input_flags__held` **and** `cursor__3i32` equals `cursor__old__3i32`
   (all three `x__i32`/`y__i32`/`z__i32` components equal).
2. Returns `false` if the click is not held, or if the cursor has moved.
3. No `Input` fields are modified; the function is read-only.

## Correctness Verdict

**Correct**

## Semantic Alignment

The implementation fulfills its semantic intent. A "click held" that is stationary
(i.e. not a drag) is precisely the conjunction it computes: the click flag being
held plus the cursor position being unchanged from the prior frame. This pairs
symmetrically with `is_input__click_dragged` (same held-flag check, negated
cursor comparison). No semantic drift is present.

## Implementation Correctness

- **Type compatibility:** `input_flags__held` is `Input_Flags__u32` (`uint32_t`);
  `INPUT_CLICK` is a power-of-two bitmask (`1<<12`). The bitwise AND yields a
  `uint32_t` of value `0` or `INPUT_CLICK`, which is contextually converted to
  `bool` by the `&&` operator (nonzero→`true`, zero→`false`). No truncation or
  lossy conversion occurs; the final `return` matches the declared `bool` return.
- **Parameter passing to callee:** `is_vectors_3i32__equal` takes `Vector__3i32`
  by value, and both `cursor__3i32` and `cursor__old__3i32` are `Vector__3i32`
  members, so the argument types match exactly with no implicit conversion.
- **Undefined behavior:** No pointer arithmetic, null dereference, type punning,
  or out-of-bounds access. The only dereference is `p_input->...`, guarded by the
  non-null precondition. (The `Vector__3i32` members are scalars, so passing them
  by value to `is_vectors_3i32__equal` is well-defined.)
- **Validation:** Appropriate for the function's role — consistent with every
  sibling accessor in this header, which all assume a valid `p_input`. Null
  checking is the caller's responsibility per the file's established convention.

## Side Effects

No side effects. The function reads `input_flags__held`, `cursor__3i32`, and
`cursor__old__3i32` but does not write to any `Input` field or invoke any
mutating caller.
