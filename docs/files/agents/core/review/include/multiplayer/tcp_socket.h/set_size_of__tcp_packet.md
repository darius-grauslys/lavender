set_size_of__tcp_packet — core/source/multiplayer/tcp_socket.c

Sets the recorded size of a TCP packet in the socket's packet_size__entries array.

Pre-conditions:
1. p_tcp_socket must be a non-null pointer to a valid, initialized TCP_Socket.
2. p_tcp_packet must be a non-null pointer that points into the queue_of__tcp_packet array of p_tcp_socket (i.e., within the range [queue_of__tcp_packet, queue_of__tcp_packet + MAX_QUANTITY_OF__TCP_PACKETS_PER__SOCKET - 1]). The function does not validate this; it is the caller's responsibility.
3. size_of__packet is a Quantity__u32 (uint32_t). In practice it should not exceed MAX_SIZE_OF__TCP_PACKET (512 bytes), though no explicit range check is performed.

Post-conditions:
1. The packet_size__entries entry at the index corresponding to p_tcp_packet is overwritten with size_of__packet (narrowed to Quantity__u16).
2. No other state is modified.

Correctness Verdict: Correct

Semantic Alignment:
The function's intent is to record the size of a specific TCP packet within the socket's tracking array. It computes the array index via pointer subtraction (p_tcp_packet - p_tcp_socket->queue_of__tcp_packet), which correctly yields the offset of the packet within the queue. The size is then stored at the corresponding index in packet_size__entries. The implementation fulfills the semantic intent.

Implementation Correctness:
Type compatibility — the parameter size_of__packet is Quantity__u32 (uint32_t), but the target field packet_size__entries is Quantity__u16 (uint16_t). This is an implicit narrowing conversion. In practice this is safe because MAX_SIZE_OF__TCP_PACKET is BIT(9) = 512, so the value will always fit within a u16. However, the type mismatch is technically present.
Undefined behavior — the pointer arithmetic (p_tcp_packet - p_tcp_socket->queue_of__tcp_packet) is only well-defined if p_tcp_packet points within the queue_of__tcp_packet array (or one-past-the-end). If the caller passes a pointer outside this array, the subtraction is undefined behavior. No validation is performed within the function; this is the caller's responsibility. This matches the pattern used by the companion function get_size_of__tcp_packet.
Validation — no validation is performed, which is appropriate for a low-level inline helper. The caller is responsible for ensuring p_tcp_packet is a valid pointer into the queue.

Side Effects:
Mutates p_tcp_socket->packet_size__entries at the computed index. No other side effects.
