#include <world/test_suite_world_chunk_generator_table.h>

#include <world/chunk_generator_table.c>

/**
 * Spec:    docs/specs/core/world/chunk_generator_table.h.spec.md
 * Section: 1.4 Functions — initialize_chunk_generator_table
 *
 * Verifies that initialize_chunk_generator_table sets all generator
 * slots to null.
 */
TEST_FUNCTION(chunk_generator_table__initialize__all_null) {
    Chunk_Generator_Table table;
    initialize_chunk_generator_table(&table);
    m_Process proc = get_default_chunk_generator_process(&table);
    munit_assert_ptr_null(proc);
    return MUNIT_OK;
}

/**
 * Spec:    docs/specs/core/world/chunk_generator_table.h.spec.md
 * Section: 1.4 Functions — register_chunk_generator_into__chunk_generator_table,
 *          get_chunk_generator_process_from__chunk_generator_table
 *
 * Verifies that a generator process registered for a given kind can be
 * retrieved by the same kind.
 */
TEST_FUNCTION(chunk_generator_table__register_and_get) {
    Chunk_Generator_Table table;
    initialize_chunk_generator_table(&table);
    m_Process dummy = (m_Process)0xDEADBEEF;
    register_chunk_generator_into__chunk_generator_table(
        &table, Chunk_Generator_Kind__None, dummy);
    m_Process result = get_chunk_generator_process_from__chunk_generator_table(
        &table, Chunk_Generator_Kind__None);
    munit_assert_ptr_equal(result, dummy);
    return MUNIT_OK;
}

/**
 * Spec:    docs/specs/core/world/chunk_generator_table.h.spec.md
 * Section: 1.4 Functions — get_default_chunk_generator_process
 *
 * Verifies that get_default_chunk_generator_process returns the
 * generator registered for Chunk_Generator_Kind__None.
 */
TEST_FUNCTION(chunk_generator_table__get_default__returns_none_slot) {
    Chunk_Generator_Table table;
    initialize_chunk_generator_table(&table);
    m_Process dummy = (m_Process)0xCAFEBABE;
    register_chunk_generator_into__chunk_generator_table(
        &table, Chunk_Generator_Kind__None, dummy);
    m_Process result = get_default_chunk_generator_process(&table);
    munit_assert_ptr_equal(result, dummy);
    return MUNIT_OK;
}

DEFINE_SUITE(chunk_generator_table,
    INCLUDE_TEST__STATELESS(chunk_generator_table__initialize__all_null),
    INCLUDE_TEST__STATELESS(chunk_generator_table__register_and_get),
    INCLUDE_TEST__STATELESS(chunk_generator_table__get_default__returns_none_slot),
    END_TESTS)
