set_structure_as__allocated — core/include/world/structures/structure.h

### Semantic
Sets the `STRUCTURE_FLAG__IS_ALLOCATED` bit in the `structure_flags` field of the given `Structure`, marking it as allocated.

### Pre-conditions
1. `p_structure` must be a non-null pointer to a valid `Structure` instance.

### Post-conditions
1. After return, `p_structure->structure_flags` has the `STRUCTURE_FLAG__IS_ALLOCATED` bit set (i.e., `is_structure__allocated(p_structure)` returns true).
2. All other bits in `p_structure->structure_flags` are preserved unchanged.
3. No other fields of the `Structure` struct are modified.

### Correctness Verdict
Correct

### Semantic Alignment
The implementation correctly fulfills its semantic intent: it sets the allocated flag using a bitwise OR with `STRUCTURE_FLAG__IS_ALLOCATED` (defined as `BIT(0)`, i.e., `1 << 0`). This is the standard idiom for setting a single bit in a flags field, and it aligns with the companion functions `is_structure__allocated` (which tests the same bit with a bitwise AND) and `set_structure_as__deallocated` (which clears the same bit with a bitwise AND-NOT). No semantic drift is present.

### Implementation Correctness
- **Type compatibility:** `structure_flags` is of type `Structure_Flags__u8` (a `uint8_t`), and `STRUCTURE_FLAG__IS_ALLOCATED` is `BIT(0)` which expands to `((1U) << (0))` — an `unsigned int` value of 1. The bitwise OR assignment `|=` between a `uint8_t` lvalue and an `unsigned int` rvalue is well-defined; the result is implicitly converted back to `uint8_t` without truncation since the value fits. No type mismatch or truncation issue.
- **Undefined behavior:** No pointer arithmetic, no null dereference (caller must pass non-null), no type punning, and no out-of-bounds access. The operation is a single, safe bitwise OR on a scalar field.
- **Validation:** This is a low-level inline setter with no validation logic, which is appropriate for its role. Null-checking is the caller's responsibility, consistent with the pattern used by all sibling inline functions in this header (e.g., `is_structure__allocated`, `set_the_kind_of__structure`).

### Side Effects
- Mutates `p_structure->structure_flags` by setting the `STRUCTURE_FLAG__IS_ALLOCATED` bit.
- No other memory, state, or I/O side effects.
