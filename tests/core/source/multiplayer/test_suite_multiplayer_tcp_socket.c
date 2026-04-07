#include <multiplayer/test_suite_multiplayer_tcp_socket.h>

#include <multiplayer/tcp_socket.c>
#include <multiplayer/ipv4_address.h>

///
/// @spec    docs/specs/core/multiplayer/tcp_socket.h.spec.md
/// @section 1.4.1 Initialization
/// @section 1.5.5 Postconditions
/// @brief   After initialize_tcp_socket, state is None.
///
TEST_FUNCTION(initialize_tcp_socket__sets_state_to_none) {
    TCP_Socket socket;
    IPv4_Address addr;
    populate_ipv4_address(&addr, "127.0.0.1", "8080");
    initialize_tcp_socket(&socket, addr, 42);
    munit_assert_int(get_state_of__tcp_socket(&socket), ==, TCP_Socket_State__None);
    return MUNIT_OK;
}

///
/// @spec    docs/specs/core/multiplayer/tcp_socket.h.spec.md
/// @section 1.4.1 Initialization
/// @section 1.5.5 Postconditions
/// @brief   After initialize_tcp_socket, UUID matches the provided value.
///
TEST_FUNCTION(initialize_tcp_socket__sets_uuid) {
    TCP_Socket socket;
    IPv4_Address addr;
    populate_ipv4_address(&addr, "127.0.0.1", "8080");
    initialize_tcp_socket(&socket, addr, 42);
    munit_assert_uint32(socket._serialization_header.uuid, ==, 42);
    return MUNIT_OK;
}

///
/// @spec    docs/specs/core/multiplayer/tcp_socket.h.spec.md
/// @section 1.4.1 Initialization
/// @section 1.5.5 Postconditions
/// @brief   After initialize_tcp_socket, packet queue is empty.
///
TEST_FUNCTION(initialize_tcp_socket__packet_queue_is_empty) {
    TCP_Socket socket;
    IPv4_Address addr;
    populate_ipv4_address(&addr, "127.0.0.1", "8080");
    initialize_tcp_socket(&socket, addr, 42);
    munit_assert_uint32(socket.quantity_of__received_packets, ==, 0);
    return MUNIT_OK;
}

///
/// @spec    docs/specs/core/multiplayer/tcp_socket.h.spec.md
/// @section 1.4.1 Initialization
/// @section 1.5.5 Postconditions
/// @brief   After initialize_tcp_socket, platform socket pointer is null.
///
TEST_FUNCTION(initialize_tcp_socket__platform_socket_is_null) {
    TCP_Socket socket;
    IPv4_Address addr;
    populate_ipv4_address(&addr, "127.0.0.1", "8080");
    initialize_tcp_socket(&socket, addr, 42);
    munit_assert_ptr_null(get_p_PLATFORM_tcp_socket_from__tcp_socket(&socket));
    return MUNIT_OK;
}

///
/// @spec    docs/specs/core/multiplayer/tcp_socket.h.spec.md
/// @section 1.4.1 Initialization
/// @section 1.5.5 Postconditions
/// @brief   After initialize_tcp_socket, flags are zero.
///
TEST_FUNCTION(initialize_tcp_socket__flags_are_zero) {
    TCP_Socket socket;
    IPv4_Address addr;
    populate_ipv4_address(&addr, "127.0.0.1", "8080");
    initialize_tcp_socket(&socket, addr, 42);
    munit_assert_uint8(get_tcp_socket_flags_from__tcp_socket(&socket), ==, 0);
    return MUNIT_OK;
}

///
/// @spec    docs/specs/core/multiplayer/tcp_socket.h.spec.md
/// @section 1.4.1 Initialization
/// @section 1.5.5 Postconditions
/// @brief   After initialize_tcp_socket_as__deallocated, socket is marked
///          as available for reuse in the pool.
///
TEST_FUNCTION(initialize_tcp_socket_as__deallocated__clears_socket) {
    TCP_Socket socket;
    IPv4_Address addr;
    populate_ipv4_address(&addr, "127.0.0.1", "8080");
    initialize_tcp_socket(&socket, addr, 42);
    initialize_tcp_socket_as__deallocated(&socket);
    munit_assert_true(
        is_serialized_struct__deallocated(
            &socket._serialization_header));
    return MUNIT_OK;
}

///
/// @spec    docs/specs/core/multiplayer/tcp_socket.h.spec.md
/// @section 1.4.5 Queries (static inline)
/// @section 1.3.2 TCP_Socket_State
/// @brief   set_state_of__tcp_socket sets state to Connected,
///          get_state_of__tcp_socket returns Connected.
///
TEST_FUNCTION(set_state_of__tcp_socket__updates_state) {
    TCP_Socket socket;
    IPv4_Address addr;
    populate_ipv4_address(&addr, "127.0.0.1", "8080");
    initialize_tcp_socket(&socket, addr, 42);
    set_state_of__tcp_socket(&socket, TCP_Socket_State__Connected);
    munit_assert_int(get_state_of__tcp_socket(&socket), ==, TCP_Socket_State__Connected);
    return MUNIT_OK;
}

///
/// @spec    docs/specs/core/multiplayer/tcp_socket.h.spec.md
/// @section 1.4.5 Queries (static inline)
/// @section 1.3.2 TCP_Socket_State
/// @brief   set_state_of__tcp_socket sets state to Connecting,
///          get_state_of__tcp_socket returns Connecting.
///
TEST_FUNCTION(set_state_of__tcp_socket__connecting) {
    TCP_Socket socket;
    IPv4_Address addr;
    populate_ipv4_address(&addr, "127.0.0.1", "8080");
    initialize_tcp_socket(&socket, addr, 42);
    set_state_of__tcp_socket(&socket, TCP_Socket_State__Connecting);
    munit_assert_int(get_state_of__tcp_socket(&socket), ==, TCP_Socket_State__Connecting);
    return MUNIT_OK;
}

///
/// @spec    docs/specs/core/multiplayer/tcp_socket.h.spec.md
/// @section 1.4.5 Queries (static inline)
/// @section 1.3.2 TCP_Socket_State
/// @brief   set_state_of__tcp_socket sets state to Authenticated,
///          get_state_of__tcp_socket returns Authenticated.
///
TEST_FUNCTION(set_state_of__tcp_socket__authenticated) {
    TCP_Socket socket;
    IPv4_Address addr;
    populate_ipv4_address(&addr, "127.0.0.1", "8080");
    initialize_tcp_socket(&socket, addr, 42);
    set_state_of__tcp_socket(&socket, TCP_Socket_State__Authenticated);
    munit_assert_int(get_state_of__tcp_socket(&socket), ==, TCP_Socket_State__Authenticated);
    return MUNIT_OK;
}

///
/// @spec    docs/specs/core/multiplayer/tcp_socket.h.spec.md
/// @section 1.4.5 Queries (static inline)
/// @section 1.3.2 TCP_Socket_State
/// @brief   set_state_of__tcp_socket sets state to Disconnected,
///          get_state_of__tcp_socket returns Disconnected.
///
TEST_FUNCTION(set_state_of__tcp_socket__disconnected) {
    TCP_Socket socket;
    IPv4_Address addr;
    populate_ipv4_address(&addr, "127.0.0.1", "8080");
    initialize_tcp_socket(&socket, addr, 42);
    set_state_of__tcp_socket(&socket, TCP_Socket_State__Disconnected);
    munit_assert_int(get_state_of__tcp_socket(&socket), ==, TCP_Socket_State__Disconnected);
    return MUNIT_OK;
}

///
/// @spec    docs/specs/core/multiplayer/tcp_socket.h.spec.md
/// @section 1.4.5 Queries (static inline)
/// @section 1.3.4 TCP_Socket_Flags__u8
/// @brief   After initialization, is_tcp_socket__manually_driven
///          returns false by default.
///
TEST_FUNCTION(is_tcp_socket__manually_driven__default_is_false) {
    TCP_Socket socket;
    IPv4_Address addr;
    populate_ipv4_address(&addr, "127.0.0.1", "8080");
    initialize_tcp_socket(&socket, addr, 42);
    munit_assert_false(is_tcp_socket__manually_driven(&socket));
    return MUNIT_OK;
}

///
/// @spec    docs/specs/core/multiplayer/tcp_socket.h.spec.md
/// @section 1.4.5 Queries (static inline)
/// @section 1.5.3 Manually Driven Sockets
/// @brief   set_tcp_socket_as__manually_driven sets the
///          TCP_SOCKET_FLAG__IS_MANUALLY_DRIVEN flag.
///
TEST_FUNCTION(set_tcp_socket_as__manually_driven__sets_flag) {
    TCP_Socket socket;
    IPv4_Address addr;
    populate_ipv4_address(&addr, "127.0.0.1", "8080");
    initialize_tcp_socket(&socket, addr, 42);
    set_tcp_socket_as__manually_driven(&socket);
    munit_assert_true(is_tcp_socket__manually_driven(&socket));
    return MUNIT_OK;
}

///
/// @spec    docs/specs/core/multiplayer/tcp_socket.h.spec.md
/// @section 1.4.5 Queries (static inline)
/// @section 1.5.3 Manually Driven Sockets
/// @brief   set_tcp_socket_as__automatically_driven clears the
///          TCP_SOCKET_FLAG__IS_MANUALLY_DRIVEN flag.
///
TEST_FUNCTION(set_tcp_socket_as__automatically_driven__clears_flag) {
    TCP_Socket socket;
    IPv4_Address addr;
    populate_ipv4_address(&addr, "127.0.0.1", "8080");
    initialize_tcp_socket(&socket, addr, 42);
    set_tcp_socket_as__manually_driven(&socket);
    set_tcp_socket_as__automatically_driven(&socket);
    munit_assert_false(is_tcp_socket__manually_driven(&socket));
    return MUNIT_OK;
}

///
/// @spec    docs/specs/core/multiplayer/tcp_socket.h.spec.md
/// @section 1.4.3 Data Transfer
/// @section 1.5.6 Error Handling
/// @brief   get_latest__delivery_from__tcp_socket returns false
///          when the queue is empty.
///
TEST_FUNCTION(get_latest__delivery_from__tcp_socket__empty_queue__returns_false) {
    TCP_Socket socket;
    IPv4_Address addr;
    populate_ipv4_address(&addr, "127.0.0.1", "8080");
    initialize_tcp_socket(&socket, addr, 42);
    TCP_Packet packet;
    bool result = get_latest__delivery_from__tcp_socket(&socket, &packet);
    munit_assert_false(result);
    return MUNIT_OK;
}

///
/// @spec    docs/specs/core/multiplayer/tcp_socket.h.spec.md
/// @section 1.4.4 Binding
/// @section 1.5.5 Postconditions
/// @brief   After bind_tcp_socket, p_PLATFORM_tcp_socket is non-null.
///          Skipped: requires platform-specific PLATFORM_TCP_Socket.
///
TEST_FUNCTION(bind_tcp_socket__sets_platform_socket) {
    // This test needs to be done per backend - not on core, since we lack PLATFORM defs.
    // 
    // TCP_Socket socket;
    // IPv4_Address addr;
    // populate_ipv4_address(&addr, "127.0.0.1", "8080");
    // initialize_tcp_socket(&socket, addr, 42);
    // PLATFORM_TCP_Socket platform_socket;
    // bind_tcp_socket(&socket, &platform_socket);
    // munit_assert_ptr_equal(
    //     get_p_PLATFORM_tcp_socket_from__tcp_socket(&socket),
    //     &platform_socket);
    return MUNIT_SKIP;
}

///
/// @spec    docs/specs/core/multiplayer/tcp_socket.h.spec.md
/// @section 1.4.1 Initialization
/// @section 1.5.5 Postconditions
/// @brief   After initialize_tcp_socket, enqueue index is zero.
///
TEST_FUNCTION(initialize_tcp_socket__enqueue_index_is_zero) {
    TCP_Socket socket;
    IPv4_Address addr;
    populate_ipv4_address(&addr, "127.0.0.1", "8080");
    initialize_tcp_socket(&socket, addr, 42);
    munit_assert_uint32(socket.index_of__enqueue_begin, ==, 0);
    return MUNIT_OK;
}

DEFINE_SUITE(tcp_socket,
    INCLUDE_TEST__STATELESS(initialize_tcp_socket__sets_state_to_none),
    INCLUDE_TEST__STATELESS(initialize_tcp_socket__sets_uuid),
    INCLUDE_TEST__STATELESS(initialize_tcp_socket__packet_queue_is_empty),
    INCLUDE_TEST__STATELESS(initialize_tcp_socket__platform_socket_is_null),
    INCLUDE_TEST__STATELESS(initialize_tcp_socket__flags_are_zero),
    INCLUDE_TEST__STATELESS(initialize_tcp_socket_as__deallocated__clears_socket),
    INCLUDE_TEST__STATELESS(set_state_of__tcp_socket__updates_state),
    INCLUDE_TEST__STATELESS(set_state_of__tcp_socket__connecting),
    INCLUDE_TEST__STATELESS(set_state_of__tcp_socket__authenticated),
    INCLUDE_TEST__STATELESS(set_state_of__tcp_socket__disconnected),
    INCLUDE_TEST__STATELESS(is_tcp_socket__manually_driven__default_is_false),
    INCLUDE_TEST__STATELESS(set_tcp_socket_as__manually_driven__sets_flag),
    INCLUDE_TEST__STATELESS(set_tcp_socket_as__automatically_driven__clears_flag),
    INCLUDE_TEST__STATELESS(get_latest__delivery_from__tcp_socket__empty_queue__returns_false),
    INCLUDE_TEST__STATELESS(bind_tcp_socket__sets_platform_socket),
    INCLUDE_TEST__STATELESS(initialize_tcp_socket__enqueue_index_is_zero),
    END_TESTS)
