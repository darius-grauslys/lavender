#include <multiplayer/test_suite_multiplayer_client__default.h>

#include <multiplayer/client__default.c>

///
/// Spec:    docs/specs/core/multiplayer/client__default.h.spec.md
/// Section: 1.3.1 Polling
///
TEST_FUNCTION(m_poll_tcp_socket_manager_as__client__default__symbol_exists) {
    m_Poll_TCP_Socket_Manager callback =
        (m_Poll_TCP_Socket_Manager)m_poll_tcp_socket_manager_as__client__default;
    munit_assert_ptr_not_null((void *)callback);
    return MUNIT_OK;
}

DEFINE_SUITE(client__default,
    INCLUDE_TEST__STATELESS(m_poll_tcp_socket_manager_as__client__default__symbol_exists),
    END_TESTS)
