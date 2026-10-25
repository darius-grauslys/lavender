m_poll_tcp_socket_manager_as__client__default — core/source/multiplayer/client__default.c, lines 10-49

Polls the client's single TCP socket (index 0, the connection to the server) for incoming
connection state, receives any pending bytes, dequeues the next TCP delivery packet, and
dispatches it as an inbound Game_Action to the local client (index 0).

Pre-conditions:
1. p_tcp_socket_manager must be a non-null pointer to an initialized TCP_Socket_Manager.
2. p_game must be a non-null pointer to an initialized Game.
3. The client pool must have been allocated and must contain at least one client at index 0;
   get_p_client_by__index_from__game(p_game, 0) must return a valid (non-null) Client *.
   If it returns NULL, GET_UUID_P(p_client) dereferences NULL (undefined behavior).
4. p_tcp_socket_manager->tcp_sockets[0] is treated as the socket to the server; it is
   always a valid in-bounds array access (MAX_QUANTITY_OF__TCP_SOCKETS >= 1), but the
   socket may be in any state (None/Disconnected/Connecting/Connected/Authenticated).
5. p_game->m_game_action_handler__receive must be non-null (receive_game_action is a
   non-null inline that calls through this function pointer).

Post-conditions:
1. The function returns void; it has no return value.
2. If the socket is in the Connected or Authenticated state, any newly received bytes are
   read into the socket's internal packet queue, and then at most ONE queued delivery is
   dequeued and dispatched to the local client via receive_game_action.
3. If the socket is in any other state (None, Disconnected, Connecting, Authenticating,
   Unknown), or if receive_bytes_over__tcp_socket returns 0, no delivery is dequeued and
   no Game_Action is dispatched; the function simply returns.
4. The TCP_Socket at index 0 may be mutated: its packet queue (quantity_of__received_packets,
   index_of__enqueue_begin, and queue_of__tcp_packet entries) is advanced by
   receive_bytes_over__tcp_socket and get_latest__delivery_from__tcp_socket.

Correctness Verdict: Incorrect

Semantic Alignment:
The high-level intent — poll the client's server-bound socket and dispatch received game
actions to the local client — is implemented, but the implementation diverges from the
reference server-side implementation (m_poll_tcp_socket_manager_as__server__default) in
two significant ways that cause both a functional defect and a latent undefined-behavior
risk:

1. The return value of get_latest__delivery_from__tcp_socket is ignored. The server
   reference wraps this call in a "while" loop:
       while (get_latest__delivery_from__tcp_socket(p_tcp_socket__client, &deliver.tcp_packet)) { ... }
   This (a) correctly handles the case where no packet is available and (b) drains ALL
   queued packets per poll. The client version calls it once unconditionally, so:
   - If get_latest__delivery_from__tcp_socket returns false (queue empty), the "delivery"
     union is left uninitialized and is then read as delivery.game_action (see
     Implementation Correctness).
   - Even when packets are available, only ONE packet is processed per poll cycle instead
     of draining the queue, so the client can fall behind the server and effectively drop
     or starve inbound game actions — a functional packet-loss defect.

2. The game action's uuid_of__client__u32 is hardcoded to 0, whereas the server reference
   sets it to GET_UUID_P(p_tcp_socket__client) (the originating socket's uuid). For the
   client receiving from the server this may be intentional (clearing/neutralizing the
   field for a server-originated action), but it is inconsistent with the server pattern
   and its correctness depends on downstream handlers not relying on this field. This is
   flagged as a semantic observation rather than a definite defect.

Implementation Correctness:
- Type compatibility: All parameter types match their targets. GET_UUID_P(p_client)
  correctly reads the Client's Serialization_Header.uuid (Client's first member is
  _serialization_header). delivery.game_action.uuid_of__client__u32 is Identifier__u32
  assigned 0 — no truncation or conversion issue. The union aliasing of TCP_Packet bytes
  as Game_Action matches the TCP_DELIVERY idiom used throughout the codebase.
- Undefined behavior: The "delivery" union is declared without an initializer. When
  get_latest__delivery_from__tcp_socket returns false, delivery is uninitialized; the
  subsequent read of delivery.game_action (including the assignment to
  delivery.game_action.uuid_of__client__u32 and the full-struct read by
  receive_game_action) constitutes reading uninitialized memory — undefined behavior.
  In the current happy path this is not triggered (receive_bytes_over__tcp_socket only
  returns non-zero when quantity_of__received_packets > 0, so get_latest__delivery_from__tcp_socket
  returns true), but the unchecked call makes the code fragile and incorrect by the
  codebase's own reference standard.
- Error-code handling: The guard "if (!receive_bytes_over__tcp_socket(...))" tests only
  for a zero return. receive_bytes_over__tcp_socket returns i32: positive on success,
  0 on no-data/destination-overflow, and a NEGATIVE value (TCP_ERROR__QUEUE_FULL = -2)
  when the receive queue is full. Because "!(-2)" evaluates to false, a queue-full error
  is treated as "data received" and processing proceeds. This is the same flawed pattern
  used in the server reference, so it appears to be an accepted (if technically incorrect)
  codebase idiom; it is noted here for completeness but is not unique to this function.
- Validation: No null-check on p_client before GET_UUID_P(p_client) — this is a
  precondition (see Pre-condition 3), acceptable for a default handler, but a debug-build
  assertion would improve robustness.

Side Effects:
- Mutates the TCP_Socket at tcp_sockets[0]: receive_bytes_over__tcp_socket appends packets
  to the socket's internal queue, and get_latest__delivery_from__tcp_socket dequeues one
  packet (advancing index_of__enqueue_begin and decrementing quantity_of__received_packets).
- Dispatches an inbound Game_Action to the local client via receive_game_action, which
  may mutate client/game state (e.g., enqueueing processes, updating input, spawning
  entities) depending on the game action handler.
- The p_game pointer is read (client pool lookup, game-action dispatch) but the Game
  struct itself is not directly written by this function beyond what receive_game_action
  does through its handler.
- No side effects on p_tcp_socket_manager beyond the single tcp_sockets[0] entry.
