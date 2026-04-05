#include <world/implemented/test_suite_world_implemented_tile_logic_table_registrar.h>

#include <world/implemented/tile_logic_table_registrar.c>
#include <world/tile_logic_table.h>

TEST_FUNCTION(tile_logic_table_registrar__register_does_not_crash) {
    Tile_Logic_Table table;
    initialize_tile_logic_table(&table);
    register_tile_logic_tables(0, &table);
    return MUNIT_OK;
}

DEFINE_SUITE(tile_logic_table_registrar,
    INCLUDE_TEST__STATELESS(tile_logic_table_registrar__register_does_not_crash),
    END_TESTS)
