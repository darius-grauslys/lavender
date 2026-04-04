#include <rendering/test_suite_rendering_sprite_manager.h>

#include <rendering/sprite_manager.c>

TEST_FUNCTION(sprite_manager__initialize__clears_state) {
    Sprite_Manager manager;
    memset(&manager, 0xFF, sizeof(manager));
    initialize_sprite_manager(&manager);
    munit_assert_ptr_null(manager.pM_pool_of__sprites);
    munit_assert_ptr_null(manager.pM_sprite_render_records);
    munit_assert_ptr_null(manager.p_sprite_render_record__last);
    munit_assert_uint32(manager.max_quantity_of__sprites, ==, 0);
    return MUNIT_OK;
}

TEST_FUNCTION(sprite_manager__allocate_members__succeeds_with_valid_quantity) {
    Sprite_Manager manager;
    initialize_sprite_manager(&manager);
    bool result = allocate_sprite_manager__members(&manager, 4);
    munit_assert_true(result);
    munit_assert_ptr_not_null(manager.pM_pool_of__sprites);
    munit_assert_ptr_not_null(manager.pM_sprite_render_records);
    munit_assert_uint32(manager.max_quantity_of__sprites, ==, 4);

    // Clean up
    free(manager.pM_pool_of__sprites);
    free(manager.pM_sprite_render_records);
    return MUNIT_OK;
}

TEST_FUNCTION(sprite_manager__allocate_members__sprites_are_deallocated) {
    Sprite_Manager manager;
    initialize_sprite_manager(&manager);
    bool result = allocate_sprite_manager__members(&manager, 4);
    munit_assert_true(result);

    for (Quantity__u32 i = 0; i < 4; i++) {
        munit_assert_true(is_sprite__deallocated(
            &manager.pM_pool_of__sprites[i]));
    }

    free(manager.pM_pool_of__sprites);
    free(manager.pM_sprite_render_records);
    return MUNIT_OK;
}

TEST_FUNCTION(sprite_manager__get_p_sprite_by__uuid__returns_null_when_empty) {
    Sprite_Manager manager;
    initialize_sprite_manager(&manager);
    allocate_sprite_manager__members(&manager, 4);

    Sprite *p_sprite =
        get_p_sprite_by__uuid_from__sprite_manager(&manager, 12345);
    munit_assert_ptr_null(p_sprite);

    free(manager.pM_pool_of__sprites);
    free(manager.pM_sprite_render_records);
    return MUNIT_OK;
}

DEFINE_SUITE(sprite_manager,
    INCLUDE_TEST__STATELESS(sprite_manager__initialize__clears_state),
    INCLUDE_TEST__STATELESS(sprite_manager__allocate_members__succeeds_with_valid_quantity),
    INCLUDE_TEST__STATELESS(sprite_manager__allocate_members__sprites_are_deallocated),
    INCLUDE_TEST__STATELESS(sprite_manager__get_p_sprite_by__uuid__returns_null_when_empty),
    END_TESTS)
