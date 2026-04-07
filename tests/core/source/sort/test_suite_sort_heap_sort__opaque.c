#include <sort/test_suite_sort_heap_sort__opaque.h>

#include <sort/heap_sort__opaque.c>

static Signed_Quantity__i32 test_opaque_heuristic__i32(
        void *p_context,
        void *p_one,
        void *p_two) {
    (void)p_context;
    int32_t a = *(int32_t*)p_one;
    int32_t b = *(int32_t*)p_two;
    return a - b;
}

static void test_opaque_swap__void(
        void *p_context,
        void *p_one,
        void *p_two) {
    (void)p_context;
    int32_t temp = *(int32_t*)p_one;
    *(int32_t*)p_one = *(int32_t*)p_two;
    *(int32_t*)p_two = temp;
}

///
/// Spec:    docs/specs/core/sort/heap_sort__opaque.h.spec.md
/// Section: 1.4.1 heap_sort__opaque
/// Section: 1.5.4 Postconditions
///
TEST_FUNCTION(heap_sort__opaque__sorts_ascending) {
    int32_t data[] = { 5, 3, 8, 1, 7, 2, 6, 4 };
    Quantity__u32 count = 8;

    heap_sort__opaque(
            NULL,
            data,
            sizeof(int32_t),
            count,
            test_opaque_heuristic__i32,
            test_opaque_swap__void);

    for (Quantity__u32 i = 0; i < count - 1; i++) {
        munit_assert_int32(data[i], <=, data[i + 1]);
    }

    return MUNIT_OK;
}

///
/// Spec:    docs/specs/core/sort/heap_sort__opaque.h.spec.md
/// Section: 1.5.3 Preconditions
///
TEST_FUNCTION(heap_sort__opaque__single_element) {
    int32_t data[] = { 42 };

    heap_sort__opaque(
            NULL,
            data,
            sizeof(int32_t),
            1,
            test_opaque_heuristic__i32,
            test_opaque_swap__void);

    munit_assert_int32(data[0], ==, 42);

    return MUNIT_OK;
}

///
/// Spec:    docs/specs/core/sort/heap_sort__opaque.h.spec.md
/// Section: 1.4.1 heap_sort__opaque
///
TEST_FUNCTION(heap_sort__opaque__two_elements_unsorted) {
    int32_t data[] = { 10, 5 };

    heap_sort__opaque(
            NULL,
            data,
            sizeof(int32_t),
            2,
            test_opaque_heuristic__i32,
            test_opaque_swap__void);

    munit_assert_int32(data[0], <=, data[1]);

    return MUNIT_OK;
}

///
/// Spec:    docs/specs/core/sort/heap_sort__opaque.h.spec.md
/// Section: 1.5.4 Postconditions
///
TEST_FUNCTION(heap_sort__opaque__two_elements_already_sorted) {
    int32_t data[] = { 5, 10 };

    heap_sort__opaque(
            NULL,
            data,
            sizeof(int32_t),
            2,
            test_opaque_heuristic__i32,
            test_opaque_swap__void);

    munit_assert_int32(data[0], ==, 5);
    munit_assert_int32(data[1], ==, 10);

    return MUNIT_OK;
}

///
/// Spec:    docs/specs/core/sort/heap_sort__opaque.h.spec.md
/// Section: 1.5.4 Postconditions
///
TEST_FUNCTION(heap_sort__opaque__already_sorted) {
    int32_t data[] = { 1, 2, 3, 4, 5, 6, 7, 8 };
    Quantity__u32 count = 8;

    heap_sort__opaque(
            NULL,
            data,
            sizeof(int32_t),
            count,
            test_opaque_heuristic__i32,
            test_opaque_swap__void);

    for (Quantity__u32 i = 0; i < count - 1; i++) {
        munit_assert_int32(data[i], <=, data[i + 1]);
    }

    return MUNIT_OK;
}

///
/// Spec:    docs/specs/core/sort/heap_sort__opaque.h.spec.md
/// Section: 1.5.5 Performance
///
TEST_FUNCTION(heap_sort__opaque__reverse_sorted) {
    int32_t data[] = { 8, 7, 6, 5, 4, 3, 2, 1 };
    Quantity__u32 count = 8;

    heap_sort__opaque(
            NULL,
            data,
            sizeof(int32_t),
            count,
            test_opaque_heuristic__i32,
            test_opaque_swap__void);

    for (Quantity__u32 i = 0; i < count - 1; i++) {
        munit_assert_int32(data[i], <=, data[i + 1]);
    }

    return MUNIT_OK;
}

///
/// Spec:    docs/specs/core/sort/heap_sort__opaque.h.spec.md
/// Section: 1.3.1 f_Sort_Heuristic__i32
/// Section: 1.5.4 Postconditions
///
TEST_FUNCTION(heap_sort__opaque__all_equal) {
    int32_t data[] = { 7, 7, 7, 7, 7 };
    Quantity__u32 count = 5;

    heap_sort__opaque(
            NULL,
            data,
            sizeof(int32_t),
            count,
            test_opaque_heuristic__i32,
            test_opaque_swap__void);

    for (Quantity__u32 i = 0; i < count; i++) {
        munit_assert_int32(data[i], ==, 7);
    }

    return MUNIT_OK;
}

///
/// Spec:    docs/specs/core/sort/heap_sort__opaque.h.spec.md
/// Section: 1.3.1 f_Sort_Heuristic__i32
///
TEST_FUNCTION(heap_sort__opaque__negative_values) {
    int32_t data[] = { -3, 5, -1, 0, -8, 2 };
    Quantity__u32 count = 6;

    heap_sort__opaque(
            NULL,
            data,
            sizeof(int32_t),
            count,
            test_opaque_heuristic__i32,
            test_opaque_swap__void);

    for (Quantity__u32 i = 0; i < count - 1; i++) {
        munit_assert_int32(data[i], <=, data[i + 1]);
    }

    return MUNIT_OK;
}

///
/// Spec:    docs/specs/core/sort/heap_sort__opaque.h.spec.md
/// Section: 1.3.1 f_Sort_Heuristic__i32
/// Section: 1.5.4 Postconditions
///
TEST_FUNCTION(heap_sort__opaque__duplicates) {
    int32_t data[] = { 3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5 };
    Quantity__u32 count = 11;

    heap_sort__opaque(
            NULL,
            data,
            sizeof(int32_t),
            count,
            test_opaque_heuristic__i32,
            test_opaque_swap__void);

    for (Quantity__u32 i = 0; i < count - 1; i++) {
        munit_assert_int32(data[i], <=, data[i + 1]);
    }

    return MUNIT_OK;
}

///
/// Spec:    docs/specs/core/sort/heap_sort__opaque.h.spec.md
/// Section: 1.4.1 heap_sort__opaque
///
TEST_FUNCTION(heap_sort__opaque__context_passed_through) {
    int32_t data[] = { 2, 1 };
    int context_value = 999;

    heap_sort__opaque(
            &context_value,
            data,
            sizeof(int32_t),
            2,
            test_opaque_heuristic__i32,
            test_opaque_swap__void);

    munit_assert_int32(data[0], <=, data[1]);

    return MUNIT_OK;
}

///
/// Spec:    docs/specs/core/sort/heap_sort__opaque.h.spec.md
/// Section: 1.5.5 Performance
///
TEST_FUNCTION(heap_sort__opaque__large_array) {
    int32_t data[64];
    Quantity__u32 count = 64;

    for (Quantity__u32 i = 0; i < count; i++) {
        data[i] = (int32_t)(count - i);
    }

    heap_sort__opaque(
            NULL,
            data,
            sizeof(int32_t),
            count,
            test_opaque_heuristic__i32,
            test_opaque_swap__void);

    for (Quantity__u32 i = 0; i < count - 1; i++) {
        munit_assert_int32(data[i], <=, data[i + 1]);
    }

    return MUNIT_OK;
}

DEFINE_SUITE(heap_sort__opaque,
    INCLUDE_TEST__STATELESS(heap_sort__opaque__sorts_ascending),
    INCLUDE_TEST__STATELESS(heap_sort__opaque__single_element),
    INCLUDE_TEST__STATELESS(heap_sort__opaque__two_elements_unsorted),
    INCLUDE_TEST__STATELESS(heap_sort__opaque__two_elements_already_sorted),
    INCLUDE_TEST__STATELESS(heap_sort__opaque__already_sorted),
    INCLUDE_TEST__STATELESS(heap_sort__opaque__reverse_sorted),
    INCLUDE_TEST__STATELESS(heap_sort__opaque__all_equal),
    INCLUDE_TEST__STATELESS(heap_sort__opaque__negative_values),
    INCLUDE_TEST__STATELESS(heap_sort__opaque__duplicates),
    INCLUDE_TEST__STATELESS(heap_sort__opaque__context_passed_through),
    INCLUDE_TEST__STATELESS(heap_sort__opaque__large_array),
    END_TESTS)
