#include <rendering/test_suite_rendering_graphics_window.h>

#include <rendering/graphics_window.c>

TEST_FUNCTION(graphics_window__initialize__clears_state) {
    Graphics_Window window;
    memset(&window, 0xFF, sizeof(window));
    initialize_graphics_window(&window);
    munit_assert_ptr_null(window.p_PLATFORM_gfx_window);
    munit_assert_ptr_null(window.p_camera);
    munit_assert_false(is_graphics_window__allocated(&window));
    return MUNIT_OK;
}

TEST_FUNCTION(graphics_window__is_allocated__returns_false_after_init) {
    Graphics_Window window;
    initialize_graphics_window(&window);
    munit_assert_false(is_graphics_window__allocated(&window));
    return MUNIT_OK;
}

TEST_FUNCTION(graphics_window__is_allocated__null_safe) {
    munit_assert_false(is_graphics_window__allocated(0));
    return MUNIT_OK;
}

TEST_FUNCTION(graphics_window__is_enabled__returns_false_after_init) {
    Graphics_Window window;
    initialize_graphics_window(&window);
    munit_assert_false(is_graphics_window__enabled(&window));
    return MUNIT_OK;
}

TEST_FUNCTION(graphics_window__set_enabled__sets_flag) {
    Graphics_Window window;
    initialize_graphics_window(&window);
    set_graphics_window_as__enabled(&window);
    munit_assert_true(is_graphics_window__enabled(&window));
    return MUNIT_OK;
}

TEST_FUNCTION(graphics_window__set_disabled__clears_flag) {
    Graphics_Window window;
    initialize_graphics_window(&window);
    set_graphics_window_as__enabled(&window);
    set_graphics_window_as__disabled(&window);
    munit_assert_false(is_graphics_window__enabled(&window));
    return MUNIT_OK;
}

TEST_FUNCTION(graphics_window__is_platform_provided__returns_false_after_init) {
    Graphics_Window window;
    initialize_graphics_window(&window);
    munit_assert_false(is_graphics_window__platform_provided(&window));
    return MUNIT_OK;
}

TEST_FUNCTION(graphics_window__set_platform_provided__sets_flag) {
    Graphics_Window window;
    initialize_graphics_window(&window);
    set_graphics_window_as__platform_provided(&window);
    munit_assert_true(is_graphics_window__platform_provided(&window));
    return MUNIT_OK;
}

TEST_FUNCTION(graphics_window__set_no_longer_platform_provided__clears_flag) {
    Graphics_Window window;
    initialize_graphics_window(&window);
    set_graphics_window_as__platform_provided(&window);
    set_graphics_window_as__no_longer__platform_provided(&window);
    munit_assert_false(is_graphics_window__platform_provided(&window));
    return MUNIT_OK;
}

TEST_FUNCTION(graphics_window__set_in_need_of_composition__sets_dirty_flag) {
    Graphics_Window window;
    initialize_graphics_window(&window);
    set_graphics_window_as__in_need_of__composition(&window);
    // The dirty flag should be set
    munit_assert_true(
        window.graphics_window__flags
        & GRAPHICS_WINDOW__FLAG__COMPOSE__DIRTY);
    return MUNIT_OK;
}

TEST_FUNCTION(graphics_window__enabled_and_platform_provided__are_independent) {
    Graphics_Window window;
    initialize_graphics_window(&window);

    set_graphics_window_as__enabled(&window);
    set_graphics_window_as__platform_provided(&window);
    munit_assert_true(is_graphics_window__enabled(&window));
    munit_assert_true(is_graphics_window__platform_provided(&window));

    set_graphics_window_as__disabled(&window);
    munit_assert_false(is_graphics_window__enabled(&window));
    munit_assert_true(is_graphics_window__platform_provided(&window));
    return MUNIT_OK;
}

TEST_FUNCTION(graphics_window__get_p_camera__returns_null_after_init) {
    Graphics_Window window;
    initialize_graphics_window(&window);
    Camera *p_cam = get_p_camera_from__graphics_window(&window);
    munit_assert_ptr_null(p_cam);
    return MUNIT_OK;
}

TEST_FUNCTION(graphics_window__set_and_get_camera__roundtrips) {
    Graphics_Window window;
    initialize_graphics_window(&window);
    Camera camera;
    memset(&camera, 0, sizeof(camera));
    set_p_camera_of__graphics_window(&window, &camera);
    Camera *p_cam = get_p_camera_from__graphics_window(&window);
    munit_assert_ptr_equal(p_cam, &camera);
    return MUNIT_OK;
}

TEST_FUNCTION(graphics_window__does_own_sprite_manager__false_after_init) {
    Graphics_Window window;
    initialize_graphics_window(&window);
    munit_assert_false(does_graphics_window_own_a__sprite_manager(&window));
    return MUNIT_OK;
}

TEST_FUNCTION(graphics_window__does_own_ui_manager__false_after_init) {
    Graphics_Window window;
    initialize_graphics_window(&window);
    munit_assert_false(does_graphics_window_own_a__ui_manager(&window));
    return MUNIT_OK;
}

TEST_FUNCTION(graphics_window__does_own_hitbox_manager__false_after_init) {
    Graphics_Window window;
    initialize_graphics_window(&window);
    munit_assert_false(does_graphics_window_own_a__hitbox_manager(&window));
    return MUNIT_OK;
}

TEST_FUNCTION(graphics_window__does_share_sprite_manager__false_after_init) {
    Graphics_Window window;
    initialize_graphics_window(&window);
    munit_assert_false(does_graphics_window_share_a__sprite_manager(&window));
    return MUNIT_OK;
}

TEST_FUNCTION(graphics_window__does_share_ui_manager__false_after_init) {
    Graphics_Window window;
    initialize_graphics_window(&window);
    munit_assert_false(does_graphics_window_share_a__ui_manager(&window));
    return MUNIT_OK;
}

TEST_FUNCTION(graphics_window__does_share_hitbox_manager__false_after_init) {
    Graphics_Window window;
    initialize_graphics_window(&window);
    munit_assert_false(does_graphics_window_share_a__hitbox_manager(&window));
    return MUNIT_OK;
}

DEFINE_SUITE(graphics_window,
    INCLUDE_TEST__STATELESS(graphics_window__initialize__clears_state),
    INCLUDE_TEST__STATELESS(graphics_window__is_allocated__returns_false_after_init),
    INCLUDE_TEST__STATELESS(graphics_window__is_allocated__null_safe),
    INCLUDE_TEST__STATELESS(graphics_window__is_enabled__returns_false_after_init),
    INCLUDE_TEST__STATELESS(graphics_window__set_enabled__sets_flag),
    INCLUDE_TEST__STATELESS(graphics_window__set_disabled__clears_flag),
    INCLUDE_TEST__STATELESS(graphics_window__is_platform_provided__returns_false_after_init),
    INCLUDE_TEST__STATELESS(graphics_window__set_platform_provided__sets_flag),
    INCLUDE_TEST__STATELESS(graphics_window__set_no_longer_platform_provided__clears_flag),
    INCLUDE_TEST__STATELESS(graphics_window__set_in_need_of_composition__sets_dirty_flag),
    INCLUDE_TEST__STATELESS(graphics_window__enabled_and_platform_provided__are_independent),
    INCLUDE_TEST__STATELESS(graphics_window__get_p_camera__returns_null_after_init),
    INCLUDE_TEST__STATELESS(graphics_window__set_and_get_camera__roundtrips),
    INCLUDE_TEST__STATELESS(graphics_window__does_own_sprite_manager__false_after_init),
    INCLUDE_TEST__STATELESS(graphics_window__does_own_ui_manager__false_after_init),
    INCLUDE_TEST__STATELESS(graphics_window__does_own_hitbox_manager__false_after_init),
    INCLUDE_TEST__STATELESS(graphics_window__does_share_sprite_manager__false_after_init),
    INCLUDE_TEST__STATELESS(graphics_window__does_share_ui_manager__false_after_init),
    INCLUDE_TEST__STATELESS(graphics_window__does_share_hitbox_manager__false_after_init),
    END_TESTS)
