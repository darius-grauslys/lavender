#include <ui/test_suite_ui_ui_tile.h>

#include <ui/ui_tile.c>

///
/// @spec    docs/specs/core/ui/ui_tile.h.spec.md
/// @section 5.4.1 Initialization
///
TEST_FUNCTION(initialize_ui_tile_as__empty__sets_none_kind) {
    UI_Tile ui_tile;
    initialize_ui_tile_as__empty(&ui_tile);
    munit_assert_int(ui_tile.the_kind_of__ui_tile, ==, UI_Tile_Kind__None);
    munit_assert_int(ui_tile.ui_tile_flags, ==, 0);
    return MUNIT_OK;
}

///
/// @spec    docs/specs/core/ui/ui_tile.h.spec.md
/// @section 5.4.1 Initialization
///
TEST_FUNCTION(initialize_ui_tile__sets_kind_and_flags) {
    UI_Tile ui_tile;
    initialize_ui_tile(
            &ui_tile,
            (UI_Tile_Kind)42,
            UI_TILE_FLAG__FLIPPED_HORIZONTAL);
    munit_assert_int(ui_tile.the_kind_of__ui_tile, ==, 42);
    munit_assert_uint16(
            ui_tile.ui_tile_flags & UI_TILE_FLAG__FLIPPED_HORIZONTAL,
            !=, 0);
    return MUNIT_OK;
}

///
/// @spec    docs/specs/core/ui/ui_tile.h.spec.md
/// @section 5.4.3 Flip Mutations
///
TEST_FUNCTION(set_ui_tile_as__flipped_horizontally__sets_flag) {
    UI_Tile ui_tile;
    initialize_ui_tile_as__empty(&ui_tile);
    set_ui_tile_as__flipped_horizontally(&ui_tile);
    munit_assert_uint16(
            ui_tile.ui_tile_flags & UI_TILE_FLAG__FLIPPED_HORIZONTAL,
            !=, 0);
    return MUNIT_OK;
}

///
/// @spec    docs/specs/core/ui/ui_tile.h.spec.md
/// @section 5.4.3 Flip Mutations
///
TEST_FUNCTION(set_ui_tile_as__unflipped_horizontally__clears_flag) {
    UI_Tile ui_tile;
    initialize_ui_tile(
            &ui_tile,
            UI_Tile_Kind__None,
            UI_TILE_FLAG__FLIPPED_HORIZONTAL);
    set_ui_tile_as__unflipped_horizontally(&ui_tile);
    munit_assert_uint16(
            ui_tile.ui_tile_flags & UI_TILE_FLAG__FLIPPED_HORIZONTAL,
            ==, 0);
    return MUNIT_OK;
}

///
/// @spec    docs/specs/core/ui/ui_tile.h.spec.md
/// @section 5.4.3 Flip Mutations
///
TEST_FUNCTION(set_ui_tile_as__flipped_vertically__sets_flag) {
    UI_Tile ui_tile;
    initialize_ui_tile_as__empty(&ui_tile);
    set_ui_tile_as__flipped_vertically(&ui_tile);
    munit_assert_uint16(
            ui_tile.ui_tile_flags & UI_TILE_FLAG__FLIPPED_VERTICAL,
            !=, 0);
    return MUNIT_OK;
}

///
/// @spec    docs/specs/core/ui/ui_tile.h.spec.md
/// @section 5.4.3 Flip Mutations
///
TEST_FUNCTION(set_ui_tile_as__unflipped_vertically__clears_flag) {
    UI_Tile ui_tile;
    initialize_ui_tile(
            &ui_tile,
            UI_Tile_Kind__None,
            UI_TILE_FLAG__FLIPPED_VERTICAL);
    set_ui_tile_as__unflipped_vertically(&ui_tile);
    munit_assert_uint16(
            ui_tile.ui_tile_flags & UI_TILE_FLAG__FLIPPED_VERTICAL,
            ==, 0);
    return MUNIT_OK;
}

///
/// @spec    docs/specs/core/ui/ui_tile.h.spec.md
/// @section 5.4.4 Scale Mutations
///
TEST_FUNCTION(set_ui_tile_as__scaling_horizontally__sets_flag) {
    UI_Tile ui_tile;
    initialize_ui_tile_as__empty(&ui_tile);
    set_ui_tile_as__scaling_horizontally(&ui_tile);
    munit_assert_uint16(
            ui_tile.ui_tile_flags & UI_TILE_FLAG__SCALE_HORIZONTAL,
            !=, 0);
    return MUNIT_OK;
}

///
/// @spec    docs/specs/core/ui/ui_tile.h.spec.md
/// @section 5.4.4 Scale Mutations
///
TEST_FUNCTION(set_ui_tile_as__not_scaling_horizontally__clears_flag) {
    UI_Tile ui_tile;
    initialize_ui_tile(
            &ui_tile,
            UI_Tile_Kind__None,
            UI_TILE_FLAG__SCALE_HORIZONTAL);
    set_ui_tile_as__not_scaling_horizontally(&ui_tile);
    munit_assert_uint16(
            ui_tile.ui_tile_flags & UI_TILE_FLAG__SCALE_HORIZONTAL,
            ==, 0);
    return MUNIT_OK;
}

///
/// @spec    docs/specs/core/ui/ui_tile.h.spec.md
/// @section 5.4.4 Scale Mutations
///
TEST_FUNCTION(set_ui_tile_as__scaling_vertically__sets_flag) {
    UI_Tile ui_tile;
    initialize_ui_tile_as__empty(&ui_tile);
    set_ui_tile_as__scaling_vertically(&ui_tile);
    munit_assert_uint16(
            ui_tile.ui_tile_flags & UI_TILE_FLAG__SCALE_VERTICAL,
            !=, 0);
    return MUNIT_OK;
}

///
/// @spec    docs/specs/core/ui/ui_tile.h.spec.md
/// @section 5.4.4 Scale Mutations
///
TEST_FUNCTION(set_ui_tile_as__not_scaling_vertically__clears_flag) {
    UI_Tile ui_tile;
    initialize_ui_tile(
            &ui_tile,
            UI_Tile_Kind__None,
            UI_TILE_FLAG__SCALE_VERTICAL);
    set_ui_tile_as__not_scaling_vertically(&ui_tile);
    munit_assert_uint16(
            ui_tile.ui_tile_flags & UI_TILE_FLAG__SCALE_VERTICAL,
            ==, 0);
    return MUNIT_OK;
}

///
/// @spec    docs/specs/core/ui/ui_tile.h.spec.md
/// @section 5.4.2 Conversion
///
TEST_FUNCTION(get_ui_tile_raw_from__ui_tile__packs_kind_in_lower_bits) {
    UI_Tile ui_tile;
    initialize_ui_tile(
            &ui_tile,
            (UI_Tile_Kind)7,
            0);
    UI_Tile_Raw raw = get_ui_tile_raw_from__ui_tile(&ui_tile);
    munit_assert_uint16(raw & 0x3FF, ==, 7);
    return MUNIT_OK;
}

///
/// @spec    docs/specs/core/ui/ui_tile.h.spec.md
/// @section 5.5.3 Postconditions
///
TEST_FUNCTION(flag_mutations__preserve_other_flags) {
    UI_Tile ui_tile;
    initialize_ui_tile(
            &ui_tile,
            (UI_Tile_Kind)100,
            UI_TILE_FLAG__FLIPPED_HORIZONTAL);
    set_ui_tile_as__flipped_vertically(&ui_tile);
    munit_assert_uint16(
            ui_tile.ui_tile_flags & UI_TILE_FLAG__FLIPPED_HORIZONTAL,
            !=, 0);
    munit_assert_uint16(
            ui_tile.ui_tile_flags & UI_TILE_FLAG__FLIPPED_VERTICAL,
            !=, 0);
    munit_assert_int(ui_tile.the_kind_of__ui_tile, ==, 100);
    return MUNIT_OK;
}

DEFINE_SUITE(ui_tile,
    INCLUDE_TEST__STATELESS(initialize_ui_tile_as__empty__sets_none_kind),
    INCLUDE_TEST__STATELESS(initialize_ui_tile__sets_kind_and_flags),
    INCLUDE_TEST__STATELESS(set_ui_tile_as__flipped_horizontally__sets_flag),
    INCLUDE_TEST__STATELESS(set_ui_tile_as__unflipped_horizontally__clears_flag),
    INCLUDE_TEST__STATELESS(set_ui_tile_as__flipped_vertically__sets_flag),
    INCLUDE_TEST__STATELESS(set_ui_tile_as__unflipped_vertically__clears_flag),
    INCLUDE_TEST__STATELESS(set_ui_tile_as__scaling_horizontally__sets_flag),
    INCLUDE_TEST__STATELESS(set_ui_tile_as__not_scaling_horizontally__clears_flag),
    INCLUDE_TEST__STATELESS(set_ui_tile_as__scaling_vertically__sets_flag),
    INCLUDE_TEST__STATELESS(set_ui_tile_as__not_scaling_vertically__clears_flag),
    INCLUDE_TEST__STATELESS(get_ui_tile_raw_from__ui_tile__packs_kind_in_lower_bits),
    INCLUDE_TEST__STATELESS(flag_mutations__preserve_other_flags),
    END_TESTS)
