is_ui_flags__being_dragged — core/include/ui/ui_flags.h

Checks whether the "being dragged" flag bit is set in a UI flags value.

Pre-conditions:
1. ui_flags__u8 is any UI_Flags__u16 value (a uint16_t); no range constraint needed.

Post-conditions:
1. Returns true if the UI_FLAGS__BIT_IS_BEING_DRAGGED bit (BIT(4), i.e. 0x10) is set in ui_flags__u8; returns false otherwise.
2. No state is mutated.

Correctness Verdict: Correct

Semantic Alignment:
The implementation correctly checks whether the "being dragged" flag bit is set by performing a bitwise AND between the flags value and UI_FLAGS__BIT_IS_BEING_DRAGGED. The result is cast to bool, which correctly converts any non-zero value to true and zero to false. This matches the semantic intent of querying a single boolean flag.

Implementation Correctness:
Type compatibility — the parameter type UI_Flags__u16 (uint16_t) matches the type used in all other is_ui_flags__* functions. The constant UI_FLAGS__BIT_IS_BEING_DRAGGED is BIT(4) which expands to ((1U) << 4) = 0x10, a value that fits within uint16_t. The bitwise AND and bool cast are well-defined operations. No implicit conversions or truncation occur.
No undefined behavior — no pointer arithmetic, no null dereference, no type punning, no out-of-bounds access.
No validation is needed — this is a pure query function operating on a value parameter.

Side Effects:
No side effects.
