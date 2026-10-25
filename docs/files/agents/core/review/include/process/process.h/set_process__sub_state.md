set_process__sub_state — core/include/process/process.h

Sets the sub-state field of a Process struct.

Pre-conditions:
1. p_this_process must be a non-null pointer to a valid, writable Process object.
2. sub_state__u8 may be any u8 value; no range constraint is enforced.

Post-conditions:
1. p_this_process->process_sub_state__u8 is overwritten with the value of sub_state__u8.

Correctness Verdict: Correct

Semantic Alignment:
The function performs a direct field assignment: it writes the provided u8 value into the process_sub_state__u8 member of the Process struct. This matches the semantic intent of the function name. The process_sub_state__u8 field is a member of a union (alongside process_value_bytes__u8), and writing to it is a valid operation that sets the sub-state of the process. No struct fields are omitted or reordered — the function only touches the single field it is named after.

Implementation Correctness:
Type compatibility — the parameter sub_state__u8 is of type u8 (typedef uint8_t), and the target field process_sub_state__u8 is also of type u8. The types match exactly with no implicit conversions or truncation.
Undefined behavior — no pointer arithmetic, no type punning, no out-of-bounds access. The only dereference is p_this_process->process_sub_state__u8, which is valid as long as p_this_process points to a valid Process object.
Validation — no null check is performed on p_this_process. This is consistent with other simple inline setters in the same file (e.g., set_process_as__enqueued, set_process_as__dequeued) that also perform direct field assignment without NDEBUG-guarded null checks. The caller is responsible for ensuring p_this_process is valid.

Side Effects:
Mutates p_this_process->process_sub_state__u8 by overwriting its value with the provided sub_state__u8.
