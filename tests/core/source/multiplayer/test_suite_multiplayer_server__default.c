#include <multiplayer/test_suite_multiplayer_server__default.h>

#include <multiplayer/server__default.c>

TEST_FUNCTION(m_poll_tcp_socket_manager_as__server__default__symbol_exists) {
    m_Poll_TCP_Socket_Manager callback =
        (m_Poll_TCP_Socket_Manager)m_poll_tcp_socket_manager_as__server__default;
    munit_assert_ptr_not_null((void *)callback);
    return MUNIT_OK;
}

DEFINE_SUITE(server__default,
    INCLUDE_TEST__STATELESS(m_poll_tcp_socket_manager_as__server__default__symbol_exists),
    END_TESTS)
