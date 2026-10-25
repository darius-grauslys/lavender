set_p_ui_flags__u8_as__disabled — core/include/ui/ui_flags.h

Clears the IS_ENABLED bit in a UI_Flags__u16, marking the UI element as disabled while preserving all other flag bits.

Pre-conditions:
1. p_ui_flags__u8 must be a non-null pointer to a writable UI_Flags__u16 (uint16_t) object.

Post-conditions:
1. The IS_ENABLED bit (UI_FLAGS__BIT_IS_ENABLED, BIT(0)) of *p_ui_flags__u8 is cleared (set to 0).
2. All other bits in *p_ui_flags__u8 remain unchanged.

Correctness Verdict: Correct

Semantic Alignment:
The implementation correctly clears the IS_ENABLED bit, fulfilling the semantic intent of "disabling" the UI flags. This is the exact complement of set_p_ui_flags__u8_as__enabled, which sets the same bit via |=. The pattern is consistent with other bit-clearing functions in the file (e.g., set_p_ui_flags__u8_as__deallocated, set_p_ui_flags__u8_as__dropped), which all use &= ~ to clear the relevant bit(s).

Implementation Correctness:
Type compatibility — p_ui_flags__u8 is UI_Flags__u16 * (uint16_t *); UI_FLAGS__BIT_IS_ENABLED is BIT(0) = 1U; the &= and ~ operations are well-defined on uint16_t. No implicit conversions or truncation.
Undefined behavior — no pointer arithmetic, no type punning, no out-of-bounds access. The dereference *p_ui_flags__u8 is safe assuming the caller provides a valid non-null pointer (caller responsibility).
Validation — no validation is needed; this is a low-level inline bit-manipulation function. The caller is responsible for ensuring p_ui_flags__u8 is valid.

Side Effects:
Mutates *p_ui_flags__u8 by clearing the IS_ENABLED bit (UI_FLAGS__BIT_IS_ENABLED). All other bits are preserved.

Note: The parameter name uses the __u8 suffix (p_ui_flags__u8) despite the type being UI_Flags__u16 (uint16_t). This naming inconsistency is consistent across all functions in this header and is a pre-existing convention rather than an issue specific to this function.
