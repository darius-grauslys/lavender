#include <world/test_suite_world_global_space_manager.h>

#include <world/global_space_manager.c>

///
/// Spec: docs/specs/core/world/global_space_manager.h.spec.md
/// Section: 1.4.1 Initialization
///
TEST_FUNCTION(global_space_manager__initialize__all_deallocated) {
    Global_Space_Manager manager;
    initialize_global_space_manager(&manager);
    for (Index__u32 i = 0; i < QUANTITY_OF__GLOBAL_SPACE; i++) {
        munit_assert_false(is_global_space__allocated(&manager.global_spaces[i]));
    }
    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/world/global_space_manager.h.spec.md
/// Section: 1.4.2 Allocation and Release
///
TEST_FUNCTION(global_space_manager__allocate__returns_non_null) {
    Global_Space_Manager manager;
    initialize_global_space_manager(&manager);
    Chunk_Vector__3i32 cv;
    cv.x__i32 = 0;
    cv.y__i32 = 0;
    cv.z__i32 = 0;
    Global_Space *p_gs = allocate_global_space_in__global_space_manager(&manager, cv);
    munit_assert_ptr_not_null(p_gs);
    munit_assert_true(is_global_space__allocated(p_gs));
    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/world/global_space_manager.h.spec.md
/// Section: 1.4.3 Lookup
///
TEST_FUNCTION(global_space_manager__allocate__lookup_returns_same) {
    Global_Space_Manager manager;
    initialize_global_space_manager(&manager);
    Chunk_Vector__3i32 cv;
    cv.x__i32 = 5;
    cv.y__i32 = 10;
    cv.z__i32 = 0;
    Global_Space *p_gs = allocate_global_space_in__global_space_manager(&manager, cv);
    Global_Space *p_found = get_p_global_space_from__global_space_manager(&manager, cv);
    munit_assert_ptr_equal(p_gs, p_found);
    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/world/global_space_manager.h.spec.md
/// Section: 1.4.3 Lookup
///
TEST_FUNCTION(global_space_manager__lookup__not_found_returns_null) {
    Global_Space_Manager manager;
    initialize_global_space_manager(&manager);
    Chunk_Vector__3i32 cv;
    cv.x__i32 = 99;
    cv.y__i32 = 99;
    cv.z__i32 = 0;
    Global_Space *p_found = get_p_global_space_from__global_space_manager(&manager, cv);
    munit_assert_ptr_null(p_found);
    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/world/global_space_manager.h.spec.md
/// Section: 1.4.2 Allocation and Release
///
TEST_FUNCTION(global_space_manager__release__makes_deallocated) {
    Global_Space_Manager manager;
    initialize_global_space_manager(&manager);
    Chunk_Vector__3i32 cv;
    cv.x__i32 = 0;
    cv.y__i32 = 0;
    cv.z__i32 = 0;
    Global_Space *p_gs = allocate_global_space_in__global_space_manager(&manager, cv);
    munit_assert_ptr_not_null(p_gs);
    release_global_space_in__global_space_manager(&manager, p_gs);
    munit_assert_false(is_global_space__allocated(p_gs));
    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/world/global_space_manager.h.spec.md
/// Section: 1.4.5 UUID Generation (static inline)
///
TEST_FUNCTION(global_space_manager__get_uuid__deterministic) {
    Chunk_Vector__3i32 cv;
    cv.x__i32 = 3;
    cv.y__i32 = 7;
    cv.z__i32 = 0;
    Identifier__u64 uuid1 = get_uuid_for__global_space(cv);
    Identifier__u64 uuid2 = get_uuid_for__global_space(cv);
    munit_assert_uint64(uuid1, ==, uuid2);
    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/world/global_space_manager.h.spec.md
/// Section: 1.4.5 UUID Generation (static inline)
///
TEST_FUNCTION(global_space_manager__get_uuid__different_positions_differ) {
    Chunk_Vector__3i32 cv1;
    cv1.x__i32 = 0;
    cv1.y__i32 = 0;
    cv1.z__i32 = 0;
    Chunk_Vector__3i32 cv2;
    cv2.x__i32 = 1;
    cv2.y__i32 = 0;
    cv2.z__i32 = 0;
    Identifier__u64 uuid1 = get_uuid_for__global_space(cv1);
    Identifier__u64 uuid2 = get_uuid_for__global_space(cv2);
    munit_assert_uint64(uuid1, !=, uuid2);
    return MUNIT_OK;
}

DEFINE_SUITE(global_space_manager,
    INCLUDE_TEST__STATELESS(global_space_manager__initialize__all_deallocated),
    INCLUDE_TEST__STATELESS(global_space_manager__allocate__returns_non_null),
    INCLUDE_TEST__STATELESS(global_space_manager__allocate__lookup_returns_same),
    INCLUDE_TEST__STATELESS(global_space_manager__lookup__not_found_returns_null),
    INCLUDE_TEST__STATELESS(global_space_manager__release__makes_deallocated),
    INCLUDE_TEST__STATELESS(global_space_manager__get_uuid__deterministic),
    INCLUDE_TEST__STATELESS(global_space_manager__get_uuid__different_positions_differ),
    END_TESTS)
