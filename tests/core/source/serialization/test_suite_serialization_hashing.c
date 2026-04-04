#include <serialization/test_suite_serialization_hashing.h>

#include <serialization/hashing.c>

TEST_FUNCTION(hashing__bound_uuid_computes_modulo) {
    Identifier__u32 result = bound_uuid_to__contiguous_array(100, 8);
    munit_assert_uint32(result, ==, 100 % 8);
    return MUNIT_OK;
}

TEST_FUNCTION(hashing__bound_uuid_zero_returns_zero) {
    Identifier__u32 result = bound_uuid_to__contiguous_array(0, 8);
    munit_assert_uint32(result, ==, 0);
    return MUNIT_OK;
}

TEST_FUNCTION(hashing__dehash_finds_allocated_element) {
    Serialization_Header headers[8];
    initialize_serialization_header__contiguous_array(
            headers, 8, sizeof(Serialization_Header));
    Identifier__u32 uuid = 42;
    Index__u32 index = uuid % 8;
    initialize_serialization_header(
            &headers[index], uuid, sizeof(Serialization_Header));
    Serialization_Header *p_found =
        dehash_identitier_u32_in__contigious_array(headers, 8, uuid);
    munit_assert_not_null(p_found);
    munit_assert_uint32(p_found->uuid, ==, uuid);
    return MUNIT_OK;
}

TEST_FUNCTION(hashing__dehash_returns_null_for_missing_uuid) {
    Serialization_Header headers[8];
    initialize_serialization_header__contiguous_array(
            headers, 8, sizeof(Serialization_Header));
    Serialization_Header *p_found =
        dehash_identitier_u32_in__contigious_array(headers, 8, 42);
    munit_assert_null(p_found);
    return MUNIT_OK;
}

TEST_FUNCTION(hashing__allocate_with_uuid_sets_uuid) {
    Serialization_Header headers[8];
    initialize_serialization_header__contiguous_array(
            headers, 8, sizeof(Serialization_Header));
    Identifier__u32 uuid = 55;
    Serialization_Header *p_allocated =
        allocate_serialization_header_with__this_uuid(headers, 8, uuid);
    munit_assert_not_null(p_allocated);
    munit_assert_uint32(p_allocated->uuid, ==, uuid);
    munit_assert_false(is_serialized_struct__deallocated(p_allocated));
    return MUNIT_OK;
}

TEST_FUNCTION(hashing__allocate_with_uuid_can_be_dehashed) {
    Serialization_Header headers[8];
    initialize_serialization_header__contiguous_array(
            headers, 8, sizeof(Serialization_Header));
    Identifier__u32 uuid = 77;
    Serialization_Header *p_allocated =
        allocate_serialization_header_with__this_uuid(headers, 8, uuid);
    munit_assert_not_null(p_allocated);
    Serialization_Header *p_found =
        dehash_identitier_u32_in__contigious_array(headers, 8, uuid);
    munit_assert_not_null(p_found);
    munit_assert_ptr_equal(p_allocated, p_found);
    return MUNIT_OK;
}

TEST_FUNCTION(hashing__has_uuid_returns_true_when_present) {
    Serialization_Header headers[8];
    initialize_serialization_header__contiguous_array(
            headers, 8, sizeof(Serialization_Header));
    Identifier__u32 uuid = 33;
    allocate_serialization_header_with__this_uuid(headers, 8, uuid);
    munit_assert_true(has_uuid_in__contiguous_array(headers, 8, uuid));
    return MUNIT_OK;
}

TEST_FUNCTION(hashing__has_uuid_returns_false_when_absent) {
    Serialization_Header headers[8];
    initialize_serialization_header__contiguous_array(
            headers, 8, sizeof(Serialization_Header));
    munit_assert_false(has_uuid_in__contiguous_array(headers, 8, 33));
    return MUNIT_OK;
}

TEST_FUNCTION(hashing__collision_resolution_handles_occupied_slot) {
    Serialization_Header headers[8];
    initialize_serialization_header__contiguous_array(
            headers, 8, sizeof(Serialization_Header));
    Identifier__u32 uuid_a = 3;
    Identifier__u32 uuid_b = 3 + 8;
    allocate_serialization_header_with__this_uuid(headers, 8, uuid_a);
    allocate_serialization_header_with__this_uuid(headers, 8, uuid_b);
    munit_assert_true(has_uuid_in__contiguous_array(headers, 8, uuid_a));
    munit_assert_true(has_uuid_in__contiguous_array(headers, 8, uuid_b));
    Serialization_Header *p_a =
        dehash_identitier_u32_in__contigious_array(headers, 8, uuid_a);
    Serialization_Header *p_b =
        dehash_identitier_u32_in__contigious_array(headers, 8, uuid_b);
    munit_assert_not_null(p_a);
    munit_assert_not_null(p_b);
    munit_assert_ptr_not_equal(p_a, p_b);
    munit_assert_uint32(p_a->uuid, ==, uuid_a);
    munit_assert_uint32(p_b->uuid, ==, uuid_b);
    return MUNIT_OK;
}

TEST_FUNCTION(hashing__allocation_returns_null_when_full) {
    Serialization_Header headers[4];
    initialize_serialization_header__contiguous_array(
            headers, 4, sizeof(Serialization_Header));
    for (Identifier__u32 i = 1; i <= 4; i++) {
        Serialization_Header *p =
            allocate_serialization_header_with__this_uuid(headers, 4, i);
        munit_assert_not_null(p);
    }
    Serialization_Header *p_overflow =
        allocate_serialization_header_with__this_uuid(headers, 4, 99);
    munit_assert_null(p_overflow);
    return MUNIT_OK;
}

TEST_FUNCTION(hashing__get_next_available_allocation_finds_free_slot) {
    Serialization_Header headers[8];
    initialize_serialization_header__contiguous_array(
            headers, 8, sizeof(Serialization_Header));
    Identifier__u32 uuid = 42;
    Serialization_Header *p_slot =
        get_next_available__allocation_in__contiguous_array(headers, 8, uuid);
    munit_assert_not_null(p_slot);
    munit_assert_true(is_serialized_struct__deallocated(p_slot));
    return MUNIT_OK;
}

TEST_FUNCTION(hashing__multiple_allocations_all_dehashable) {
    Serialization_Header headers[16];
    initialize_serialization_header__contiguous_array(
            headers, 16, sizeof(Serialization_Header));
    Identifier__u32 uuids[] = {5, 21, 37, 100, 200, 7, 23};
    Quantity__u32 count = sizeof(uuids) / sizeof(uuids[0]);
    for (Quantity__u32 i = 0; i < count; i++) {
        Serialization_Header *p =
            allocate_serialization_header_with__this_uuid(
                    headers, 16, uuids[i]);
        munit_assert_not_null(p);
    }
    for (Quantity__u32 i = 0; i < count; i++) {
        Serialization_Header *p =
            dehash_identitier_u32_in__contigious_array(
                    headers, 16, uuids[i]);
        munit_assert_not_null(p);
        munit_assert_uint32(p->uuid, ==, uuids[i]);
    }
    return MUNIT_OK;
}

DEFINE_SUITE(hashing,
    INCLUDE_TEST__STATELESS(hashing__bound_uuid_computes_modulo),
    INCLUDE_TEST__STATELESS(hashing__bound_uuid_zero_returns_zero),
    INCLUDE_TEST__STATELESS(hashing__dehash_finds_allocated_element),
    INCLUDE_TEST__STATELESS(hashing__dehash_returns_null_for_missing_uuid),
    INCLUDE_TEST__STATELESS(hashing__allocate_with_uuid_sets_uuid),
    INCLUDE_TEST__STATELESS(hashing__allocate_with_uuid_can_be_dehashed),
    INCLUDE_TEST__STATELESS(hashing__has_uuid_returns_true_when_present),
    INCLUDE_TEST__STATELESS(hashing__has_uuid_returns_false_when_absent),
    INCLUDE_TEST__STATELESS(hashing__collision_resolution_handles_occupied_slot),
    INCLUDE_TEST__STATELESS(hashing__allocation_returns_null_when_full),
    INCLUDE_TEST__STATELESS(hashing__get_next_available_allocation_finds_free_slot),
    INCLUDE_TEST__STATELESS(hashing__multiple_allocations_all_dehashable),
    END_TESTS)
