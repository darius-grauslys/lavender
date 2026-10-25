is_process__sub_process — core/include/process/process.h

Checks whether the given Process has the PROCESS_FLAG__IS_SUB_PROCESS bit set in its process_flags__u8 field.

Pre-conditions:
1. p_process must be a non-null pointer to a valid Process object. Unlike many other functions in process.h, this function does NOT perform a null check (consistent with is_process__critical and other flag-checking helpers in the same file).

Post-conditions:
1. Returns true if the PROCESS_FLAG__IS_SUB_PROCESS bit (BIT(1)) is set in p_process->process_flags__u8; returns false otherwise.
2. No state is mutated; the Process object is read-only.

Correctness Verdict: Correct

Semantic Alignment:
The implementation correctly checks the sub-process flag by performing a bitwise AND between process_flags__u8 and PROCESS_FLAG__IS_SUB_PROCESS (defined as BIT(1) = 2). The integer result of the AND is implicitly converted to bool (zero becomes false, non-zero becomes true), which is the correct semantic for a boolean flag query. This matches the established pattern used by the sibling function is_process__critical.

Implementation Correctness:
Type compatibility — p_process is Process *, and process_flags__u8 is Process_Flags__u8 (uint8_t). PROCESS_FLAG__IS_SUB_PROCESS is BIT(1) which evaluates to ((1U) << 1) = 2, an unsigned int that is compatible with uint8_t in the bitwise AND. The result (uint8_t) is implicitly converted to bool for the return type, which is well-defined in C (0 → false, non-zero → true). No truncation or data loss occurs.
No undefined behavior — no pointer arithmetic, no null dereference (caller's responsibility), no type punning, no out-of-bounds access. The function reads a single uint8_t field and performs a bitwise operation.
Validation — no validation is performed within this function. This is appropriate for a low-level inline flag-checking helper; the caller is responsible for ensuring p_process is valid. This is consistent with the pattern used by is_process__critical and other similar helpers in the same file.

Side Effects:
No side effects — this is a pure query function. It reads p_process->process_flags__u8 and returns a boolean result without modifying any state.