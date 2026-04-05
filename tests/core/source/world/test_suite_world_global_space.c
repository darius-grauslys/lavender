#include <world/test_suite_world_global_space.h>

#include <world/global_space.c>

TEST_FUNCTION(global_space__initialize_global_space__sets_deallocated) {
    Global_Space global_space;
    initialize_global_space(&global_space);
    munit_assert_false(is_global_space__allocated(&global_space));
    return MUNIT_OK;
}

TEST_FUNCTION(global_space__initialize_global_space__clears_all_flags) {
    Global_Space global_space;
    initialize_global_space(&global_space);
    munit_assert_false(is_global_space__constructing(&global_space));
    munit_assert_false(is_global_space__deconstructing(&global_space));
    munit_assert_false(is_global_space__awaiting_construction(&global_space));
    munit_assert_false(is_global_space__awaiting_deconstruction(&global_space));
    munit_assert_false(is_global_space__dirty(&global_space));
    return MUNIT_OK;
}

TEST_FUNCTION(global_space__initialize_global_space_as__allocated__is_allocated) {
    Global_Space global_space;
    initialize_global_space_as__allocated(&global_space, 12345);
    munit_assert_true(is_global_space__allocated(&global_space));
    return MUNIT_OK;
}

TEST_FUNCTION(global_space__is_global_space__allocated__null_returns_false) {
    munit_assert_false(is_global_space__allocated(0));
    return MUNIT_OK;
}

TEST_FUNCTION(global_space__hold_and_drop__increments_and_decrements) {
    Global_Space global_space;
    initialize_global_space_as__allocated(&global_space, 1);
    Quantity__u16 initial_refs = global_space.quantity_of__references;
    hold_global_space(&global_space);
    munit_assert_uint16(global_space.quantity_of__references, ==, initial_refs + 1);
    drop_global_space(&global_space);
    munit_assert_uint16(global_space.quantity_of__references, ==, initial_refs);
    return MUNIT_OK;
}

TEST_FUNCTION(global_space__drop__returns_true_when_all_dropped) {
    Global_Space global_space;
    initialize_global_space_as__allocated(&global_space, 1);
    hold_global_space(&global_space);
    hold_global_space(&global_space);
    munit_assert_false(drop_global_space(&global_space));
    bool result = drop_global_space(&global_space);
    munit_assert_true(result);
    return MUNIT_OK;
}

TEST_FUNCTION(global_space__set_constructing__sets_flag_and_clears_awaiting) {
    Global_Space global_space;
    initialize_global_space_as__allocated(&global_space, 1);
    set_global_space_as__awaiting_construction(&global_space);
    munit_assert_true(is_global_space__awaiting_construction(&global_space));
    set_global_space_as__constructing(&global_space);
    munit_assert_true(is_global_space__constructing(&global_space));
    munit_assert_false(is_global_space__awaiting_construction(&global_space));
    return MUNIT_OK;
}

TEST_FUNCTION(global_space__set_deconstructing__sets_flag_and_clears_awaiting) {
    Global_Space global_space;
    initialize_global_space_as__allocated(&global_space, 1);
    set_global_space_as__awaiting_deconstruction(&global_space);
    munit_assert_true(is_global_space__awaiting_deconstruction(&global_space));
    set_global_space_as__deconstructing(&global_space);
    munit_assert_true(is_global_space__deconstructing(&global_space));
    munit_assert_false(is_global_space__awaiting_deconstruction(&global_space));
    return MUNIT_OK;
}

TEST_FUNCTION(global_space__set_not_constructing__clears_both_flags) {
    Global_Space global_space;
    initialize_global_space_as__allocated(&global_space, 1);
    set_global_space_as__awaiting_construction(&global_space);
    set_global_space_as__constructing(&global_space);
    set_global_space_as__NOT_constructing(&global_space);
    munit_assert_false(is_global_space__constructing(&global_space));
    munit_assert_false(is_global_space__awaiting_construction(&global_space));
    return MUNIT_OK;
}

TEST_FUNCTION(global_space__set_not_deconstructing__clears_both_flags) {
    Global_Space global_space;
    initialize_global_space_as__allocated(&global_space, 1);
    set_global_space_as__awaiting_deconstruction(&global_space);
    set_global_space_as__deconstructing(&global_space);
    set_global_space_as__NOT_deconstructing(&global_space);
    munit_assert_false(is_global_space__deconstructing(&global_space));
    munit_assert_false(is_global_space__awaiting_deconstruction(&global_space));
    return MUNIT_OK;
}

TEST_FUNCTION(global_space__dirty_flag__set_and_clear) {
    Global_Space global_space;
    initialize_global_space_as__allocated(&global_space, 1);
    munit_assert_false(is_global_space__dirty(&global_space));
    set_global_space_as__dirty(&global_space);
    munit_assert_true(is_global_space__dirty(&global_space));
    set_global_space_as__NOT_dirty(&global_space);
    munit_assert_false(is_global_space__dirty(&global_space));
    return MUNIT_OK;
}

TEST_FUNCTION(global_space__is_dirty__null_safe) {
    munit_assert_false(is_global_space__dirty(0));
    return MUNIT_OK;
}

TEST_FUNCTION(global_space__is_active__requires_allocated_and_no_construction_flags) {
    Global_Space global_space;
    initialize_global_space_as__allocated(&global_space, 1);
    hold_global_space(&global_space);
    munit_assert_true(is_global_space__active(&global_space));
    set_global_space_as__constructing(&global_space);
    munit_assert_false(is_global_space__active(&global_space));
    return MUNIT_OK;
}

TEST_FUNCTION(global_space__set_and_get_chunk) {
    Global_Space global_space;
    initialize_global_space(&global_space);
    Chunk chunk;
    set_chunk_for__global_space(&global_space, &chunk);
    munit_assert_ptr_equal(get_p_chunk_from__global_space(&global_space), &chunk);
    return MUNIT_OK;
}

TEST_FUNCTION(global_space__get_chunk__null_safe) {
    Chunk *p_chunk = get_p_chunk_from__global_space(0);
    munit_assert_ptr_null(p_chunk);
    return MUNIT_OK;
}

TEST_FUNCTION(global_space__set_and_get_collision_node) {
    Global_Space global_space;
    initialize_global_space(&global_space);
    Collision_Node node;
    set_collision_node_for__global_space(&global_space, &node);
    munit_assert_ptr_equal(get_p_collision_node_from__global_space(&global_space), &node);
    return MUNIT_OK;
}

DEFINE_SUITE(global_space,
    INCLUDE_TEST__STATELESS(global_space__initialize_global_space__sets_deallocated),
    INCLUDE_TEST__STATELESS(global_space__initialize_global_space__clears_all_flags),
    INCLUDE_TEST__STATELESS(global_space__initialize_global_space_as__allocated__is_allocated),
    INCLUDE_TEST__STATELESS(global_space__is_global_space__allocated__null_returns_false),
    INCLUDE_TEST__STATELESS(global_space__hold_and_drop__increments_and_decrements),
    INCLUDE_TEST__STATELESS(global_space__drop__returns_true_when_all_dropped),
    INCLUDE_TEST__STATELESS(global_space__set_constructing__sets_flag_and_clears_awaiting),
    INCLUDE_TEST__STATELESS(global_space__set_deconstructing__sets_flag_and_clears_awaiting),
    INCLUDE_TEST__STATELESS(global_space__set_not_constructing__clears_both_flags),
    INCLUDE_TEST__STATELESS(global_space__set_not_deconstructing__clears_both_flags),
    INCLUDE_TEST__STATELESS(global_space__dirty_flag__set_and_clear),
    INCLUDE_TEST__STATELESS(global_space__is_dirty__null_safe),
    INCLUDE_TEST__STATELESS(global_space__is_active__requires_allocated_and_no_construction_flags),
    INCLUDE_TEST__STATELESS(global_space__set_and_get_chunk),
    INCLUDE_TEST__STATELESS(global_space__get_chunk__null_safe),
    INCLUDE_TEST__STATELESS(global_space__set_and_get_collision_node),
    END_TESTS)
