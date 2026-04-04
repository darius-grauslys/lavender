#include <collisions/test_suite_collisions_collision_node.h>

#include <collisions/collision_node.c>

TEST_FUNCTION(collision_node__initialize__sets_empty_list) {
    Collision_Node node;
    Identifier__u64 uuid = 0x0000000100000002ULL;

    initialize_collision_node(&node, uuid);

    munit_assert_ptr_null(
            node.p_linked_list__collision_node_entries__tail);

    return MUNIT_OK;
}

TEST_FUNCTION(collision_node__initialize__sets_uuid) {
    Collision_Node node;
    Identifier__u64 uuid = 0x00000005000000AULL;

    initialize_collision_node(&node, uuid);

    munit_assert_true(is_collision_node__allocated(&node));

    return MUNIT_OK;
}

TEST_FUNCTION(collision_node__is_allocated__false_when_deallocated) {
    Collision_Node node;
    memset(&node, 0, sizeof(node));
    node._serialization_header.uuid = IDENTIFIER__UNKNOWN__u64;

    munit_assert_false(is_collision_node__allocated(&node));

    return MUNIT_OK;
}

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

TEST_FUNCTION(collision_node__remove_all_entries__leaves_empty) {
    Collision_Node_Pool pool;
    initialize_collision_node_pool(&pool);

    Identifier__u64 node_uuid = 0x0000000600000006ULL;
    Collision_Node *p_node =
        allocate_collision_node_from__collision_node_pool(
                &pool, node_uuid);

    Chunk_Vector__3i32 chunk_vec = { 6, 6, 0 };

    add_entry_to__collision_node(&pool, p_node, chunk_vec, 50);
    add_entry_to__collision_node(&pool, p_node, chunk_vec, 60);

    remove_entry_from__collision_node(&pool, p_node, 50);
    remove_entry_from__collision_node(&pool, p_node, 60);

    Quantity__u32 count =
        get_quantity_of__entries_in__collision_node(p_node);
    munit_assert_uint32(count, ==, 0);
    munit_assert_ptr_null(
            p_node->p_linked_list__collision_node_entries__tail);

    return MUNIT_OK;
}

TEST_FUNCTION(collision_node__get_quantity__empty_node_returns_zero) {
    Collision_Node node;
    Identifier__u64 uuid = 0x0000000700000007ULL;
    initialize_collision_node(&node, uuid);

    Quantity__u32 count =
        get_quantity_of__entries_in__collision_node(&node);
    munit_assert_uint32(count, ==, 0);

    return MUNIT_OK;
}

TEST_FUNCTION(collision_node__iterate_entry__traverses_list) {
    Collision_Node_Pool pool;
    initialize_collision_node_pool(&pool);

    Identifier__u64 node_uuid = 0x0000000800000008ULL;
    Collision_Node *p_node =
        allocate_collision_node_from__collision_node_pool(
                &pool, node_uuid);

    Chunk_Vector__3i32 chunk_vec = { 8, 8, 0 };

    add_entry_to__collision_node(&pool, p_node, chunk_vec, 1);
    add_entry_to__collision_node(&pool, p_node, chunk_vec, 2);
    add_entry_to__collision_node(&pool, p_node, chunk_vec, 3);

    Collision_Node_Entry *p_entry =
        p_node->p_linked_list__collision_node_entries__tail;

    int count = 0;
    while (p_entry) {
        count++;
        p_entry = p_entry->p_previous_entry;
    }

    munit_assert_int(count, ==, 3);

    return MUNIT_OK;
}

DEFINE_SUITE(collision_node,
    INCLUDE_TEST__STATELESS(collision_node__initialize__sets_empty_list),
    INCLUDE_TEST__STATELESS(collision_node__initialize__sets_uuid),
    INCLUDE_TEST__STATELESS(collision_node__is_allocated__false_when_deallocated),
    INCLUDE_TEST__STATELESS(collision_node__add_entry__single_entry),
    INCLUDE_TEST__STATELESS(collision_node__add_entry__multiple_entries),
    INCLUDE_TEST__STATELESS(collision_node__remove_entry__removes_tail),
    INCLUDE_TEST__STATELESS(collision_node__remove_entry__removes_head),
    INCLUDE_TEST__STATELESS(collision_node__remove_entry__removes_middle),
    INCLUDE_TEST__STATELESS(collision_node__remove_all_entries__leaves_empty),
    INCLUDE_TEST__STATELESS(collision_node__get_quantity__empty_node_returns_zero),
    INCLUDE_TEST__STATELESS(collision_node__iterate_entry__traverses_list),
    END_TESTS)
