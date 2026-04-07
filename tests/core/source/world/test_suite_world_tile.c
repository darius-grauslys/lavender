#include <world/test_suite_world_tile.h>

#include <world/tile.c>

///
/// @spec    docs/specs/core/world/tile.h.spec.md
/// @section 1.4.3 Kind Accessors
///
TEST_FUNCTION(tile__set_and_get_tile_kind) {
    Tile tile;
    set_tile_kind_of__tile(&tile, Tile_Kind__None);
    munit_assert_int(get_tile_kind_from__tile(&tile), ==, Tile_Kind__None);
    return MUNIT_OK;
}

///
/// @spec    docs/specs/core/world/tile.h.spec.md
/// @section 1.4.3 Kind Accessors
///
TEST_FUNCTION(tile__is_tile_of__this_kind__returns_true_when_matching) {
    Tile tile;
    set_tile_kind_of__tile(&tile, Tile_Kind__None);
    munit_assert_true(is_tile_of__this_kind(&tile, Tile_Kind__None));
    return MUNIT_OK;
}

///
/// @spec    docs/specs/core/world/tile.h.spec.md
/// @section 1.4.3 Kind Accessors
///
TEST_FUNCTION(tile__is_tile_of__this_kind__returns_false_when_not_matching) {
    Tile tile;
    set_tile_kind_of__tile(&tile, Tile_Kind__None);
    munit_assert_false(is_tile_of__this_kind(&tile, Tile_Kind__Unknown));
    return MUNIT_OK;
}

///
/// @spec    docs/specs/core/world/tile.h.spec.md
/// @section 1.4.3 Kind Accessors
///
TEST_FUNCTION(tile__is_tile_kind__illegal__none_is_not_illegal) {
    munit_assert_false(is_tile_kind__illegal(Tile_Kind__None));
    return MUNIT_OK;
}

///
/// @spec    docs/specs/core/world/tile.h.spec.md
/// @section 1.4.3 Kind Accessors
///
TEST_FUNCTION(tile__is_tile_kind__illegal__unknown_is_illegal) {
    munit_assert_true(is_tile_kind__illegal(Tile_Kind__Unknown));
    return MUNIT_OK;
}

///
/// @spec    docs/specs/core/world/tile.h.spec.md
/// @section 1.4.1 Flag Queries
/// @section 1.4.2 Flag Mutations
///
TEST_FUNCTION(tile__set_tile__is_unpassable__true) {
    Tile_Flags__u8 flags = 0;
    set_tile__is_unpassable(&flags, true);
    munit_assert_true(is_tile__unpassable(flags));
    return MUNIT_OK;
}

///
/// @spec    docs/specs/core/world/tile.h.spec.md
/// @section 1.4.1 Flag Queries
/// @section 1.4.2 Flag Mutations
///
TEST_FUNCTION(tile__set_tile__is_unpassable__false) {
    Tile_Flags__u8 flags = 0;
    set_tile__is_unpassable(&flags, true);
    set_tile__is_unpassable(&flags, false);
    munit_assert_false(is_tile__unpassable(flags));
    return MUNIT_OK;
}

///
/// @spec    docs/specs/core/world/tile.h.spec.md
/// @section 1.4.1 Flag Queries
/// @section 1.4.2 Flag Mutations
///
TEST_FUNCTION(tile__set_tile__is_sight_blocking__true) {
    Tile_Flags__u8 flags = 0;
    set_tile__is_sight_blocking(&flags, true);
    munit_assert_true(is_tile__sight_blocking(flags));
    return MUNIT_OK;
}

///
/// @spec    docs/specs/core/world/tile.h.spec.md
/// @section 1.4.1 Flag Queries
/// @section 1.4.2 Flag Mutations
///
TEST_FUNCTION(tile__set_tile__is_sight_blocking__false) {
    Tile_Flags__u8 flags = 0;
    set_tile__is_sight_blocking(&flags, true);
    set_tile__is_sight_blocking(&flags, false);
    munit_assert_false(is_tile__sight_blocking(flags));
    return MUNIT_OK;
}

///
/// @spec    docs/specs/core/world/tile.h.spec.md
/// @section 1.5.3 Postconditions
///
TEST_FUNCTION(tile__flag_mutations_preserve_other_bits) {
    Tile_Flags__u8 flags = 0;
    set_tile__is_unpassable(&flags, true);
    set_tile__is_sight_blocking(&flags, true);
    munit_assert_true(is_tile__unpassable(flags));
    munit_assert_true(is_tile__sight_blocking(flags));
    set_tile__is_unpassable(&flags, false);
    munit_assert_false(is_tile__unpassable(flags));
    munit_assert_true(is_tile__sight_blocking(flags));
    return MUNIT_OK;
}

DEFINE_SUITE(tile,
    INCLUDE_TEST__STATELESS(tile__set_and_get_tile_kind),
    INCLUDE_TEST__STATELESS(tile__is_tile_of__this_kind__returns_true_when_matching),
    INCLUDE_TEST__STATELESS(tile__is_tile_of__this_kind__returns_false_when_not_matching),
    INCLUDE_TEST__STATELESS(tile__is_tile_kind__illegal__none_is_not_illegal),
    INCLUDE_TEST__STATELESS(tile__is_tile_kind__illegal__unknown_is_illegal),
    INCLUDE_TEST__STATELESS(tile__set_tile__is_unpassable__true),
    INCLUDE_TEST__STATELESS(tile__set_tile__is_unpassable__false),
    INCLUDE_TEST__STATELESS(tile__set_tile__is_sight_blocking__true),
    INCLUDE_TEST__STATELESS(tile__set_tile__is_sight_blocking__false),
    INCLUDE_TEST__STATELESS(tile__flag_mutations_preserve_other_bits),
    END_TESTS)
