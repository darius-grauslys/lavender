set_p_ui_flags__u8_as__being_dragged — core/include/ui/ui_flags.h

Sets the "is being dragged" flag bit in a UI_Flags__u16 flags field via bitwise OR.

Pre-conditions:
1. p_ui_flags__u8 must be a non-null pointer to a writable UI_Flags__u16 (uint16_t) object.
2. The pointed-to UI_Flags__u16 may have any initial value; no specific bit pattern is required beforehand.

Post-conditions:
1. The UI_FLAGS__BIT_IS_BEING_DRAGGED bit (bit 4, value BIT(4)) is set in the pointed-to UI_Flags__u16.
2. All other bits in the pointed-to UI_Flags__u16 remain unchanged (preserved by the |= operation).

Correctness Verdict: Correct

Semantic Alignment:
The implementation correctly fulfills its semantic intent: marking a UI element as "being dragged" by setting the corresponding flag bit via bitwise OR. The operation is idempotent — calling it when the bit is already set leaves the flags unchanged. This matches the expected behavior of a flag-setting helper.

Implementation Correctness:
Type compatibility — p_ui_flags__u8 is typed as UI_Flags__u16 * (i.e., uint16_t *). Dereferencing yields UI_Flags__u16 (uint16_t), which is the correct type for the |= operation. UI_FLAGS__BIT_IS_BEING_DRAGGED is defined as BIT(4), a compile-time integer constant compatible with uint16_t. No implicit conversions or truncation occur.
Undefined behavior — no pointer arithmetic, no null dereference (null checking is the caller's responsibility for inline helpers), no type punning, no out-of-bounds access.
Validation — no validation is needed or appropriate; this is a low-level inline flag setter. The caller is responsible for ensuring p_ui_flags__u8 is valid and non-null.

Side Effects:
Mutates the UI_Flags__u16 pointed to by p_ui_flags__u8 by setting the UI_FLAGS__BIT_IS_BEING_DRAGGED bit (bit 4). No other memory or state is affected.
