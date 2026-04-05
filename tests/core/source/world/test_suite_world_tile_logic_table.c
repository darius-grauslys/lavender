#include <world/test_suite_world_tile_logic_table.h>

#include <world/tile_logic_table.c>

TEST_FUNCTION(tile_logic_table__initialize__zeroes_records) {
    Tile_Logic_Table table;
    initialize_tile_logic_table(&table);
    munit_assert_uint32(table.quantity_of__records, ==, 0);
    return MUNIT_OK;
}

TEST_FUNCTION(tile_logic_record__is_unpassable__false_by_default) {
    Tile_Logic_Record record;
    record.tile_logic_flags__u8 = 0;
    munit_assert_false(is_tile_logic_record__unpassable(&record));
    return MUNIT_OK;
}

TEST_FUNCTION(tile_logic_record__is_unpassable__true_when_set) {
    Tile_Logic_Record record;
    record.tile_logic_flags__u8 = TILE_LOGIC_FLAG__IS_UNPASSABLE;
    munit_assert_true(is_tile_logic_record__unpassable(&record));
    return MUNIT_OK;
}

TEST_FUNCTION(tile_logic_record__is_sight_blocking__false_by_default) {
    Tile_Logic_Record record;
    record.tile_logic_flags__u8 = 0;
    munit_assert_false(is_tile_logic_record__sight_blocking(&record));
    return MUNIT_OK;
}

TEST_FUNCTION(tile_logic_record__is_sight_blocking__true_when_set) {
    Tile_Logic_Record record;
    record.tile_logic_flags__u8 = TILE_LOGIC_FLAG__IS_SIGHT_BLOCKING;
    munit_assert_true(is_tile_logic_record__sight_blocking(&record));
    return MUNIT_OK;
}

TEST_FUNCTION(tile_logic_record__is_without_ground__false_by_default) {
    Tile_Logic_Record record;
    record.tile_logic_flags__u8 = 0;
    munit_assert_false(is_tile_logic_record__without_ground(&record));
    return MUNIT_OK;
}

TEST_FUNCTION(tile_logic_record__is_without_ground__true_when_set) {
    Tile_Logic_Record record;
    record.tile_logic_flags__u8 = TILE_LOGIC_FLAG__IS_WITHOUT_GROUND;
    munit_assert_true(is_tile_logic_record__without_ground(&record));
    return MUNIT_OK;
}

TEST_FUNCTION(tile_logic_record__multiple_flags) {
    Tile_Logic_Record record;
    record.tile_logic_flags__u8 =
        TILE_LOGIC_FLAG__IS_UNPASSABLE
        | TILE_LOGIC_FLAG__IS_SIGHT_BLOCKING;
    munit_assert_true(is_tile_logic_record__unpassable(&record));
    munit_assert_true(is_tile_logic_record__sight_blocking(&record));
    munit_assert_false(is_tile_logic_record__without_ground(&record));
    return MUNIT_OK;
}

DEFINE_SUITE(tile_logic_table,
    INCLUDE_TEST__STATELESS(tile_logic_table__initialize__zeroes_records),
    INCLUDE_TEST__STATELESS(tile_logic_record__is_unpassable__false_by_default),
    INCLUDE_TEST__STATELESS(tile_logic_record__is_unpassable__true_when_set),
    INCLUDE_TEST__STATELESS(tile_logic_record__is_sight_blocking__false_by_default),
    INCLUDE_TEST__STATELESS(tile_logic_record__is_sight_blocking__true_when_set),
    INCLUDE_TEST__STATELESS(tile_logic_record__is_without_ground__false_by_default),
    INCLUDE_TEST__STATELESS(tile_logic_record__is_without_ground__true_when_set),
    INCLUDE_TEST__STATELESS(tile_logic_record__multiple_flags),
    END_TESTS)
