#include <world/test_suite_world_local_space.h>

#include <world/local_space.c>

///
/// Spec: docs/specs/core/world/local_space.h.spec.md
/// Section: 1.4.1 Initialization
///
TEST_FUNCTION(local_space__initialize__null_global_space) {
    Local_Space ls;
    initialize_local_space(&ls);
    munit_assert_ptr_null(get_p_global_space_from__local_space(&ls));
    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/world/local_space.h.spec.md
/// Section: 1.4.1 Initialization
///
TEST_FUNCTION(local_space__initialize__null_neighbors) {
    Local_Space ls;
    initialize_local_space(&ls);
    munit_assert_ptr_null(ls.p_local_space__north);
    munit_assert_ptr_null(ls.p_local_space__east);
    munit_assert_ptr_null(ls.p_local_space__south);
    munit_assert_ptr_null(ls.p_local_space__west);
    munit_assert_ptr_null(ls.p_local_space__above);
    munit_assert_ptr_null(ls.p_local_space__below);
    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/world/local_space.h.spec.md
/// Section: 1.4.1 Initialization
///
TEST_FUNCTION(local_space__initialize__not_allocated) {
    Local_Space ls;
    initialize_local_space(&ls);
    munit_assert_false(is_local_space__allocated(&ls));
    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/world/local_space.h.spec.md
/// Section: 1.4.1 Initialization
///
TEST_FUNCTION(local_space__initialize__not_active) {
    Local_Space ls;
    initialize_local_space(&ls);
    munit_assert_false(is_local_space__active(&ls));
    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/world/local_space.h.spec.md
/// Section: 1.4.2 Neighbor Setup
///
TEST_FUNCTION(local_space__set_neighbors__sets_all_six) {
    Local_Space ls;
    Local_Space north, east, south, west, above, below;
    initialize_local_space(&ls);
    initialize_local_space(&north);
    initialize_local_space(&east);
    initialize_local_space(&south);
    initialize_local_space(&west);
    initialize_local_space(&above);
    initialize_local_space(&below);
    set_neighbors_of__local_space(&ls, &north, &east, &south, &west, &above, &below);
    munit_assert_ptr_equal(ls.p_local_space__north, &north);
    munit_assert_ptr_equal(ls.p_local_space__east, &east);
    munit_assert_ptr_equal(ls.p_local_space__south, &south);
    munit_assert_ptr_equal(ls.p_local_space__west, &west);
    munit_assert_ptr_equal(ls.p_local_space__above, &above);
    munit_assert_ptr_equal(ls.p_local_space__below, &below);
    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/world/local_space.h.spec.md
/// Section: 1.4.4 State Queries
///
TEST_FUNCTION(local_space__is_allocated__null_returns_false) {
    munit_assert_false(is_local_space__allocated(0));
    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/world/local_space.h.spec.md
/// Section: 1.4.3 Accessors
///
TEST_FUNCTION(local_space__get_global_space__null_safe) {
    Global_Space *p_gs = get_p_global_space_from__local_space(0);
    munit_assert_ptr_null(p_gs);
    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/world/local_space.h.spec.md
/// Section: 1.4.3 Accessors
///
TEST_FUNCTION(local_space__get_chunk__null_safe) {
    Chunk *p_chunk = get_p_chunk_from__local_space(0);
    munit_assert_ptr_null(p_chunk);
    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/world/local_space.h.spec.md
/// Section: 1.4.3 Accessors
///
TEST_FUNCTION(local_space__get_chunk__null_global_space_returns_null) {
    Local_Space ls;
    initialize_local_space(&ls);
    Chunk *p_chunk = get_p_chunk_from__local_space(&ls);
    munit_assert_ptr_null(p_chunk);
    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/world/local_space.h.spec.md
/// Section: 1.4.4 State Queries
///
TEST_FUNCTION(local_space__is_allocated__with_allocated_global_space) {
    Local_Space ls;
    initialize_local_space(&ls);
    Global_Space gs;
    initialize_global_space_as__allocated(&gs, 1);
    ls.p_global_space = &gs;
    munit_assert_true(is_local_space__allocated(&ls));
    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/world/local_space.h.spec.md
/// Section: 1.4.4 State Queries
///
TEST_FUNCTION(local_space__is_active__with_active_global_space) {
    Local_Space ls;
    initialize_local_space(&ls);
    Global_Space gs;
    initialize_global_space_as__allocated(&gs, 1);
    hold_global_space(&gs);
    ls.p_global_space = &gs;
    munit_assert_true(is_local_space__active(&ls));
    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/world/local_space.h.spec.md
/// Section: 1.4.4 State Queries
///
TEST_FUNCTION(local_space__is_active__false_when_constructing) {
    Local_Space ls;
    initialize_local_space(&ls);
    Global_Space gs;
    initialize_global_space_as__allocated(&gs, 1);
    hold_global_space(&gs);
    set_global_space_as__constructing(&gs);
    ls.p_global_space = &gs;
    munit_assert_false(is_local_space__active(&ls));
    return MUNIT_OK;
}

DEFINE_SUITE(local_space,
    INCLUDE_TEST__STATELESS(local_space__initialize__null_global_space),
    INCLUDE_TEST__STATELESS(local_space__initialize__null_neighbors),
    INCLUDE_TEST__STATELESS(local_space__initialize__not_allocated),
    INCLUDE_TEST__STATELESS(local_space__initialize__not_active),
    INCLUDE_TEST__STATELESS(local_space__set_neighbors__sets_all_six),
    INCLUDE_TEST__STATELESS(local_space__is_allocated__null_returns_false),
    INCLUDE_TEST__STATELESS(local_space__get_global_space__null_safe),
    INCLUDE_TEST__STATELESS(local_space__get_chunk__null_safe),
    INCLUDE_TEST__STATELESS(local_space__get_chunk__null_global_space_returns_null),
    INCLUDE_TEST__STATELESS(local_space__is_allocated__with_allocated_global_space),
    INCLUDE_TEST__STATELESS(local_space__is_active__with_active_global_space),
    INCLUDE_TEST__STATELESS(local_space__is_active__false_when_constructing),
    END_TESTS)
