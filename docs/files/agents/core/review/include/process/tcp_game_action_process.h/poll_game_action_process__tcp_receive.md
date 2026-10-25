poll_game_action_process__tcp_receive — core/source/process/tcp_game_action_process.c

Polls the TCP packet bitmap to determine whether all anticipated TCP packets have arrived for a serialization request associated with a process.

Pre-conditions:
1. p_game may be any Game pointer or NULL — it is not used by this function.
2. p_process must be a non-null pointer to a valid Process whose p_process_data points to an activated Serialization_Request.
3. p_process->p_process_data must point to a Serialization_Request that has been activated via activate_serialization_request with is_serialization_request__tcp_or__io == true, so that pM_packet_bitmap is non-null and quantity_of__tcp_packets__anticipated is set.
4. (Debug only) The Serialization_Request must have the SERIALIZATION_REQUEST_FLAG__IS_TCP_OR_IO flag set; otherwise PLATFORM_Read_File_Error__Unknown is returned.

Post-conditions:
1. Returns PLATFORM_Read_File_Error__End_Of_File when all anticipated TCP packets have arrived (i.e., the bitmap has no unset bits within the range [0, quantity_of__tcp_packets__anticipated)).
2. Returns PLATFORM_Read_File_Error__System_Busy when at least one anticipated TCP packet has not yet arrived.
3. Returns PLATFORM_Read_File_Error__Unknown (debug builds only) when the Serialization_Request is not flagged as TCP/IO.
4. No state is mutated; the function is read-only with respect to all parameters.

Correctness Verdict: Correct

Semantic Alignment:
The implementation fulfills the semantic intent as documented in the header: it returns System_Busy while packets are still missing and End_Of_File once all anticipated packets have been received. The function correctly delegates to get_tcp_packet__bitmap_data to find the first unset bit in the packet bitmap, then compares the result against quantity_of__tcp_packets__anticipated to determine completion.

Note: The inline comment in the .c file (line 95) states "after which it will return None," which is inconsistent with both the header documentation (which says "End_Of_File") and the actual implementation (which returns End_Of_File). This is a documentation discrepancy in the .c file only; the implementation matches the header.

Implementation Correctness:
Type compatibility — index_of__bitmap_bit is Index__u32 (uint32_t) and is compared against quantity_of__tcp_packets__anticipated which is Quantity__u16 (uint16_t). The uint16_t is implicitly promoted to uint32_t for the comparison, which is safe and lossless. No truncation occurs.
Undefined behavior — no out-of-bounds access: get_tcp_packet__bitmap_data accesses p_bitmap up to index TCP_PAYLOAD_BYTE(quantity_of__tcp_packets__anticipated), and the bitmap is allocated with (quantity_of__tcp_packets__anticipated >> 3) + 1 bytes (see activate_serialization_request), so the access is always within bounds. No null dereference occurs assuming pre-conditions are met. No type punning or broken pointer arithmetic.
Validation — the debug-only check validates the TCP/IO flag but does not check for null p_process or null pM_packet_bitmap. This is consistent with the codebase's pattern of assuming valid inputs in release builds; the caller is responsible for ensuring pre-conditions. The unused p_game parameter is a minor code smell but does not affect correctness.

Side Effects:
No side effects. The function reads from the Serialization_Request's packet bitmap and returns an error code. No state is mutated.
