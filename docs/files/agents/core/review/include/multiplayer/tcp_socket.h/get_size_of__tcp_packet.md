get_size_of__tcp_packet — core/source/multiplayer/tcp_socket.c

Returns the recorded size (in bytes) of a TCP_Packet stored within a TCP_Socket's packet queue.

Pre-conditions:
1. p_tcp_socket must be a non-null pointer to a valid, initialized TCP_Socket object.
2. p_tcp_packet must be a non-null pointer to a TCP_Packet that points to an element within the p_tcp_socket->queue_of__tcp_packet array (or one past the last element). If p_tcp_packet does not point into this array, the pointer subtraction is undefined behavior.

Post-conditions:
1. Returns the Quantity__u32 value from p_tcp_socket->packet_size__entries at the index computed by the pointer subtraction (p_tcp_packet - p_tcp_socket->queue_of__tcp_packet).
2. No mutation of p_tcp_socket or p_tcp_packet occurs.

Correctness Verdict: Correct

Semantic Alignment:
The implementation correctly fulfills its semantic intent. It computes the index of the given p_tcp_packet within the queue_of__tcp_packet array using pointer arithmetic, then uses that index to look up the corresponding size entry in packet_size__entries. The two parallel arrays (queue_of__tcp_packet and packet_size__entries) are indexed consistently, so the correct size for the given packet is returned.

Implementation Correctness:
Type compatibility — The pointer subtraction (p_tcp_packet - p_tcp_socket->queue_of__tcp_packet) yields a ptrdiff_t, which is implicitly converted to an array index type. This is standard and safe for array indexing. The array elements are Quantity__u16 (uint16_t) and the return type is Quantity__u32 (uint32_t), which is a widening conversion with no loss of data.
Undefined behavior — The pointer subtraction is only well-defined if p_tcp_packet points to an element within (or one past the end of) the queue_of__tcp_packet array. This is a caller-enforced pre-condition; the function itself does not validate it. No other undefined behavior is present (no null dereference, no type punning, no out-of-bounds access assuming the pre-condition holds).
Validation — No validation is performed, which is appropriate for this low-level static inline accessor. The caller (e.g., get_latest__delivery_from__tcp_socket) is responsible for ensuring p_tcp_packet is valid and within the queue.

Side Effects:
No side effects. The function performs only read-only access to the TCP_Socket struct's packet_size__entries array and the queue_of__tcp_packet array (via pointer subtraction).
