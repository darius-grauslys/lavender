m_process__game_action__entity__get__inbound_server__init — core/source/game_action/core/entity/game_action__entity__get.c

Lavender-style initialization that zeroes the TCP payload bitmap within the entity Get game action's payload and assigns the process run handler for the inbound server execution phase.

Pre-conditions:
1. p_this_process must be a non-null pointer to a valid Process whose p_process_data points to a valid Game_Action of kind Game_Action_Kind__Entity__Get.
2. p_game may be used by the process run handler but is not directly accessed by this init function.

Post-conditions:
1. The tcp_payload_bitmap field within the GA_Entity__Payload union of the game action is zeroed (set to all 0x00 bytes).
2. p_this_process->m_process_run__handler is assigned to m_process__game_action__entity__get__inbound_server.

Correctness Verdict: Correct

Semantic Alignment:
This is a Lavender-style initialization — it resets the TCP payload bitmap to its initial (zeroed) state and sets the process run handler. It does NOT acquire any resources (not RAII-style). The memset uses SIZE_OF__TCP_PAYLOAD_BITMAP__ENTITY which is computed as the size of the tcp_payload_bitmap field within GA_Entity__Payload, ensuring the entire bitmap is zeroed. The run handler is correctly assigned to the corresponding inbound server process function. All operations are consistent with the semantic intent of preparing the process for execution.

Implementation Correctness:
Type compatibility — get_p_tcp_payload_bitmap__ga_entity__payload returns u8*, which is correct for memset's first parameter. SIZE_OF__TCP_PAYLOAD_BITMAP__ENTITY is a size_t-compatible value from sizeof. The assignment of m_process_run__handler is a direct function pointer assignment with no conversion issues.
No undefined behavior — get_p_tcp_payload_bitmap__ga_entity__payload accesses p_game_action->_ga_payload_union, which is valid as long as p_process_data points to a valid Game_Action. The memset operates on a valid field within that struct. No out-of-bounds access, no null dereference (assuming pre-conditions hold), no type punning.
No validation is performed — this is consistent with the function's role as a low-level init. It is the caller's responsibility to ensure p_this_process and p_process_data are valid.

Side Effects:
Mutates the Game_Action pointed to by p_this_process->p_process_data: zeroes the tcp_payload_bitmap field. Mutates p_this_process: assigns m_process_run__handler to m_process__game_action__entity__get__inbound_server.
