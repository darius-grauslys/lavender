poll_for__uuid_collision__uuid_64 — core/source/serialization/hashing.c, lines 56-84

Linearly probes a contiguous array of Serialization_Header__UUID_64 entries for a slot that is either deallocated (uuid == IDENTIFIER__UNKNOWN__u64) or contains a matching uuid. Returns the index of the first such slot, or INDEX__UNKNOWN__u32 if the array is full.

Pre-conditions:
1. p_serialization_headers must be a non-null pointer to a contiguous array of Serialization_Header__UUID_64 structs.
2. length_of__p_serialization_headers must be greater than 0 (used as divisor in modulo operations).
3. The first element's size_of__struct field must be correctly set to the sizeof the actual serialized struct (not just sizeof(Serialization_Header__UUID_64)), as it is used for stride-based pointer arithmetic across the array.
4. identifier__u64 may be any u64 value, including IDENTIFIER__UNKNOWN__u64.
5. index__initial__u32 may be INDEX__UNKNOWN__u32 (to start probing from the hash of identifier__u64) or a valid index (to resume probing from index__initial__u32 + 1).

Post-conditions:
1. If a deallocated or matching slot is found, returns its Index__u32 within [0, length_of__p_serialization_headers - 1].
2. If no such slot exists (array is full and no match found), returns INDEX__UNKNOWN__u32.
3. No mutation of p_serialization_headers or any struct in the array occurs.

Correctness Verdict: Correct

Semantic Alignment:
The implementation faithfully mirrors the u32 counterpart (poll_for__uuid_collision) with appropriate type widening for 64-bit UUIDs. The linear probing logic is identical: it computes the starting probe position as either (index__initial__u32 + 1) % length or identifier__u64 % length, then iterates through all slots in the array, returning the first deallocated or matching slot. The loop correctly terminates when it wraps around to the starting position, and INDEX__UNKNOWN__u32 is returned if the full cycle completes without finding a suitable slot.

Implementation Correctness:
Type compatibility: All parameter types match their target usages. The identifier__u64 parameter (Identifier__u64 / uint64_t) is correctly used with is_identifier_u64_matching__serialization_header and in modulo arithmetic. The index__initial__u32 parameter (Index__u32 / uint32_t) is promoted to uint64_t in the ternary expression when combined with identifier__u64 — this is a safe widening conversion. The return value current_identifier (uint64_t) is implicitly narrowed to Index__u32 (uint32_t) on return, but this is safe because the modulo operations guarantee the value is always within [0, length_of__p_serialization_headers - 1], which fits in uint32_t. The size_of__struct field (Quantity__u32 / uint32_t) is read from the first header and used in pointer arithmetic; the multiplication current_identifier * size_of__struct is performed in uint64_t arithmetic, which is correct and avoids any truncation.

Undefined behavior: No broken pointer arithmetic, no null dereference, no type punning, no out-of-bounds access. The pointer arithmetic p_bytes + current_identifier * size_of__struct correctly computes the address of each element in the contiguous array. The do-while loop guarantees at least one iteration, and the modulo-based wraparound ensures all indices in [0, length-1] are visited exactly once before the loop terminates.

Validation: No input validation is performed within this function, which is appropriate for its role as a low-level hashing/probing utility. Validation of p_serialization_headers and length_of__p_serialization_headers is the responsibility of the caller.

Side Effects:
No side effects. The function is pure read-only: it reads from p_serialization_headers (via the first element's size_of__struct field and subsequent elements' uuid fields) but does not modify any memory.
