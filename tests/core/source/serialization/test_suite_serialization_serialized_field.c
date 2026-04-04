#include <serialization/test_suite_serialization_serialized_field.h>

#include <serialization/serialized_field.c>

TEST_FUNCTION(serialized_field__initialize_sets_data_and_uuid) {
    Serialization_Header target;
    initialize_serialization_header(&target, 42, sizeof(Serialization_Header));
    Serialized_Field field;
    initialize_serialized_field(&field, &target, 42);
    munit_assert_uint32(field.identifier_for__serialized_field, ==, 42);
    munit_assert_ptr_equal(field.p_serialized_field__data, &target);
    return MUNIT_OK;
}

TEST_FUNCTION(serialized_field__initialize_as_unassigned_clears_all) {
    Serialized_Field field;
    field.identifier_for__serialized_field = 99;
    field.p_serialized_field__data = (void*)0xDEADBEEF;
    initialize_serialized_field_as__unassigned(&field);
    munit_assert_uint32(
            field.identifier_for__serialized_field,
            ==,
            IDENTIFIER__UNKNOWN__u32);
    munit_assert_ptr_null(field.p_serialized_field__data);
    return MUNIT_OK;
}

TEST_FUNCTION(serialized_field__initialize_as_unlinked_sets_uuid_only) {
    Serialized_Field field;
    field.p_serialized_field__data = (void*)0xDEADBEEF;
    initialize_serialized_field_as__unlinked(&field, 77);
    munit_assert_uint32(field.identifier_for__serialized_field, ==, 77);
    munit_assert_ptr_null(field.p_serialized_field__data);
    return MUNIT_OK;
}

TEST_FUNCTION(serialized_field__is_linked_returns_false_when_unassigned) {
    Serialized_Field field;
    initialize_serialized_field_as__unassigned(&field);
    munit_assert_false(is_p_serialized_field__linked(&field));
    return MUNIT_OK;
}

TEST_FUNCTION(serialized_field__is_linked_returns_false_when_unlinked) {
    Serialized_Field field;
    initialize_serialized_field_as__unlinked(&field, 77);
    munit_assert_false(is_p_serialized_field__linked(&field));
    return MUNIT_OK;
}

TEST_FUNCTION(serialized_field__is_linked_returns_true_when_properly_linked) {
    Serialization_Header target;
    initialize_serialization_header(&target, 42, sizeof(Serialization_Header));
    Serialized_Field field;
    initialize_serialized_field(&field, &target, 42);
    munit_assert_true(is_p_serialized_field__linked(&field));
    return MUNIT_OK;
}

TEST_FUNCTION(serialized_field__link_against_contiguous_array_succeeds) {
    Serialization_Header headers[4];
    initialize_serialization_header__contiguous_array(
            headers, 4, sizeof(Serialization_Header));
    initialize_serialization_header(&headers[2], 55, sizeof(Serialization_Header));

    Serialized_Field field;
    initialize_serialized_field_as__unlinked(&field, 55);
    bool result = link_serialized_field_against__contiguous_array(
            &field,
            headers,
            4);
    munit_assert_true(result);
    munit_assert_ptr_equal(field.p_serialized_field__data, &headers[2]);
    munit_assert_true(is_p_serialized_field__linked(&field));
    return MUNIT_OK;
}

TEST_FUNCTION(serialized_field__link_against_contiguous_array_fails_when_not_found) {
    Serialization_Header headers[4];
    initialize_serialization_header__contiguous_array(
            headers, 4, sizeof(Serialization_Header));
    initialize_serialization_header(&headers[0], 10, sizeof(Serialization_Header));
    initialize_serialization_header(&headers[1], 20, sizeof(Serialization_Header));

    Serialized_Field field;
    initialize_serialized_field_as__unlinked(&field, 99);
    bool result = link_serialized_field_against__contiguous_array(
            &field,
            headers,
            4);
    munit_assert_false(result);
    munit_assert_false(is_p_serialized_field__linked(&field));
    return MUNIT_OK;
}

TEST_FUNCTION(serialized_field__matching_header_returns_true_on_match) {
    Serialization_Header target;
    initialize_serialization_header(&target, 42, sizeof(Serialization_Header));
    Serialized_Field field;
    initialize_serialized_field(&field, &target, 42);
    munit_assert_true(
            is_serialized_field_matching__serialization_header(&field, &target));
    return MUNIT_OK;
}

TEST_FUNCTION(serialized_field__matching_header_returns_false_on_mismatch) {
    Serialization_Header target;
    initialize_serialization_header(&target, 42, sizeof(Serialization_Header));
    Serialization_Header other;
    initialize_serialization_header(&other, 99, sizeof(Serialization_Header));
    Serialized_Field field;
    initialize_serialized_field(&field, &target, 42);
    munit_assert_false(
            is_serialized_field_matching__serialization_header(&field, &other));
    return MUNIT_OK;
}

DEFINE_SUITE(serialized_field,
    INCLUDE_TEST__STATELESS(serialized_field__initialize_sets_data_and_uuid),
    INCLUDE_TEST__STATELESS(serialized_field__initialize_as_unassigned_clears_all),
    INCLUDE_TEST__STATELESS(serialized_field__initialize_as_unlinked_sets_uuid_only),
    INCLUDE_TEST__STATELESS(serialized_field__is_linked_returns_false_when_unassigned),
    INCLUDE_TEST__STATELESS(serialized_field__is_linked_returns_false_when_unlinked),
    INCLUDE_TEST__STATELESS(serialized_field__is_linked_returns_true_when_properly_linked),
    INCLUDE_TEST__STATELESS(serialized_field__link_against_contiguous_array_succeeds),
    INCLUDE_TEST__STATELESS(serialized_field__link_against_contiguous_array_fails_when_not_found),
    INCLUDE_TEST__STATELESS(serialized_field__matching_header_returns_true_on_match),
    INCLUDE_TEST__STATELESS(serialized_field__matching_header_returns_false_on_mismatch),
    END_TESTS)
