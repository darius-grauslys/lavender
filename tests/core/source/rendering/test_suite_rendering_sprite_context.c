#include <rendering/test_suite_rendering_sprite_context.h>

#include <rendering/sprite_context.c>

TEST_FUNCTION(sprite_context__initialize__clears_state) {
    Sprite_Context context;
    memset(&context, 0xFF, sizeof(context));
    initialize_sprite_context(&context);
    munit_assert_ptr_null(context.pM_sprite_managers);
    munit_assert_uint8(context.max_quantity_of__sprite_managers, ==, 0);
    munit_assert_false(is_sprite_managers_allocated_in__sprite_context(&context));
    return MUNIT_OK;
}

TEST_FUNCTION(sprite_context__is_sprite_managers_allocated__returns_false_after_init) {
    Sprite_Context context;
    initialize_sprite_context(&context);
    munit_assert_false(is_sprite_managers_allocated_in__sprite_context(&context));
    return MUNIT_OK;
}

TEST_FUNCTION(sprite_context__allocate_sprite_managers__succeeds) {
    Sprite_Context context;
    initialize_sprite_context(&context);
    bool result = allocate_sprite_managers_from__sprite_context(&context, 4);
    munit_assert_true(result);
    munit_assert_true(is_sprite_managers_allocated_in__sprite_context(&context));
    munit_assert_ptr_not_null(context.pM_sprite_managers);

    release_sprite_managers_from__sprite_context(&context);
    return MUNIT_OK;
}

TEST_FUNCTION(sprite_context__release_sprite_managers__clears_allocation) {
    Sprite_Context context;
    initialize_sprite_context(&context);
    allocate_sprite_managers_from__sprite_context(&context, 4);
    munit_assert_true(is_sprite_managers_allocated_in__sprite_context(&context));

    release_sprite_managers_from__sprite_context(&context);
    munit_assert_false(is_sprite_managers_allocated_in__sprite_context(&context));
    return MUNIT_OK;
}

TEST_FUNCTION(sprite_context__get_p_sprite_manager_by__uuid__returns_null_when_not_found) {
    Sprite_Context context;
    initialize_sprite_context(&context);
    allocate_sprite_managers_from__sprite_context(&context, 4);

    Sprite_Manager *p_mgr =
        get_p_sprite_manager_by__uuid_from__sprite_context(&context, 99999);
    munit_assert_ptr_null(p_mgr);

    release_sprite_managers_from__sprite_context(&context);
    return MUNIT_OK;
}

DEFINE_SUITE(sprite_context,
    INCLUDE_TEST__STATELESS(sprite_context__initialize__clears_state),
    INCLUDE_TEST__STATELESS(sprite_context__is_sprite_managers_allocated__returns_false_after_init),
    INCLUDE_TEST__STATELESS(sprite_context__allocate_sprite_managers__succeeds),
    INCLUDE_TEST__STATELESS(sprite_context__release_sprite_managers__clears_allocation),
    INCLUDE_TEST__STATELESS(sprite_context__get_p_sprite_manager_by__uuid__returns_null_when_not_found),
    END_TESTS)
