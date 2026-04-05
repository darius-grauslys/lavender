#include <world/implemented/test_suite_world_implemented_chunk_generator_registrar.h>

#include <world/implemented/chunk_generator_registrar.c>

TEST_FUNCTION(chunk_generator_registrar__register_does_not_crash) {
    Chunk_Generator_Table table;
    initialize_chunk_generator_table(&table);
    register_chunk_generators(&table);
    return MUNIT_OK;
}

DEFINE_SUITE(chunk_generator_registrar,
    INCLUDE_TEST__STATELESS(chunk_generator_registrar__register_does_not_crash),
    END_TESTS)
