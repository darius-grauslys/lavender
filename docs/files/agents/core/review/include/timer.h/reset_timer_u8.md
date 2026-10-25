reset_timer_u8 — core/include/timer.h

Resets a Timer__u8's remaining time to its stored start value.

Pre-conditions:
1. timer__u8 must be a non-null pointer to a writable Timer__u8 object.
2. timer__u8->start__u8 must have been previously initialized to a valid value (typically via initialize_timer_u8 or get_timer__u8).

Post-conditions:
1. timer__u8->remaining__u8 is set to timer__u8->start__u8.
2. timer__u8->start__u8 is unchanged.

Correctness Verdict: Correct

Semantic Alignment:
This function follows the Lavender-style "reset" pattern — it does not perform resource acquisition (RAII). It restores the timer to its initial countdown value by copying start__u8 into remaining__u8, which is the correct semantic intent for resetting a timer. The implementation matches this intent precisely.

Implementation Correctness:
Type compatibility — timer__u8 is a Timer__u8*, and both remaining__u8 and start__u8 are uint8_t fields, so the assignment is type-safe with no implicit conversions or truncation.
Undefined behavior — no pointer arithmetic, no null dereference (assuming the non-null pre-condition is met), no type punning, no out-of-bounds access.
Validation — no validation is performed beyond the pre-condition that the pointer is non-null. This is appropriate for a low-level inline utility function; null-checking would be the caller's responsibility.

Side Effects:
Mutates timer__u8->remaining__u8 to equal timer__u8->start__u8. The start__u8 field is not modified.
