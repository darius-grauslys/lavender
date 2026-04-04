#include <collisions/test_suite_collisions_collision_node_pool.h>

#include <collisions/collision_node_pool.c>

TEST_FUNCTION(collision_node_pool__initialize__all_nodes_deallocated) {
    Collision_Node_Pool pool;
    initialize_collision_node_pool(&pool);

    for (Index__u32 i = 0; i < QUANTITY_OF__GLOBAL_SPACE; i++) {
        munit_assert_false(
                is_collision_node__allocated(
                    &pool.collision_nodes[i]));
    }

    return MUNIT_OK;
}

TEST_FUNCTION(collision_node_pool__allocate_node__returns_non_null) {
    Collision_Node_Pool pool;
    initialize_collision_node_pool(&pool);

    Identifier__u64 uuid = 0x0000000100000001ULL;
    Collision_Node *p_node =
        allocate_collision_node_from__collision_node_pool(
                &pool, uuid);

    munit_assert_ptr_not_null(p_node);
    munit_assert_true(is_collision_node__allocated(p_node));

    return MUNIT_OK;
}

TEST_FUNCTION(collision_node_pool__allocate_node__is_findable_by_uuid) {
    Collision_Node_Pool pool;
    initialize_collision_node_pool(&pool);

    Identifier__u64 uuid = 0x0000000200000003ULL;
    Collision_Node *p_node_allocated =
        allocate_collision_node_from__collision_node_pool(
                &pool, uuid);

    Collision_Node *p_node_found =
        get_p_collision_node_by__uuid_64_from__collision_node_pool(
                &pool, uuid);

    munit_assert_ptr_equal(p_node_allocated, p_node_found);

    return MUNIT_OK;
}

TEST_FUNCTION(collision_node_pool__release_node__marks_deallocated) {
    Collision_Node_Pool pool;
    initialize_collision_node_pool(&pool);

    Identifier__u64 uuid = 0x0000000400000005ULL;
    Collision_Node *p_node =
        allocate_collision_node_from__collision_node_pool(
                &pool, uuid);

    munit_assert_ptr_not_null(p_node);
    munit_assert_true(is_collision_node__allocated(p_node));

    release_collision_node_from__collision_node_pool(&pool, p_node);

    munit_assert_false(is_collision_node__allocated(p_node));

    return MUNIT_OK;
}

TEST_FUNCTION(collision_node_pool__allocate_multiple_nodes__all_valid) {
    Collision_Node_Pool pool;
    initialize_collision_node_pool(&pool);

    Collision_Node *nodes[4];
    for (int i = 0; i < 4; i++) {
        Identifier__u64 uuid =
            ((Identifier__u64)(i + 1) << 32)
            | (Identifier__u64)(i + 10);
        nodes[i] =
            allocate_collision_node_from__collision_node_pool(
                    &pool, uuid);
        munit_assert_ptr_not_null(nodes[i]);
        munit_assert_true(is_collision_node__allocated(nodes[i]));
    }

    for (int i = 0; i < 4; i++) {
        for (int j = i + 1; j < 4; j++) {
            munit_assert_ptr_not_equal(nodes[i], nodes[j]);
        }
    }

    return MUNIT_OK;
}

TEST_FUNCTION(collision_node_pool__allocate_entry__returns_non_null) {
    Collision_Node_Pool pool;
    initialize_collision_node_pool(&pool);

    Collision_Node_Entry *p_entry =
        allocate_collision_node_entry_from__collision_node_pool(&pool);

    munit_assert_ptr_not_null(p_entry);

    return MUNIT_OK;
}

TEST_FUNCTION(collision_node_pool__allocate_release_entry__reusable) {
    Collision_Node_Pool pool;
    initialize_collision_node_pool(&pool);

    Collision_Node_Entry *p_entry =
        allocate_collision_node_entry_from__collision_node_pool(&pool);
    munit_assert_ptr_not_null(p_entry);

    release_collision_node_entry_from__collision_node_pool(
            &pool, p_entry);

    Collision_Node_Entry *p_entry_2 =
        allocate_collision_node_entry_from__collision_node_pool(&pool);
    munit_assert_ptr_not_null(p_entry_2);

    return MUNIT_OK;
}

TEST_FUNCTION(collision_node_pool__allocate_all_entries__exhausts_pool) {
    Collision_Node_Pool pool;
    initialize_collision_node_pool(&pool);

    for (Index__u32 i = 0; i < MAX_QUANTITY_OF__HITBOX_AABB; i++) {
        Collision_Node_Entry *p_entry =
            allocate_collision_node_entry_from__collision_node_pool(
                    &pool);
        munit_assert_ptr_not_null(p_entry);
    }

    Collision_Node_Entry *p_entry_overflow =
        allocate_collision_node_entry_from__collision_node_pool(&pool);
    munit_assert_ptr_null(p_entry_overflow);

    return MUNIT_OK;
}

TEST_FUNCTION(collision_node_pool__lookup_unallocated__returns_null) {
    Collision_Node_Pool pool;
    initialize_collision_node_pool(&pool);

    Identifier__u64 uuid = 0x00000099000000AAULL;
    Collision_Node *p_node =
        get_p_collision_node_by__uuid_64_from__collision_node_pool(
                &pool, uuid);

    munit_assert_ptr_null(p_node);

    return MUNIT_OK;
}

TEST_FUNCTION(collision_node_pool__release_and_reallocate_node__works) {
    Collision_Node_Pool pool;
    initialize_collision_node_pool(&pool);

    Identifier__u64 uuid = 0x0000000A0000000BULL;
    Collision_Node *p_node =
        allocate_collision_node_from__collision_node_pool(
                &pool, uuid);
    munit_assert_ptr_not_null(p_node);

    release_collision_node_from__collision_node_pool(&pool, p_node);
    munit_assert_false(is_collision_node__allocated(p_node));

    Collision_Node *p_node_2 =
        allocate_collision_node_from__collision_node_pool(
                &pool, uuid);
    munit_assert_ptr_not_null(p_node_2);
    munit_assert_true(is_collision_node__allocated(p_node_2));

    return MUNIT_OK;
}

DEFINE_SUITE(collision_node_pool,
    INCLUDE_TEST__STATELESS(collision_node_pool__initialize__all_nodes_deallocated),
    INCLUDE_TEST__STATELESS(collision_node_pool__allocate_node__returns_non_null),
    INCLUDE_TEST__STATELESS(collision_node_pool__allocate_node__is_findable_by_uuid),
    INCLUDE_TEST__STATELESS(collision_node_pool__release_node__marks_deallocated),
    INCLUDE_TEST__STATELESS(collision_node_pool__allocate_multiple_nodes__all_valid),
    INCLUDE_TEST__STATELESS(collision_node_pool__allocate_entry__returns_non_null),
    INCLUDE_TEST__STATELESS(collision_node_pool__allocate_release_entry__reusable),
    INCLUDE_TEST__STATELESS(collision_node_pool__allocate_all_entries__exhausts_pool),
    INCLUDE_TEST__STATELESS(collision_node_pool__lookup_unallocated__returns_null),
    INCLUDE_TEST__STATELESS(collision_node_pool__release_and_reallocate_node__works),
    END_TESTS)
