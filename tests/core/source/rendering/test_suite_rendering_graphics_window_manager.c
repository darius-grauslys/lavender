#include <rendering/test_suite_rendering_graphics_window_manager.h>

#include <rendering/graphics_window_manager.c>

///
/// Spec: docs/specs/core/rendering/graphics_window_manager.h.spec.md
/// Section: 1.4.1 Initialization
///
TEST_FUNCTION(graphics_window_manager__initialize__all_windows_deallocated) {
    Graphics_Window_Manager manager;
    initialize_graphics_window_manager(&manager);
    for (Quantity__u32 i = 0; i < MAX_QUANTITY_OF__GRAPHICS_WINDOWS; i++) {
        munit_assert_false(
            is_graphics_window__allocated(&manager.graphics_windows[i]));
    }
    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/rendering/graphics_window_manager.h.spec.md
/// Section: 1.4.1 Initialization
///
TEST_FUNCTION(graphics_window_manager__initialize__sorted_array_cleared) {
    Graphics_Window_Manager manager;
    initialize_graphics_window_manager(&manager);
    for (Quantity__u32 i = 0; i < MAX_QUANTITY_OF__GRAPHICS_WINDOWS; i++) {
        munit_assert_ptr_null(
            manager.ptr_array_of__sorted_graphic_windows[i]);
    }
    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/rendering/graphics_window_manager.h.spec.md
/// Section: 1.4.5 Lookup
///
TEST_FUNCTION(graphics_window_manager__get_by_uuid__returns_null_when_empty) {
    Graphics_Window_Manager manager;
    initialize_graphics_window_manager(&manager);
    Graphics_Window *p_window =
        get_p_graphics_window_by__uuid_from__graphics_window_manager(
            &manager, 12345);
    munit_assert_ptr_null(p_window);
    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/rendering/graphics_window_manager.h.spec.md
/// Section: 1.4.3 Parent-Child
///
TEST_FUNCTION(graphics_window_manager__is_graphics_window_with__parent__false_after_init) {
    Graphics_Window_Manager manager;
    initialize_graphics_window_manager(&manager);
    // An unallocated window should not have a parent
    munit_assert_false(
        is_graphics_window_with__parent(&manager.graphics_windows[0]));
    return MUNIT_OK;
}

DEFINE_SUITE(graphics_window_manager,
    INCLUDE_TEST__STATELESS(graphics_window_manager__initialize__all_windows_deallocated),
    INCLUDE_TEST__STATELESS(graphics_window_manager__initialize__sorted_array_cleared),
    INCLUDE_TEST__STATELESS(graphics_window_manager__get_by_uuid__returns_null_when_empty),
    INCLUDE_TEST__STATELESS(graphics_window_manager__is_graphics_window_with__parent__false_after_init),
    END_TESTS)
