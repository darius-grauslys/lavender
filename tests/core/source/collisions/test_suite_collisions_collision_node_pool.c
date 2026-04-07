#include <collisions/test_suite_collisions_collision_node_pool.h>

#include <collisions/collision_node_pool.c>

/**
 * Spec: collision_node_pool.h.spec.md
 * Section: 1.4.1 Initialization
 *          1.5.5 Postconditions
 *
 * Verifies that after initialize_collision_node_pool, every node slot
 * in the pool reports as deallocated (is_collision_node__allocated == false).
 */
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

/**
 * Spec: collision_node_pool.h.spec.md
 * Section: 1.4.2 Node Allocation
 *          1.5.5 Postconditions
 *
 * Verifies that allocate_collision_node_from__collision_node_pool returns
 * a non-null pointer and that the returned node reports as allocated.
 */
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

/**
 * Spec: collision_node_pool.h.spec.md
 * Section: 1.4.4 Lookup (static inline)
 *          1.5.2 Hashing Strategy
 *
 * Verifies that a node allocated with a given UUID can be retrieved by
 * that same UUID via get_p_collision_node_by__uuid_64_from__collision_node_pool,
 * and that the returned pointer matches the originally allocated pointer.
 */
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

/**
 * Spec: collision_node_pool.h.spec.md
 * Section: 1.4.2 Node Allocation
 *          1.5.5 Postconditions
 *
 * Verifies that after release_collision_node_from__collision_node_pool,
 * the previously allocated node reports as deallocated
 * (is_collision_node__allocated == false).
 */
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

/**
 * Spec: collision_node_pool.h.spec.md
 * Section: 1.4.2 Node Allocation
 *
 * Verifies that multiple collision nodes can be allocated simultaneously,
 * each returning a non-null, allocated pointer, and that all returned
 * pointers are distinct from one another.
 */
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

/**
 * Spec: collision_node_pool.h.spec.md
 * Section: 1.4.3 Entry Allocation
 *
 * Verifies that allocate_collision_node_entry_from__collision_node_pool
 * returns a non-null pointer when the entry pool is not exhausted.
 */
TEST_FUNCTION(collision_node_pool__allocate_entry__returns_non_null) {
    Collision_Node_Pool pool;
    initialize_collision_node_pool(&pool);

    Collision_Node_Entry *p_entry =
        allocate_collision_node_entry_from__collision_node_pool(&pool);

    munit_assert_ptr_not_null(p_entry);

    return MUNIT_OK;
}

/**
 * Spec: collision_node_pool.h.spec.md
 * Section: 1.4.3 Entry Allocation
 *          1.5.1 Pool Lifecycle
 *
 * Verifies that an entry released via
 * release_collision_node_entry_from__collision_node_pool can be
 * successfully reallocated, confirming the entry slot is returned
 * to the available pool.
 */
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

/**
 * Spec: collision_node_pool.h.spec.md
 * Section: 1.4.3 Entry Allocation
 *          1.5.6 Error Handling
 *
 * Verifies that allocating MAX_QUANTITY_OF__HITBOX_AABB entries succeeds,
 * and that a subsequent allocation attempt returns NULL, confirming the
 * entry pool is exhausted and error handling returns NULL as specified.
 */
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

/**
 * Spec: collision_node_pool.h.spec.md
 * Section: 1.4.4 Lookup (static inline)
 *          1.5.6 Error Handling
 *
 * Verifies that looking up a UUID that has never been allocated returns
 * NULL, confirming the O(1) lookup correctly distinguishes unallocated
 * slots.
 */
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

/**
 * Spec: collision_node_pool.h.spec.md
 * Section: 1.4.2 Node Allocation
 *          1.5.1 Pool Lifecycle
 *
 * Verifies that a node slot released via
 * release_collision_node_from__collision_node_pool can be reallocated
 * with the same UUID, returning a non-null, allocated node, confirming
 * the slot is correctly returned to the pool for reuse.
 */
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
