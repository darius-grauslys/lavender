#include <rendering/test_suite_rendering_sprite.h>

#include <rendering/sprite.c>

TEST_FUNCTION(sprite__is_sprite__deallocated__returns_true_for_zeroed_sprite) {
    Sprite sprite;
    memset(&sprite, 0, sizeof(sprite));
    // A zeroed serialization header should indicate deallocated
    munit_assert_true(is_sprite__deallocated(&sprite));
    return MUNIT_OK;
}

TEST_FUNCTION(sprite__is_sprite__enabled__returns_false_when_flags_zero) {
    Sprite sprite;
    memset(&sprite, 0, sizeof(sprite));
    sprite.sprite_flags__u8 = 0;
    munit_assert_false(is_sprite__enabled(&sprite));
    return MUNIT_OK;
}

TEST_FUNCTION(sprite__set_sprite_as__enabled__sets_flag) {
    Sprite sprite;
    memset(&sprite, 0, sizeof(sprite));
    sprite.sprite_flags__u8 = 0;
    set_sprite_as__enabled(&sprite);
    munit_assert_true(is_sprite__enabled(&sprite));
    return MUNIT_OK;
}

TEST_FUNCTION(sprite__set_sprite_as__disabled__clears_flag) {
    Sprite sprite;
    memset(&sprite, 0, sizeof(sprite));
    sprite.sprite_flags__u8 = 0;
    set_sprite_as__enabled(&sprite);
    munit_assert_true(is_sprite__enabled(&sprite));
    set_sprite_as__disabled(&sprite);
    munit_assert_false(is_sprite__enabled(&sprite));
    return MUNIT_OK;
}

TEST_FUNCTION(sprite__is_sprite__needing_graphics_update__returns_false_initially) {
    Sprite sprite;
    memset(&sprite, 0, sizeof(sprite));
    sprite.sprite_flags__u8 = 0;
    munit_assert_false(is_sprite__needing_graphics_update(&sprite));
    return MUNIT_OK;
}

TEST_FUNCTION(sprite__set_sprite_as__needing_graphics_update__sets_flag) {
    Sprite sprite;
    memset(&sprite, 0, sizeof(sprite));
    sprite.sprite_flags__u8 = 0;
    set_sprite_as__needing_graphics_update(&sprite);
    munit_assert_true(is_sprite__needing_graphics_update(&sprite));
    return MUNIT_OK;
}

TEST_FUNCTION(sprite__set_sprite_as__NOT_needing_graphics_update__clears_flag) {
    Sprite sprite;
    memset(&sprite, 0, sizeof(sprite));
    sprite.sprite_flags__u8 = 0;
    set_sprite_as__needing_graphics_update(&sprite);
    set_sprite_as__NOT_needing_graphics_update(&sprite);
    munit_assert_false(is_sprite__needing_graphics_update(&sprite));
    return MUNIT_OK;
}

TEST_FUNCTION(sprite__is_sprite__flipped_x__returns_false_initially) {
    Sprite sprite;
    memset(&sprite, 0, sizeof(sprite));
    sprite.sprite_flags__u8 = 0;
    munit_assert_false(is_sprite__flipped_x(&sprite));
    return MUNIT_OK;
}

TEST_FUNCTION(sprite__set_sprite_as__flipped_x__sets_flag) {
    Sprite sprite;
    memset(&sprite, 0, sizeof(sprite));
    sprite.sprite_flags__u8 = 0;
    set_sprite_as__flipped_x(&sprite);
    munit_assert_true(is_sprite__flipped_x(&sprite));
    return MUNIT_OK;
}

TEST_FUNCTION(sprite__set_sprite_as__NOT_flipped_x__clears_flag) {
    Sprite sprite;
    memset(&sprite, 0, sizeof(sprite));
    sprite.sprite_flags__u8 = 0;
    set_sprite_as__flipped_x(&sprite);
    set_sprite_as__NOT_flipped_x(&sprite);
    munit_assert_false(is_sprite__flipped_x(&sprite));
    return MUNIT_OK;
}

TEST_FUNCTION(sprite__is_sprite__flipped_y__returns_false_initially) {
    Sprite sprite;
    memset(&sprite, 0, sizeof(sprite));
    sprite.sprite_flags__u8 = 0;
    munit_assert_false(is_sprite__flipped_y(&sprite));
    return MUNIT_OK;
}

TEST_FUNCTION(sprite__set_sprite_as__flipped_y__sets_flag) {
    Sprite sprite;
    memset(&sprite, 0, sizeof(sprite));
    sprite.sprite_flags__u8 = 0;
    set_sprite_as__flipped_y(&sprite);
    munit_assert_true(is_sprite__flipped_y(&sprite));
    return MUNIT_OK;
}

TEST_FUNCTION(sprite__set_sprite_as__NOT_flipped_y__clears_flag) {
    Sprite sprite;
    memset(&sprite, 0, sizeof(sprite));
    sprite.sprite_flags__u8 = 0;
    set_sprite_as__flipped_y(&sprite);
    set_sprite_as__NOT_flipped_y(&sprite);
    munit_assert_false(is_sprite__flipped_y(&sprite));
    return MUNIT_OK;
}

TEST_FUNCTION(sprite__flags_are_independent) {
    Sprite sprite;
    memset(&sprite, 0, sizeof(sprite));
    sprite.sprite_flags__u8 = 0;

    set_sprite_as__enabled(&sprite);
    set_sprite_as__flipped_x(&sprite);
    set_sprite_as__flipped_y(&sprite);
    set_sprite_as__needing_graphics_update(&sprite);

    munit_assert_true(is_sprite__enabled(&sprite));
    munit_assert_true(is_sprite__flipped_x(&sprite));
    munit_assert_true(is_sprite__flipped_y(&sprite));
    munit_assert_true(is_sprite__needing_graphics_update(&sprite));

    set_sprite_as__disabled(&sprite);
    munit_assert_false(is_sprite__enabled(&sprite));
    munit_assert_true(is_sprite__flipped_x(&sprite));
    munit_assert_true(is_sprite__flipped_y(&sprite));
    munit_assert_true(is_sprite__needing_graphics_update(&sprite));

    set_sprite_as__NOT_flipped_x(&sprite);
    munit_assert_false(is_sprite__enabled(&sprite));
    munit_assert_false(is_sprite__flipped_x(&sprite));
    munit_assert_true(is_sprite__flipped_y(&sprite));
    munit_assert_true(is_sprite__needing_graphics_update(&sprite));
    return MUNIT_OK;
}

TEST_FUNCTION(sprite__get_p_sprite_animation_from__sprite__returns_embedded_animation) {
    Sprite sprite;
    memset(&sprite, 0, sizeof(sprite));
    Sprite_Animation *p_anim = get_p_sprite_animation_from__sprite(&sprite);
    munit_assert_ptr_not_null(p_anim);
    munit_assert_ptr_equal(p_anim, &sprite.animation);
    return MUNIT_OK;
}

TEST_FUNCTION(sprite__set_frame_index__marks_needing_update) {
    Sprite sprite;
    memset(&sprite, 0, sizeof(sprite));
    sprite.sprite_flags__u8 = 0;
    munit_assert_false(is_sprite__needing_graphics_update(&sprite));
    set_frame_index_of__sprite(&sprite, 5);
    munit_assert_uint16(sprite.index_of__sprite_frame, ==, 5);
    munit_assert_true(is_sprite__needing_graphics_update(&sprite));
    return MUNIT_OK;
}

DEFINE_SUITE(sprite,
    INCLUDE_TEST__STATELESS(sprite__is_sprite__deallocated__returns_true_for_zeroed_sprite),
    INCLUDE_TEST__STATELESS(sprite__is_sprite__enabled__returns_false_when_flags_zero),
    INCLUDE_TEST__STATELESS(sprite__set_sprite_as__enabled__sets_flag),
    INCLUDE_TEST__STATELESS(sprite__set_sprite_as__disabled__clears_flag),
    INCLUDE_TEST__STATELESS(sprite__is_sprite__needing_graphics_update__returns_false_initially),
    INCLUDE_TEST__STATELESS(sprite__set_sprite_as__needing_graphics_update__sets_flag),
    INCLUDE_TEST__STATELESS(sprite__set_sprite_as__NOT_needing_graphics_update__clears_flag),
    INCLUDE_TEST__STATELESS(sprite__is_sprite__flipped_x__returns_false_initially),
    INCLUDE_TEST__STATELESS(sprite__set_sprite_as__flipped_x__sets_flag),
    INCLUDE_TEST__STATELESS(sprite__set_sprite_as__NOT_flipped_x__clears_flag),
    INCLUDE_TEST__STATELESS(sprite__is_sprite__flipped_y__returns_false_initially),
    INCLUDE_TEST__STATELESS(sprite__set_sprite_as__flipped_y__sets_flag),
    INCLUDE_TEST__STATELESS(sprite__set_sprite_as__NOT_flipped_y__clears_flag),
    INCLUDE_TEST__STATELESS(sprite__flags_are_independent),
    INCLUDE_TEST__STATELESS(sprite__get_p_sprite_animation_from__sprite__returns_embedded_animation),
    INCLUDE_TEST__STATELESS(sprite__set_frame_index__marks_needing_update),
    END_TESTS)
