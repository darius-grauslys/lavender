#include <serialization/test_suite_serialization_serialization_request.h>

#include <serialization/serialization_request.c>

///
/// Spec: core/serialization/serialization_request.h.spec.md
/// Section: 1.4.1 Initialization
///
TEST_FUNCTION(serialization_request__initialize_zeroes_all_fields) {
    Serialization_Request request;
    request.p_data = (void*)0xDEADBEEF;
    request.serialization_request_flags = 0xFF;
    initialize_serialization_request(&request);
    munit_assert_ptr_null(request.p_data);
    munit_assert_ptr_null(request.p_serialization_header);
    munit_assert_uint8(request.serialization_request_flags, ==, 0);
    return MUNIT_OK;
}

///
/// Spec: core/serialization/serialization_request.h.spec.md
/// Section: 1.4.3 Flag Setters, 1.4.4 Flag Getters
/// Flag: SERIALZIATION_REQUEST_FLAG__IS_ALLOCATED
///
TEST_FUNCTION(serialization_request__set_allocated_flag) {
    Serialization_Request request;
    initialize_serialization_request(&request);
    munit_assert_false(is_serialization_request__allocated(&request));
    set_serialization_request_as__allocated(&request);
    munit_assert_true(is_serialization_request__allocated(&request));
    set_serialization_request_as__deallocated(&request);
    munit_assert_false(is_serialization_request__allocated(&request));
    return MUNIT_OK;
}

///
/// Spec: core/serialization/serialization_request.h.spec.md
/// Section: 1.4.3 Flag Setters, 1.4.4 Flag Getters
/// Flag: SERIALZIATION_REQUEST_FLAG__IS_ACTIVE
///
TEST_FUNCTION(serialization_request__set_active_flag) {
    Serialization_Request request;
    initialize_serialization_request(&request);
    munit_assert_false(is_serialization_request__active(&request));
    set_serialization_request_as__active(&request);
    munit_assert_true(is_serialization_request__active(&request));
    set_serialization_request_as__inactive(&request);
    munit_assert_false(is_serialization_request__active(&request));
    return MUNIT_OK;
}

///
/// Spec: core/serialization/serialization_request.h.spec.md
/// Section: 1.4.3 Flag Setters, 1.4.4 Flag Getters
/// Flag: SERIALIZATION_REQUEST_FLAG__READ_OR_WRITE
///
TEST_FUNCTION(serialization_request__set_read_write_flag) {
    Serialization_Request request;
    initialize_serialization_request(&request);
    munit_assert_true(is_serialization_request__writing(&request));
    munit_assert_false(is_serialization_request__reading(&request));
    set_serialization_request_as__read(&request);
    munit_assert_true(is_serialization_request__reading(&request));
    munit_assert_false(is_serialization_request__writing(&request));
    set_serialization_request_as__write(&request);
    munit_assert_true(is_serialization_request__writing(&request));
    munit_assert_false(is_serialization_request__reading(&request));
    return MUNIT_OK;
}

///
/// Spec: core/serialization/serialization_request.h.spec.md
/// Section: 1.4.3 Flag Setters, 1.4.4 Flag Getters
/// Flag: SERIALIZATION_REQUEST_FLAG__KEEP_ALIVE
///
TEST_FUNCTION(serialization_request__set_keep_alive_flag) {
    Serialization_Request request;
    initialize_serialization_request(&request);
    munit_assert_true(is_serialization_request__fire_and_forget(&request));
    munit_assert_false(is_serialization_request__keep_alive(&request));
    set_serialization_request_as__keep_alive(&request);
    munit_assert_true(is_serialization_request__keep_alive(&request));
    munit_assert_false(is_serialization_request__fire_and_forget(&request));
    set_serialization_request_as__fire_and_forget(&request);
    munit_assert_true(is_serialization_request__fire_and_forget(&request));
    return MUNIT_OK;
}

///
/// Spec: core/serialization/serialization_request.h.spec.md
/// Section: 1.4.3 Flag Setters, 1.4.4 Flag Getters
/// Flag: SERIALIZATION_REQUEST_FLAG__IS_TCP_OR_IO
///
TEST_FUNCTION(serialization_request__set_tcp_io_flag) {
    Serialization_Request request;
    initialize_serialization_request(&request);
    munit_assert_false(is_serialization_request__tcp_or_io(&request));
    set_serialization_request_as__tcp(&request);
    munit_assert_true(is_serialization_request__tcp_or_io(&request));
    set_serialization_request_as__io(&request);
    munit_assert_false(is_serialization_request__tcp_or_io(&request));
    return MUNIT_OK;
}

///
/// Spec: core/serialization/serialization_request.h.spec.md
/// Section: 1.3.2 Serialization_Request_Flags
///
TEST_FUNCTION(serialization_request__flags_are_independent) {
    Serialization_Request request;
    initialize_serialization_request(&request);
    set_serialization_request_as__allocated(&request);
    set_serialization_request_as__read(&request);
    set_serialization_request_as__keep_alive(&request);
    munit_assert_true(is_serialization_request__allocated(&request));
    munit_assert_true(is_serialization_request__reading(&request));
    munit_assert_true(is_serialization_request__keep_alive(&request));
    munit_assert_false(is_serialization_request__active(&request));
    munit_assert_false(is_serialization_request__tcp_or_io(&request));
    return MUNIT_OK;
}

DEFINE_SUITE(serialization_request,
    INCLUDE_TEST__STATELESS(serialization_request__initialize_zeroes_all_fields),
    INCLUDE_TEST__STATELESS(serialization_request__set_allocated_flag),
    INCLUDE_TEST__STATELESS(serialization_request__set_active_flag),
    INCLUDE_TEST__STATELESS(serialization_request__set_read_write_flag),
    INCLUDE_TEST__STATELESS(serialization_request__set_keep_alive_flag),
    INCLUDE_TEST__STATELESS(serialization_request__set_tcp_io_flag),
    INCLUDE_TEST__STATELESS(serialization_request__flags_are_independent),
    END_TESTS)
