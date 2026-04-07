#include <collisions/test_suite_collisions_collision_node.h>

#include <collisions/collision_node.c>

/*
 * Spec: docs/specs/core/collisions/collision_node.h.spec.md
 * Section: 1.4.1 Initialization
 *
 * Verifies that initialize_collision_node sets the entry list tail
 * pointer to NULL, leaving the node in an empty state.
 */
TEST_FUNCTION(collision_node__initialize__sets_empty_list) {
    Collision_Node node;
    Identifier__u64 uuid = 0x0000000100000002ULL;

    initialize_collision_node(&node, uuid);

    munit_assert_ptr_null(
            node.p_linked_list__collision_node_entries__tail);

    return MUNIT_OK;
}

/*
 * Spec: docs/specs/core/collisions/collision_node.h.spec.md
 * Section: 1.4.1 Initialization
 *
 * Verifies that initialize_collision_node stores the provided 64-bit
 * UUID such that is_collision_node__allocated returns true afterward.
 */
TEST_FUNCTION(collision_node__initialize__sets_uuid) {
    Collision_Node node;
    Identifier__u64 uuid = 0x00000005000000AULL;

    initialize_collision_node(&node, uuid);

    munit_assert_true(is_collision_node__allocated(&node));

    return MUNIT_OK;
}

/*
 * Spec: docs/specs/core/collisions/collision_node.h.spec.md
 * Section: 1.4.7 Allocation Query
 *
 * Verifies that is_collision_node__allocated returns false when the
 * node's UUID is set to the deallocated sentinel IDENTIFIER__UNKNOWN__u64.
 */
TEST_FUNCTION(collision_node__is_allocated__false_when_deallocated) {
    Collision_Node node;
    memset(&node, 0, sizeof(node));
    node._serialization_header.uuid = IDENTIFIER__UNKNOWN__u64;

    munit_assert_false(is_collision_node__allocated(&node));

    return MUNIT_OK;
}

/*
 * Spec: docs/specs/core/collisions/collision_node.h.spec.md
 * Section: 1.4.2 Entry Management
 *
 * Verifies that add_entry_to__collision_node succeeds for a single
 * entry, returns true, and correctly sets the tail pointer and its
 * hitbox UUID field.
 */
TEST_FUNCTION(collision_node__add_entry__single_entry) {
    Collision_Node_Pool pool;
    initialize_collision_node_pool(&pool);

    Identifier__u64 node_uuid = 0x0000000100000001ULL;
    Collision_Node *p_node =
        allocate_collision_node_from__collision_node_pool(
                &pool, node_uuid);

    munit_assert_ptr_not_null(p_node);

    Chunk_Vector__3i32 chunk_vec = { 1, 1, 0 };
    Identifier__u32 hitbox_uuid = 42;

    bool result = add_entry_to__collision_node(
            &pool, p_node, chunk_vec, hitbox_uuid);

    munit_assert_true(result);
    munit_assert_ptr_not_null(
            p_node->p_linked_list__collision_node_entries__tail);
    munit_assert_uint32(
            p_node->p_linked_list__collision_node_entries__tail
                ->uuid_of__hitbox__u32,
            ==,
            hitbox_uuid);

    return MUNIT_OK;
}

/*
 * Spec: docs/specs/core/collisions/collision_node.h.spec.md
 * Section: 1.4.2 Entry Management
 *
 * Verifies that add_entry_to__collision_node correctly accumulates
 * multiple entries, with get_quantity_of__entries_in__collision_node
 * reflecting the correct count after each addition.
 */
TEST_FUNCTION(collision_node__add_entry__multiple_entries) {
    Collision_Node_Pool pool;
    initialize_collision_node_pool(&pool);

    Identifier__u64 node_uuid = 0x0000000200000002ULL;
    Collision_Node *p_node =
        allocate_collision_node_from__collision_node_pool(
                &pool, node_uuid);

    munit_assert_ptr_not_null(p_node);

    Chunk_Vector__3i32 chunk_vec = { 2, 2, 0 };

    bool r1 = add_entry_to__collision_node(
            &pool, p_node, chunk_vec, 10);
    bool r2 = add_entry_to__collision_node(
            &pool, p_node, chunk_vec, 20);
    bool r3 = add_entry_to__collision_node(
            &pool, p_node, chunk_vec, 30);

    munit_assert_true(r1);
    munit_assert_true(r2);
    munit_assert_true(r3);

    Quantity__u32 count =
        get_quantity_of__entries_in__collision_node(p_node);
    munit_assert_uint32(count, ==, 3);

    return MUNIT_OK;
}

/*
 * Spec: docs/specs/core/collisions/collision_node.h.spec.md
 * Section: 1.4.2 Entry Management
 *
 * Verifies that remove_entry_from__collision_node correctly removes
 * the tail entry (most recently added), leaving the previous entry
 * as the new tail.
 */
TEST_FUNCTION(collision_node__remove_entry__removes_tail) {
    Collision_Node_Pool pool;
    initialize_collision_node_pool(&pool);

    Identifier__u64 node_uuid = 0x0000000300000003ULL;
    Collision_Node *p_node =
        allocate_collision_node_from__collision_node_pool(
                &pool, node_uuid);

    Chunk_Vector__3i32 chunk_vec = { 3, 3, 0 };

    add_entry_to__collision_node(&pool, p_node, chunk_vec, 100);
    add_entry_to__collision_node(&pool, p_node, chunk_vec, 200);

    remove_entry_from__collision_node(&pool, p_node, 200);

    Quantity__u32 count =
        get_quantity_of__entries_in__collision_node(p_node);
    munit_assert_uint32(count, ==, 1);

    munit_assert_uint32(
            p_node->p_linked_list__collision_node_entries__tail
                ->uuid_of__hitbox__u32,
            ==,
            100);

    return MUNIT_OK;
}

/*
 * Spec: docs/specs/core/collisions/collision_node.h.spec.md
 * Section: 1.4.2 Entry Management
 *
 * Verifies that remove_entry_from__collision_node correctly removes
 * the head entry (first added / deepest in the list), leaving the
 * remaining entry as the sole tail.
 */
TEST_FUNCTION(collision_node__remove_entry__removes_head) {
    Collision_Node_Pool pool;
    initialize_collision_node_pool(&pool);

    Identifier__u64 node_uuid = 0x0000000400000004ULL;
    Collision_Node *p_node =
        allocate_collision_node_from__collision_node_pool(
                &pool, node_uuid);

    Chunk_Vector__3i32 chunk_vec = { 4, 4, 0 };

    add_entry_to__collision_node(&pool, p_node, chunk_vec, 100);
    add_entry_to__collision_node(&pool, p_node, chunk_vec, 200);

    remove_entry_from__collision_node(&pool, p_node, 100);

    Quantity__u32 count =
        get_quantity_of__entries_in__collision_node(p_node);
    munit_assert_uint32(count, ==, 1);

    munit_assert_uint32(
            p_node->p_linked_list__collision_node_entries__tail
                ->uuid_of__hitbox__u32,
            ==,
            200);

    return MUNIT_OK;
}

/*
 * Spec: docs/specs/core/collisions/collision_node.h.spec.md
 * Section: 1.4.2 Entry Management
 *
 * Verifies that remove_entry_from__collision_node correctly removes
 * an entry from the middle of the linked list, keeping the remaining
 * entries intact and reducing the count by one.
 */
TEST_FUNCTION(collision_node__remove_entry__removes_middle) {
    Collision_Node_Pool pool;
    initialize_collision_node_pool(&pool);

    Identifier__u64 node_uuid = 0x0000000500000005ULL;
    Collision_Node *p_node =
        allocate_collision_node_from__collision_node_pool(
                &pool, node_uuid);

    Chunk_Vector__3i32 chunk_vec = { 5, 5, 0 };

    add_entry_to__collision_node(&pool, p_node, chunk_vec, 10);
    add_entry_to__collision_node(&pool, p_node, chunk_vec, 20);
    add_entry_to__collision_node(&pool, p_node, chunk_vec, 30);

    remove_entry_from__collision_node(&pool, p_node, 20);

    Quantity__u32 count =
        get_quantity_of__entries_in__collision_node(p_node);
    munit_assert_uint32(count, ==, 2);

    return MUNIT_OK;
}

/*
 * Spec: docs/specs/core/collisions/collision_node.h.spec.md
 * Section: 1.4.2 Entry Management
 *
 * Verifies that removing