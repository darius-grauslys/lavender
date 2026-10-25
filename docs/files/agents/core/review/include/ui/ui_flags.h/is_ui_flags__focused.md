is_ui_flags__focused — core/include/ui/ui_flags.h

## Semantic
Returns whether a UI element is considered "focused" by checking if it is currently being held or being dragged.

## Pre-conditions
1. `ui_flags__u8` is a valid `UI_Flags__u16` value (a 16-bit unsigned integer containing bit flags).

## Post-conditions
1. Returns `true` if either `UI_FLAGS__BIT_IS_BEING_HELD` or `UI_FLAGS__BIT_IS_BEING_DRAGGED` is set in the flags; returns `false` otherwise.
2. The input parameter is not modified (passed by value).

## Correctness Verdict
Correct

## Semantic Alignment
The implementation correctly fulfills the semantic intent of determining whether a UI element is "focused" based on being held or dragged. The function delegates to the existing `is_ui_flags__being_held` and `is_ui_flags__being_dragged` helper functions, which perform proper bitwise AND checks against `UI_FLAGS__BIT_IS_BEING_HELD` and `UI_FLAGS__BIT_IS_BEING_DRAGGED` respectively. The logical OR combination is semantically appropriate for "focused" meaning either condition.

## Implementation Correctness
- **Type compatibility**: The parameter type `UI_Flags__u16` (typedef for `uint16_t`) matches the expected type for the flag-checking functions. No implicit conversions or truncation occur.
- **Undefined behavior**: None. The function performs only bitwise operations and logical OR on boolean results. No pointer dereferencing, no array access, no null pointer risk.
- **Validation**: No validation is needed for this function's role. It operates on a simple bitfield value passed by value, and it is the caller's responsibility to provide meaningful flag values.

## Side Effects
No side effects. The function is pure — it reads its parameter by value and returns a boolean result without modifying any state.
