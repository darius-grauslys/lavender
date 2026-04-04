#include <rendering/test_suite_rendering_gfx_context.h>

#include <rendering/gfx_context.c>

TEST_FUNCTION(gfx_context__initialize__sets_platform_context_null) {
    Gfx_Context gfx_context;
    memset(&gfx_context, 0xFF, sizeof(gfx_context));
    initialize_gfx_context(&gfx_context);
    // After initialization, platform context pointer should be null
    // (it's set externally by platform init)
    munit_assert_ptr_null(
        get_p_PLATFORM_gfx_context_from__gfx_context(&gfx_context));
    return MUNIT_OK;
}

TEST_FUNCTION(gfx_context__get_p_aliased_texture_manager__returns_valid_ptr) {
    Gfx_Context gfx_context;
    initialize_gfx_context(&gfx_context);
    Aliased_Texture_Manager *p_mgr =
        get_p_aliased_texture_manager_from__gfx_context(&gfx_context);
    munit_assert_ptr_not_null(p_mgr);
    munit_assert_ptr_equal(p_mgr, &gfx_context.aliased_texture_manager);
    return MUNIT_OK;
}

TEST_FUNCTION(gfx_context__get_p_graphics_window_manager__returns_valid_ptr) {
    Gfx_Context gfx_context;
    initialize_gfx_context(&gfx_context);
    Graphics_Window_Manager *p_mgr =
        get_p_graphics_window_manager_from__gfx_context(&gfx_context);
    munit_assert_ptr_not_null(p_mgr);
    munit_assert_ptr_equal(p_mgr, &gfx_context.graphics_window_manager);
    return MUNIT_OK;
}

TEST_FUNCTION(gfx_context__get_p_font_manager__returns_valid_ptr) {
    Gfx_Context gfx_context;
    initialize_gfx_context(&gfx_context);
    Font_Manager *p_mgr =
        get_p_font_manager_from__gfx_context(&gfx_context);
    munit_assert_ptr_not_null(p_mgr);
    munit_assert_ptr_equal(p_mgr, &gfx_context.font_manager);
    return MUNIT_OK;
}

TEST_FUNCTION(gfx_context__get_p_sprite_context__returns_valid_ptr) {
    Gfx_Context gfx_context;
    initialize_gfx_context(&gfx_context);
    Sprite_Context *p_ctx =
        get_p_sprite_context_from__gfx_context(&gfx_context);
    munit_assert_ptr_not_null(p_ctx);
    munit_assert_ptr_equal(p_ctx, &gfx_context.sprite_context);
    return MUNIT_OK;
}

TEST_FUNCTION(gfx_context__get_p_ui_context__returns_valid_ptr) {
    Gfx_Context gfx_context;
    initialize_gfx_context(&gfx_context);
    UI_Context *p_ctx =
        get_p_ui_context_from__gfx_context(&gfx_context);
    munit_assert_ptr_not_null(p_ctx);
    munit_assert_ptr_equal(p_ctx, &gfx_context.ui_context);
    return MUNIT_OK;
}

TEST_FUNCTION(gfx_context__get_p_ui_tile_map_manager__returns_valid_ptr) {
    Gfx_Context gfx_context;
    initialize_gfx_context(&gfx_context);
    UI_Tile_Map_Manager *p_mgr =
        get_p_ui_tile_map_manager_from__gfx_context(&gfx_context);
    munit_assert_ptr_not_null(p_mgr);
    munit_assert_ptr_equal(p_mgr, &gfx_context.ui_tile_map_manager);
    return MUNIT_OK;
}

DEFINE_SUITE(gfx_context,
    INCLUDE_TEST__STATELESS(gfx_context__initialize__sets_platform_context_null),
    INCLUDE_TEST__STATELESS(gfx_context__get_p_aliased_texture_manager__returns_valid_ptr),
    INCLUDE_TEST__STATELESS(gfx_context__get_p_graphics_window_manager__returns_valid_ptr),
    INCLUDE_TEST__STATELESS(gfx_context__get_p_font_manager__returns_valid_ptr),
    INCLUDE_TEST__STATELESS(gfx_context__get_p_sprite_context__returns_valid_ptr),
    INCLUDE_TEST__STATELESS(gfx_context__get_p_ui_context__returns_valid_ptr),
    INCLUDE_TEST__STATELESS(gfx_context__get_p_ui_tile_map_manager__returns_valid_ptr),
    END_TESTS)
