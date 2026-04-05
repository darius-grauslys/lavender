#include <multiplayer/test_suite_multiplayer_tcp_socket_manager.h>

#include <multiplayer/tcp_socket_manager.c>

static void dummy_poll_callback(
        TCP_Socket_Manager *p_tcp_socket_manager,
        Game *p_game) {
    (void)p_tcp_socket_manager;
    (void)p_game;
}

TEST_FUNCTION(initialize_tcp_socket_manager__quantity_of_connections_is_zero) {
    TCP_Socket_Manager manager;
    initialize_tcp_socket_manager(&manager, dummy_poll_callback);
    munit_assert_uint32(
        get_quantity_of__active_tcp_sockets(&manager), ==, 0);
    return MUNIT_OK;
}

TEST_FUNCTION(initialize_tcp_socket_manager__sets_poll_callback) {
    TCP_Socket_Manager manager;
    initialize_tcp_socket_manager(&manager, dummy_poll_callback);
    munit_assert_ptr_equal(
        (void *)manager.m_poll_tcp_socket_manager,
        (void *)dummy_poll_callback);
    return MUNIT_OK;
}

TEST_FUNCTION(initialize_tcp_socket_manager__all_sockets_are_deallocated) {
    TCP_Socket_Manager manager;
    initialize_tcp_socket_manager(&manager, dummy_poll_callback);
    for (Quantity__u32 i = 0; i < MAX_QUANTITY_OF__TCP_SOCKETS; i++) {
        munit_assert_true(
            is_serialized_struct__deallocated(
                &manager.tcp_sockets[i]._serialization_header));
    }
    return MUNIT_OK;
}

TEST_FUNCTION(initialize_tcp_socket_manager__pending_connection_is_null) {
    TCP_Socket_Manager manager;
    initialize_tcp_socket_manager(&manager, dummy_poll_callback);
    munit_assert_ptr_null(manager.p_PLATFORM_tcp_socket__pending_connection);
    return MUNIT_OK;
}

TEST_FUNCTION(get_p_tcp_socket_for__this_uuid__unknown_uuid__returns_null) {
    TCP_Socket_Manager manager;
    initialize_tcp_socket_manager(&manager, dummy_poll_callback);
    TCP_Socket *p_socket =
        get_p_tcp_socket_for__this_uuid(&manager, 12345);
    munit_assert_ptr_null(p_socket);
    return MUNIT_OK;
}

TEST_FUNCTION(get_quantity_of__active_tcp_sockets__after_init__returns_zero) {
    TCP_Socket_Manager manager;
    initialize_tcp_socket_manager(&manager, dummy_poll_callback);
    Quantity__u32 count = get_quantity_of__active_tcp_sockets(&manager);
    munit_assert_uint32(count, ==, 0);
    return MUNIT_OK;
}

TEST_FUNCTION(initialize_tcp_socket_manager__null_callback__sets_null) {
    TCP_Socket_Manager manager;
    initialize_tcp_socket_manager(&manager, (m_Poll_TCP_Socket_Manager)0);
    munit_assert_ptr_null((void *)manager.m_poll_tcp_socket_manager);
    return MUNIT_OK;
}

DEFINE_SUITE(tcp_socket_manager,
    INCLUDE_TEST__STATELESS(initialize_tcp_socket_manager__quantity_of_connections_is_zero),
    INCLUDE_TEST__STATELESS(initialize_tcp_socket_manager__sets_poll_callback),
    INCLUDE_TEST__STATELESS(initialize_tcp_socket_manager__all_sockets_are_deallocated),
    INCLUDE_TEST__STATELESS(initialize_tcp_socket_manager__pending_connection_is_null),
    INCLUDE_TEST__STATELESS(get_p_tcp_socket_for__this_uuid__unknown_uuid__returns_null),
    INCLUDE_TEST__STATELESS(get_quantity_of__active_tcp_sockets__after_init__returns_zero),
    INCLUDE_TEST__STATELESS(initialize_tcp_socket_manager__null_callback__sets_null),
    END_TESTS)
