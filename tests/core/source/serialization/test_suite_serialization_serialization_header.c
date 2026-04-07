#include <serialization/test_suite_serialization_serialization_header.h>

#include <serialization/serialization_header.c>

///
/// Spec: docs/specs/core/serialization/serialization_header.h.spec.md
/// Section: 1.4.1 Initialization — initialize_serialization_header
///
TEST_FUNCTION(serialization_header__initialize_sets_uuid_and_size) {
    Serialization_Header header;
    initialize_serialization_header(
            &header,
            42,
            sizeof(Serialization_Header));
    munit_assert_uint32(header.uuid, ==, 42);
    munit_assert_uint32(header.size_of__struct, ==, sizeof(Serialization_Header));
    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/serialization/serialization_header.h.spec.md
/// Section: 1.4.1 Initialization — initialize_serialization_header_for__deallocated_struct
///
TEST_FUNCTION(serialization_header__initialize_deallocated_sets_unknown_uuid) {
    Serialization_Header header;
    header.uuid = 123;
    initialize_serialization_header_for__deallocated_struct(
            &header,
            sizeof(Serialization_Header));
    munit_assert_uint32(header.uuid, ==, IDENTIFIER__UNKNOWN__u32);
    munit_assert_uint32(header.size_of__struct, ==, sizeof(Serialization_Header));
    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/serialization/serialization_header.h.spec.md
/// Section: 1.4.4 Identity Checks — is_serialized_struct__deallocated
///
TEST_FUNCTION(serialization_header__is_deallocated_returns_true_for_unknown_uuid) {
    Serialization_Header header;
    initialize_serialization_header_for__deallocated_struct(
            &header,
            sizeof(Serialization_Header));
    munit_assert_true(is_serialized_struct__deallocated(&header));
    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/serialization/serialization_header.h.spec.md
/// Section: 1.4.4 Identity Checks — is_serialized_struct__deallocated
///
TEST_FUNCTION(serialization_header__is_deallocated_returns_false_for_valid_uuid) {
    Serialization_Header header;
    initialize_serialization_header(
            &header,
            42,
            sizeof(Serialization_Header));
    munit_assert_false(is_serialized_struct__deallocated(&header));
    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/serialization/serialization_header.h.spec.md
/// Section: 1.4.4 Identity Checks — is_serialized_struct__deallocated
///
TEST_FUNCTION(serialization_header__is_deallocated_returns_true_for_null) {
    munit_assert_true(is_serialized_struct__deallocated(0));
    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/serialization/serialization_header.h.spec.md
/// Section: 1.4.4 Identity Checks — is_identifier_u32_matching__serialization_header
///
TEST_FUNCTION(serialization_header__identifier_matching_returns_true_on_match) {
    Serialization_Header header;
    initialize_serialization_header(
            &header,
            99,
            sizeof(Serialization_Header));
    munit_assert_true(
            is_identifier_u32_matching__serialization_header(99, &header));
    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/serialization/serialization_header.h.spec.md
/// Section: 1.4.4 Identity Checks — is_identifier_u32_matching__serialization_header
///
TEST_FUNCTION(serialization_header__identifier_matching_returns_false_on_mismatch) {
    Serialization_Header header;
    initialize_serialization_header(
            &header,
            99,
            sizeof(Serialization_Header));
    munit_assert_false(
            is_identifier_u32_matching__serialization_header(100, &header));
    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/serialization/serialization_header.h.spec.md
/// Section: 1.4.2 Contiguous Array Initialization — initialize_serialization_header__contiguous_array
///
TEST_FUNCTION(serialization_header__contiguous_array_init_marks_all_deallocated) {
    Serialization_Header headers[8];
    initialize_serialization_header__contiguous_array(
            headers,
            8,
            sizeof(Serialization_Header));
    for (Index__u32 i = 0; i < 8; i++) {
        Serialization_Header *p_header =
            get_p_serialization_header_from__contigious_array(
                    headers, 8, i);
        munit_assert_not_null(p_header);
        munit_assert_true(is_serialized_struct__deallocated(p_header));
        munit_assert_uint32(
                p_header->size_of__struct, ==, sizeof(Serialization_Header));
    }
    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/serialization/serialization_header.h.spec.md
/// Section: 1.4.3 Contiguous Array Access — get_p_serialization_header_from__contigious_array
///
TEST_FUNCTION(serialization_header__contiguous_array_access_returns_correct_element) {
    Serialization_Header headers[4];
    initialize_serialization_header__contiguous_array(
            headers,
            4,
            sizeof(Serialization_Header));
    Serialization_Header *p_first =
        get_p_serialization_header_from__contigious_array(headers, 4, 0);
    Serialization_Header *p_second =
        get_p_serialization_header_from__contigious_array(headers, 4, 1);
    munit_assert_ptr_equal(p_first, &headers[0]);
    munit_assert_ptr_equal(p_second, &headers[1]);
    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/serialization/serialization_header.h.spec.md
/// Section: 1.4.3 Contiguous Array Access — get_next_available_p_serialization_header
///
TEST_FUNCTION(serialization_header__get_next_available_finds_first_free) {
    Serialization_Header headers[4];
    initialize_serialization_header__contiguous_array(
            headers,
            4,
            sizeof(Serialization_Header));
    initialize_serialization_header(&headers[0], 10, sizeof(Serialization_Header));
    initialize_serialization_header(&headers[1], 20, sizeof(Serialization_Header));
    Serialization_Header *p_available =
        get_next_available_p_serialization_header(headers, 4);
    munit_assert_not_null(p_available);
    munit_assert_ptr_equal(p_available, &headers[2]);
    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/serialization/serialization_header.h.spec.md
/// Section: 1.4.3 Contiguous Array Access — get_next_available_p_serialization_header
///
TEST_FUNCTION(serialization_header__get_next_available_returns_null_when_full) {
    Serialization_Header headers[2];
    initialize_serialization_header__contiguous_array(
            headers,
            2,
            sizeof(Serialization_Header));
    initialize_serialization_header(&headers[0], 10, sizeof(Serialization_Header));
    initialize_serialization_header(&headers[1], 20, sizeof(Serialization_Header));
    Serialization_Header *p_available =
        get_next_available_p_serialization_header(headers, 2);
    munit_assert_null(p_available);
    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/serialization/serialization_header.h.spec.md
/// Section: 1.3.4 Convenience Macros — ALLOCATE_P
///
TEST_FUNCTION(serialization_header__allocate_p_sets_uuid) {
    Serialization_Header header;
    initialize_serialization_header_for__deallocated_struct(
            &header,
            sizeof(Serialization_Header));
    munit_assert_true(is_serialized_struct__deallocated(&header));
    ALLOCATE_P(&header, 55);
    munit_assert_uint32(header.uuid, ==, 55);
    munit_assert_false(is_serialized_struct__deallocated(&header));
    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/serialization/serialization_header.h.spec.md
/// Section: 1.3.4 Convenience Macros — DEALLOCATE_P
///
TEST_FUNCTION(serialization_header__deallocate_p_sets_unknown) {
    Serialization_Header header;
    initialize_serialization_header(
            &header,
            55,
            sizeof(Serialization_Header));
    DEALLOCATE_P(&header);
    munit_assert_true(is_serialized_struct__deallocated(&header));
    munit_assert_uint32(
            header.size_of__struct, ==, sizeof(Serialization_Header));
    return MUNIT_OK;
}

DEFINE_SUITE(serialization_header,
    INCLUDE_TEST__STATELESS(serialization_header__initialize_sets_uuid_and_size),
    INCLUDE_TEST__STATELESS(serialization_header__initialize_deallocated_sets_unknown_uuid),
    INCLUDE_TEST__STATELESS(serialization_header__is_deallocated_returns_true_for_unknown_uuid),
    INCLUDE_TEST__STATELESS(serialization_header__is_deallocated_returns_false_for_valid_uuid),
    INCLUDE_TEST__STATELESS(serialization_header__is_deallocated_returns_true_for_null),
    INCLUDE_TEST__STATELESS(serialization_header__identifier_matching_returns_true_on_match),
    INCLUDE_TEST__STATELESS(serialization_header__identifier_matching_returns_false_on_mismatch),
    INCLUDE_TEST__STATELESS(serialization_header__contiguous_array_init_marks_all_deallocated),
    INCLUDE_TEST__STATELESS(serialization_header__contiguous_array_access_returns_correct_element),
    INCLUDE_TEST__STATELESS(serialization_header__get_next_available_finds_first_free),
    INCLUDE_TEST__STATELESS(serialization_header__get_next_available_returns_null_when_full),
    INCLUDE_TEST__STATELESS(serialization_header__allocate_p_sets_uuid),
    INCLUDE_TEST__STATELESS(serialization_header__deallocate_p_sets_unknown),
    END_TESTS)
