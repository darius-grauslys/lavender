#include <ui/test_suite_ui_ui_tile_map_manager.h>

#include <ui/ui_tile_map_manager.c>

///
/// Spec:   docs/specs/core/ui/ui_tile_map_manager.h.spec.md
/// Tests:  §12.4 Functions — initialize_ui_tile_map_manager
///
TEST_FUNCTION(initialize_ui_tile_map_manager__all_deallocated) {
    UI_Tile_Map_Manager manager;
    initialize_ui_tile_map_manager(&manager);
    for (Quantity__u32 i = 0;
            i < UI_TILE_MAP__SMALL__MAX_QUANTITY_OF; i++) {
        munit_assert_false(
                is_ui_tile_map_flags__allocated(
                    manager.ui_tile_maps__small[i].ui_tile_map__flags));
    }
    for (Quantity__u32 i = 0;
            i < UI_TILE_MAP__MEDIUM__MAX_QUANTITY_OF; i++) {
        munit_assert_false(
                is_ui_tile_map_flags__allocated(
                    manager.ui_tile_maps__medium[i].ui_tile_map__flags));
    }
    for (Quantity__u32 i = 0;
            i < UI_TILE_MAP__LARGE__MAX_QUANTITY_OF; i++) {
        munit_assert_false(
                is_ui_tile_map_flags__allocated(
                    manager.ui_tile_maps__large[i].ui_tile_map__flags));
    }
    return MUNIT_OK;
}

///
/// Spec:   docs/specs/core/ui/ui_tile_map_manager.h.spec.md
/// Tests:  §12.4 Functions — allocate_ui_tile_map_with__ui_tile_map_manager
///
TEST_FUNCTION(allocate_ui_tile_map__small__returns_valid_wrapper) {
    UI_Tile_Map_Manager manager;
    initialize_ui_tile_map_manager(&manager);
    UI_Tile_Map__Wrapper wrapper =
        allocate_ui_tile_map_with__ui_tile_map_manager(
                &manager,
                UI_Tile_Map_Size__Small);
    munit_assert_true(is_ui_tile_map__wrapper_with__data(&wrapper));
    munit_assert_int(
            get_catagory_size_of__p_ui_tile_map__wrapper(&wrapper),
            ==,
            UI_Tile_Map_Size__Small);
    return MUNIT_OK;
}

///
/// Spec:   docs/specs/core/ui/ui_tile_map_manager.h.spec.md
/// Tests:  §12.4 Functions — allocate_ui_tile_map_with__ui_tile_map_manager
///
TEST_FUNCTION(allocate_ui_tile_map__medium__returns_valid_wrapper) {
    UI_Tile_Map_Manager manager;
    initialize_ui_tile_map_manager(&manager);
    UI_Tile_Map__Wrapper wrapper =
        allocate_ui_tile_map_with__ui_tile_map_manager(
                &manager,
                UI_Tile_Map_Size__Medium);
    munit_assert_true(is_ui_tile_map__wrapper_with__data(&wrapper));
    munit_assert_int(
            get_catagory_size_of__p_ui_tile_map__wrapper(&wrapper),
            ==,
            UI_Tile_Map_Size__Medium);
    return MUNIT_OK;
}

///
/// Spec:   docs/specs/core/ui/ui_tile_map_manager.h.spec.md
/// Tests:  §12.4 Functions — allocate_ui_tile_map_with__ui_tile_map_manager
///
TEST_FUNCTION(allocate_ui_tile_map__large__returns_valid_wrapper) {
    UI_Tile_Map_Manager manager;
    initialize_ui_tile_map_manager(&manager);
    UI_Tile_Map__Wrapper wrapper =
        allocate_ui_tile_map_with__ui_tile_map_manager(
                &manager,
                UI_Tile_Map_Size__Large);
    munit_assert_true(is_ui_tile_map__wrapper_with__data(&wrapper));
    munit_assert_int(
            get_catagory_size_of__p_ui_tile_map__wrapper(&wrapper),
            ==,
            UI_Tile_Map_Size__Large);
    return MUNIT_OK;
}

///
/// Spec:   docs/specs/core/ui/ui_tile_map_manager.h.spec.md
/// Tests:  §12.4 Functions — release_ui_tile_map_with__ui_tile_map_manager
///
TEST_FUNCTION(release_ui_tile_map__nullifies_wrapper_data) {
    UI_Tile_Map_Manager manager;
    initialize_ui_tile_map_manager(&manager);
    UI_Tile_Map__Wrapper wrapper =
        allocate_ui_tile_map_with__ui_tile_map_manager(
                &manager,
                UI_Tile_Map_Size__Small);
    munit_assert_true(is_ui_tile_map__wrapper_with__data(&wrapper));
    release_ui_tile_map_with__ui_tile_map_manager(
            &manager, &wrapper);
    munit_assert_false(is_ui_tile_map__wrapper_with__data(&wrapper));
    return MUNIT_OK;
}

///
/// Spec:   docs/specs/core/ui/ui_tile_map_manager.h.spec.md
/// Tests:  §12.4 Functions — allocate_ui_tile_map_with__ui_tile_map_manager
///
TEST_FUNCTION(allocate_ui_tile_map__exhaust_small_pool) {
    UI_Tile_Map_Manager manager;
    initialize_ui_tile_map_manager(&manager);
    UI_Tile_Map__Wrapper wrappers[UI_TILE_MAP__SMALL__MAX_QUANTITY_OF];
    for (Quantity__u32 i = 0;
            i < UI_TILE_MAP__SMALL__MAX_QUANTITY_OF; i++) {
        wrappers[i] =
            allocate_ui_tile_map_with__ui_tile_map_manager(
                    &manager,
                    UI_Tile_Map_Size__Small);
        munit_assert_true(
                is_ui_tile_map__wrapper_with__data(&wrappers[i]));
    }
    UI_Tile_Map__Wrapper exhausted =
        allocate_ui_tile_map_with__ui_tile_map_manager(
                &manager,
                UI_Tile_Map_Size__Small);
    munit_assert_false(is_ui_tile_map__wrapper_with__data(&exhausted));
    return MUNIT_OK;
}

///
/// Spec:   docs/specs/core/ui/ui_tile_map_manager.h.spec.md
/// Tests:  §12.4 Functions — release_ui_tile_map_with__ui_tile_map_manager,
///                            allocate_ui_tile_map_with__ui_tile_map_manager
///
TEST_FUNCTION(release_and_reallocate__small_tile_map) {
    UI_Tile_Map_Manager manager;
    initialize_ui_tile_map_manager(&manager);
    UI_Tile_Map__Wrapper wrapper =
        allocate_ui_tile_map_with__ui_tile_map_manager(
                &manager,
                UI_Tile_Map_Size__Small);
    release_ui_tile_map_with__ui_tile_map_manager(
            &manager, &wrapper);
    UI_Tile_Map__Wrapper wrapper2 =
        allocate_ui_tile_map_with__ui_tile_map_manager(
                &manager,
                UI_Tile_Map_Size__Small);
    munit_assert_true(is_ui_tile_map__wrapper_with__data(&wrapper2));
    return MUNIT_OK;
}

DEFINE_SUITE(ui_tile_map_manager,
    INCLUDE_TEST__STATELESS(initialize_ui_tile_map_manager__all_deallocated),
    INCLUDE_TEST__STATELESS(allocate_ui_tile_map__small__returns_valid_wrapper),
    INCLUDE_TEST__STATELESS(allocate_ui_tile_map__medium__returns_valid_wrapper),
    INCLUDE_TEST__STATELESS(allocate_ui_tile_map__large__returns_valid_wrapper),
    INCLUDE_TEST__STATELESS(release_ui_tile_map__nullifies_wrapper_data),
    INCLUDE_TEST__STATELESS(allocate_ui_tile_map__exhaust_small_pool),
    INCLUDE_TEST__STATELESS(release_and_reallocate__small_tile_map),
    END_TESTS)
