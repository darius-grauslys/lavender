#include <ui/test_suite_ui_ui_tile_map.h>

#include <ui/ui_tile_map.c>

///
/// Spec:   docs/specs/core/ui/ui_tile_map.h.spec.md
/// Section: 3.4.1 Initialization
///
TEST_FUNCTION(initialize_ui_tile_map__small_as__deallocated__zeroes_data) {
    UI_Tile_Map__Small small_map;
    memset(&small_map, 0xFF, sizeof(small_map));
    initialize_ui_tile_map__small_as__deallocated(&small_map);
    munit_assert_false(
            is_ui_tile_map_flags__allocated(
                small_map.ui_tile_map__flags));
    return MUNIT_OK;
}

///
/// Spec:   docs/specs/core/ui/ui_tile_map.h.spec.md
/// Section: 3.4.1 Initialization
///
TEST_FUNCTION(initialize_ui_tile_map__medium_as__deallocated__zeroes_data) {
    UI_Tile_Map__Medium medium_map;
    memset(&medium_map, 0xFF, sizeof(medium_map));
    initialize_ui_tile_map__medium_as__deallocated(&medium_map);
    munit_assert_false(
            is_ui_tile_map_flags__allocated(
                medium_map.ui_tile_map__flags));
    return MUNIT_OK;
}

///
/// Spec:   docs/specs/core/ui/ui_tile_map.h.spec.md
/// Section: 3.4.1 Initialization
///
TEST_FUNCTION(initialize_ui_tile_map__large_as__deallocated__zeroes_data) {
    UI_Tile_Map__Large large_map;
    memset(&large_map, 0xFF, sizeof(large_map));
    initialize_ui_tile_map__large_as__deallocated(&large_map);
    munit_assert_false(
            is_ui_tile_map_flags__allocated(
                large_map.ui_tile_map__flags));
    return MUNIT_OK;
}

///
/// Spec:   docs/specs/core/ui/ui_tile_map.h.spec.md
/// Section: 3.4.1 Initialization
///
TEST_FUNCTION(initialize_ui_tile_map__wrapper__sets_fields) {
    UI_Tile_Raw data[64];
    UI_Tile_Map__Wrapper wrapper;
    initialize_ui_tile_map__wrapper(
            &wrapper,
            data,
            8,
            8,
            UI_Tile_Map_Size__Small);
    munit_assert_ptr_equal(wrapper.p_ui_tile_data, data);
    munit_assert_uint32(
            get_width_of__p_ui_tile_map__wrapper(&wrapper),
            ==, 8);
    munit_assert_uint32(
            get_height_of__p_ui_tile_map__wrapper(&wrapper),
            ==, 8);
    munit_assert_int(
            get_catagory_size_of__p_ui_tile_map__wrapper(&wrapper),
            ==,
            UI_Tile_Map_Size__Small);
    return MUNIT_OK;
}

///
/// Spec:   docs/specs/core/ui/ui_tile_map.h.spec.md
/// Section: 3.4.4 Validation
///
TEST_FUNCTION(is_ui_tile_map__wrapper_with__data__true_when_non_null) {
    UI_Tile_Raw data[4];
    UI_Tile_Map__Wrapper wrapper;
    initialize_ui_tile_map__wrapper(
            &wrapper, data, 2, 2, UI_Tile_Map_Size__Small);
    munit_assert_true(is_ui_tile_map__wrapper_with__data(&wrapper));
    return MUNIT_OK;
}

///
/// Spec:   docs/specs/core/ui/ui_tile_map.h.spec.md
/// Section: 3.4.4 Validation
///
TEST_FUNCTION(is_ui_tile_map__wrapper_with__data__false_when_null) {
    UI_Tile_Map__Wrapper wrapper;
    initialize_ui_tile_map__wrapper(
            &wrapper, 0, 2, 2, UI_Tile_Map_Size__Small);
    munit_assert_false(is_ui_tile_map__wrapper_with__data(&wrapper));
    return MUNIT_OK;
}

///
/// Spec:   docs/specs/core/ui/ui_tile_map.h.spec.md
/// Section: 3.4.4 Validation
///
TEST_FUNCTION(is_ui_tile_map__wrapper_with__valid_size_catagory__valid) {
    UI_Tile_Map__Wrapper wrapper;
    UI_Tile_Raw data[4];
    initialize_ui_tile_map__wrapper(
            &wrapper, data, 2, 2, UI_Tile_Map_Size__Small);
    munit_assert_true(
            is_ui_tile_map__wrapper_with__valid_size_catagory(&wrapper));
    return MUNIT_OK;
}

///
/// Spec:   docs/specs/core/ui/ui_tile_map.h.spec.md
/// Section: 3.4.4 Validation
///
TEST_FUNCTION(is_ui_tile_map__wrapper_with__valid_size_catagory__invalid_none) {
    UI_Tile_Map__Wrapper wrapper;
    UI_Tile_Raw data[4];
    initialize_ui_tile_map__wrapper(
            &wrapper, data, 2, 2, UI_Tile_Map_Size__None);
    munit_assert_false(
            is_ui_tile_map__wrapper_with__valid_size_catagory(&wrapper));
    return MUNIT_OK;
}

///
/// Spec:   docs/specs/core/ui/ui_tile_map.h.spec.md
/// Section: 3.4.4 Validation
///
TEST_FUNCTION(is_ui_tile_map__wrapper_with__valid_size_catagory__invalid_unknown) {
    UI_Tile_Map__Wrapper wrapper;
    UI_Tile_Raw data[4];
    initialize_ui_tile_map__wrapper(
            &wrapper, data, 2, 2, UI_Tile_Map_Size__Unknown);
    munit_assert_false(
            is_ui_tile_map__wrapper_with__valid_size_catagory(&wrapper));
    return MUNIT_OK;
}

///
/// Spec:   docs/specs/core/ui/ui_tile_map.h.spec.md
/// Section: 3.4.4 Validation
///
TEST_FUNCTION(is_ui_tile_map__wrapper__valid__true_for_valid_wrapper) {
    UI_Tile_Raw data[16];
    UI_Tile_Map__Wrapper wrapper;
    initialize_ui_tile_map__wrapper(
            &wrapper, data, 4, 4, UI_Tile_Map_Size__Small);
    munit_assert_true(is_ui_tile_map__wrapper__valid(&wrapper));
    return MUNIT_OK;
}

///
/// Spec:   docs/specs/core/ui/ui_tile_map.h.spec.md
/// Section: 3.4.4 Validation
///
TEST_FUNCTION(is_ui_tile_map__wrapper__valid__false_for_null_data) {
    UI_Tile_Map__Wrapper wrapper;
    initialize_ui_tile_map__wrapper(
            &wrapper, 0, 4, 4, UI_Tile_Map_Size__Small);
    munit_assert_false(is_ui_tile_map__wrapper__valid(&wrapper));
    return MUNIT_OK;
}

///
/// Spec:   docs/specs/core/ui/ui_tile_map.h.spec.md
/// Section: 3.4.3 Flag Management
///
TEST_FUNCTION(ui_tile_map_flags__allocated_and_deallocated) {
    UI_Tile_Map__Flags flags = 0;
    munit_assert_false(is_ui_tile_map_flags__allocated(flags));
    set_ui_tile_map_flags_as__allocated(&flags);
    munit_assert_true(is_ui_tile_map_flags__allocated(flags));
    set_ui_tile_map_flags_as__deallocated(&flags);
    munit_assert_false(is_ui_tile_map_flags__allocated(flags));
    return MUNIT_OK;
}

///
/// Spec:   docs/specs/core/ui/ui_tile_map.h.spec.md
/// Section: 3.4.5 Construction
///
TEST_FUNCTION(ui_tile_map__small_to__wrapper__creates_valid_wrapper) {
    UI_Tile_Map__Small small_map;
    initialize_ui_tile_map__small_as__deallocated(&small_map);
    set_ui_tile_map_flags_as__allocated(&small_map.ui_tile_map__flags);
    UI_Tile_Map__Wrapper wrapper =
        ui_tile_map__small_to__ui_tile_map_wrapper(&small_map);
    munit_assert_true(is_ui_tile_map__wrapper_with__data(&wrapper));
    munit_assert_int(
            get_catagory_size_of__p_ui_tile_map__wrapper(&wrapper),
            ==,
            UI_Tile_Map_Size__Small);
    return MUNIT_OK;
}

///
/// Spec:   docs/specs/core/ui/ui_tile_map.h.spec.md
/// Section: 3.4.5 Construction
///
TEST_FUNCTION(ui_tile_map__medium_to__wrapper__creates_valid_wrapper) {
    UI_Tile_Map__Medium medium_map;
    initialize_ui_tile_map__medium_as__deallocated(&medium_map);
    set_ui_tile_map_flags_as__allocated(&medium_map.ui_tile_map__flags);
    UI_Tile_Map__Wrapper wrapper =
        ui_tile_map__medium_to__ui_tile_map_wrapper(&medium_map);
    munit_assert_true(is_ui_tile_map__wrapper_with__data(&wrapper));
    munit_assert_int(
            get_catagory_size_of__p_ui_tile_map__wrapper(&wrapper),
            ==,
            UI_Tile_Map_Size__Medium);
    return MUNIT_OK;
}

///
/// Spec:   docs/specs/core/ui/ui_tile_map.h.spec.md
/// Section: 3.4.5 Construction
///
TEST_FUNCTION(ui_tile_map__large_to__wrapper__creates_valid_wrapper) {
    UI_Tile_Map__Large large_map;
    initialize_ui_tile_map__large_as__deallocated(&large_map);
    set_ui_tile_map_flags_as__allocated(&large_map.ui_tile_map__flags);
    UI_Tile_Map__Wrapper wrapper =
        ui_tile_map__large_to__ui_tile_map_wrapper(&large_map);
    munit_assert_true(is_ui_tile_map__wrapper_with__data(&wrapper));
    munit_assert_int(
            get_catagory_size_of__p_ui_tile_map__wrapper(&wrapper),
            ==,
            UI_Tile_Map_Size__Large);
    return MUNIT_OK;
}

///
/// Spec:   docs/specs/core/ui/ui_tile_map.h.spec.md
/// Section: 3.4.2 Tile Map Operations
///
TEST_FUNCTION(fill_ui_tile_map__fills_all_tiles) {
    UI_Tile_Raw data[16];
    UI_Tile_Map__Wrapper wrapper;
    initialize_ui_tile_map__wrapper(
            &wrapper, data, 4, 4, UI_Tile_Map_Size__Small);
    UI_Tile fill_tile;
    initialize_ui_tile(&fill_tile, (UI_Tile_Kind)42, 0);
    fill_ui_tile_map(&wrapper, fill_tile);
    UI_Tile_Raw expected_raw = get_ui_tile_raw_from__ui_tile(&fill_tile);
    for (int i = 0; i < 16; i++) {
        munit_assert_uint16(data[i], ==, expected_raw);
    }
    return MUNIT_OK;
}

DEFINE_SUITE(ui_tile_map,
    INCLUDE_TEST__STATELESS(initialize_ui_tile_map__small_as__deallocated__zeroes_data),
    INCLUDE_TEST__STATELESS(initialize_ui_tile_map__medium_as__deallocated__zeroes_data),
    INCLUDE_TEST__STATELESS(initialize_ui_tile_map__large_as__deallocated__zeroes_data),
    INCLUDE_TEST__STATELESS(initialize_ui_tile_map__wrapper__sets_fields),
    INCLUDE_TEST__STATELESS(is_ui_tile_map__wrapper_with__data__true_when_non_null),
    INCLUDE_TEST__STATELESS(is_ui_tile_map__wrapper_with__data__false_when_null),
    INCLUDE_TEST__STATELESS(is_ui_tile_map__wrapper_with__valid_size_catagory__valid),
    INCLUDE_TEST__STATELESS(is_ui_tile_map__wrapper_with__valid_size_catagory__invalid_none),
    INCLUDE_TEST__STATELESS(is_ui_tile_map__wrapper_with__valid_size_catagory__invalid_unknown),
    INCLUDE_TEST__STATELESS(is_ui_tile_map__wrapper__valid__true_for_valid_wrapper),
    INCLUDE_TEST__STATELESS(is_ui_tile_map__wrapper__valid__false_for_null_data),
    INCLUDE_TEST__STATELESS(ui_tile_map_flags__allocated_and_deallocated),
    INCLUDE_TEST__STATELESS(ui_tile_map__small_to__wrapper__creates_valid_wrapper),
    INCLUDE_TEST__STATELESS(ui_tile_map__medium_to__wrapper__creates_valid_wrapper),
    INCLUDE_TEST__STATELESS(ui_tile_map__large_to__wrapper__creates_valid_wrapper),
    INCLUDE_TEST__STATELESS(fill_ui_tile_map__fills_all_tiles),
    END_TESTS)
