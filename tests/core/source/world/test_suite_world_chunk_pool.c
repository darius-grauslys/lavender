#include <world/test_suite_world_chunk_pool.h>

#include <world/chunk_pool.c>

TEST_FUNCTION(chunk_pool__initialize__all_deallocated) {
    Chunk_Pool pool;
    initialize_chunk_pool(&pool);
    for (Index__u32 i = 0; i < QUANTITY_OF__GLOBAL_SPACE; i++) {
        munit_assert_false(is_chunk__active(&pool.chunks[i]));
    }
    return MUNIT_OK;
}

TEST_FUNCTION(chunk_pool__allocate__returns_non_null) {
    Chunk_Pool pool;
    initialize_chunk_pool(&pool);
    Chunk *p_chunk = allocate_chunk_from__chunk_pool(&pool, 12345);
    munit_assert_ptr_not_null(p_chunk);
    return MUNIT_OK;
}

TEST_FUNCTION(chunk_pool__allocate__sets_uuid) {
    Chunk_Pool pool;
    initialize_chunk_pool(&pool);
    Identifier__u64 uuid = 99999;
    Chunk *p_chunk = allocate_chunk_from__chunk_pool(&pool, uuid);
    munit_assert_ptr_not_null(p_chunk);
    munit_assert_uint64(get_uuid__chunk(p_chunk), ==, uuid);
    return MUNIT_OK;
}

TEST_FUNCTION(chunk_pool__release__makes_available) {
    Chunk_Pool pool;
    initialize_chunk_pool(&pool);
    Chunk *p_chunk = allocate_chunk_from__chunk_pool(&pool, 1);
    munit_assert_ptr_not_null(p_chunk);
    release_chunk_from__chunk_pool(&pool, p_chunk);
    Chunk *p_chunk2 = allocate_chunk_from__chunk_pool(&pool, 2);
    munit_assert_ptr_not_null(p_chunk2);
    return MUNIT_OK;
}

TEST_FUNCTION(chunk_pool__allocate_multiple__returns_different_chunks) {
    Chunk_Pool pool;
    initialize_chunk_pool(&pool);
    Chunk *p_chunk1 = allocate_chunk_from__chunk_pool(&pool, 1);
    Chunk *p_chunk2 = allocate_chunk_from__chunk_pool(&pool, 2);
    munit_assert_ptr_not_null(p_chunk1);
    munit_assert_ptr_not_null(p_chunk2);
    munit_assert_ptr_not_equal(p_chunk1, p_chunk2);
    return MUNIT_OK;
}

DEFINE_SUITE(chunk_pool,
    INCLUDE_TEST__STATELESS(chunk_pool__initialize__all_deallocated),
    INCLUDE_TEST__STATELESS(chunk_pool__allocate__returns_non_null),
    INCLUDE_TEST__STATELESS(chunk_pool__allocate__sets_uuid),
    INCLUDE_TEST__STATELESS(chunk_pool__release__makes_available),
    INCLUDE_TEST__STATELESS(chunk_pool__allocate_multiple__returns_different_chunks),
    END_TESTS)
