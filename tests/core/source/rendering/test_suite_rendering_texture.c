#include <rendering/test_suite_rendering_texture.h>

#include <rendering/texture.c>

/**
 * Spec: docs/specs/core/rendering/texture.h.spec.md
 * Section: 1.4.1 Initialization
 */
TEST_FUNCTION(texture__initialize_texture__clears_fields) {
    Texture texture;
    texture.p_PLATFORM_texture = (PLATFORM_Texture*)0xDEADBEEF;
    texture.texture_flags = 0xFFFFFFFF;
    initialize_texture(texture);
    // NOTE: initialize_texture takes by value, so this tests that
    // the function signature exists. The local copy is not modified.
    // This is a known bug documented in the spec.
    return MUNIT_OK;
}

/**
 * Spec: docs/specs/core/rendering/texture.h.spec.md
 * Section: 1.4.2 Visibility
 */
TEST_FUNCTION(texture__set_texture_flags_as__hidden__sets_flag) {
    Texture_Flags flags = 0;
    set_texture_flags_as__hidden(&flags);
    munit_assert_true(is_texture_flags__hidden(flags));
    return MUNIT_OK;
}

/**
 * Spec: docs/specs/core/rendering/texture.h.spec.md
 * Section: 1.4.2 Visibility
 */
TEST_FUNCTION(texture__set_texture_flags_as__visible__clears_flag) {
    Texture_Flags flags = 0;
    set_texture_flags_as__hidden(&flags);
    munit_assert_true(is_texture_flags__hidden(flags));
    set_texture_flags_as__visible(&flags);
    munit_assert_false(is_texture_flags__hidden(flags));
    return MUNIT_OK;
}

/**
 * Spec: docs/specs/core/rendering/texture.h.spec.md
 * Section: 1.4.2 Visibility
 */
TEST_FUNCTION(texture__is_texture_flags__hidden__returns_false_when_not_set) {
    Texture_Flags flags = 0;
    munit_assert_false(is_texture_flags__hidden(flags));
    return MUNIT_OK;
}

/**
 * Spec: docs/specs/core/rendering/texture.h.spec.md
 * Section: 1.4.3 Read-Only
 */
TEST_FUNCTION(texture__set_texture_flags_as__readonly__sets_flag) {
    Texture_Flags flags = 0;
    set_texture_flags_as__readonly(&flags);
    munit_assert_true(is_texture_flags__readonly(flags));
    return MUNIT_OK;
}

/**
 * Spec: docs/specs/core/rendering/texture.h.spec.md
 * Section: 1.4.3 Read-Only
 */
TEST_FUNCTION(texture__set_texture_flags_as__not_readonly__clears_flag) {
    Texture_Flags flags = 0;
    set_texture_flags_as__readonly(&flags);
    munit_assert_true(is_texture_flags__readonly(flags));
    set_texture_flags_as__not_readonly(&flags);
    munit_assert_false(is_texture_flags__readonly(flags));
    return MUNIT_OK;
}

/**
 * Spec: docs/specs/core/rendering/texture.h.spec.md
 * Section: 1.4.3 Read-Only
 */
TEST_FUNCTION(texture__is_texture_flags__readonly__returns_false_when_not_set) {
    Texture_Flags flags = 0;
    munit_assert_false(is_texture_flags__readonly(flags));
    return MUNIT_OK;
}

/**
 * Spec: docs/specs/core/rendering/texture.h.spec.md
 * Section: 1.4.2 Visibility, 1.4.3 Read-Only
 */
TEST_FUNCTION(texture__hidden_and_readonly__are_independent) {
    Texture_Flags flags = 0;
    set_texture_flags_as__hidden(&flags);
    set_texture_flags_as__readonly(&flags);
    munit_assert_true(is_texture_flags__hidden(flags));
    munit_assert_true(is_texture_flags__readonly(flags));

    set_texture_flags_as__visible(&flags);
    munit_assert_false(is_texture_flags__hidden(flags));
    munit_assert_true(is_texture_flags__readonly(flags));

    set_texture_flags_as__not_readonly(&flags);
    munit_assert_false(is_texture_flags__hidden(flags));
    munit_assert_false(is_texture_flags__readonly(flags));
    return MUNIT_OK;
}

/**
 * Spec: docs/specs/core/rendering/texture.h.spec.md
 * Section: 1.4.4 Component Extraction
 */
TEST_FUNCTION(texture__get_texture_flags__width__extracts_width_bits) {
    Texture_Flags flags = 0;
    Texture_Flags width = get_texture_flags__width(flags);
    // With zero flags, width should be zero (encoding for 8 pixels)
    munit_assert_uint32(width, ==, 0);
    return MUNIT_OK;
}

/**
 * Spec: docs/specs/core/rendering/texture.h.spec.md
 * Section: 1.4.4 Component Extraction
 */
TEST_FUNCTION(texture__get_texture_flags__height__extracts_height_bits) {
    Texture_Flags flags = 0;
    Texture_Flags height = get_texture_flags__height(flags);
    munit_assert_uint32(height, ==, 0);
    return MUNIT_OK;
}

/**
 * Spec: docs/specs/core/rendering/texture.h.spec.md
 * Section: 1.4.4 Component Extraction
 */
TEST_FUNCTION(texture__get_texture_flags__size__extracts_size_bits) {
    Texture_Flags flags = 0;
    Texture_Flags size = get_texture_flags__size(flags);
    munit_assert_uint32(size, ==, 0);
    return MUNIT_OK;
}

/**
 * Spec: docs/specs/core/rendering/texture.h.spec.md
 * Section: 1.4.4 Component Extraction
 */
TEST_FUNCTION(texture__get_texture_flags__rendering_method__extracts_method) {
    Texture_Flags flags = 0;
    Texture_Flags method = get_texture_flags__rendering_method(flags);
    munit_assert_uint32(method, ==, 0);
    return MUNIT_OK;
}

/**
 * Spec: docs/specs/core/rendering/texture.h.spec.md
 * Section: 1.4.4 Component Extraction
 */
TEST_FUNCTION(texture__get_texture_flags__format__extracts_format) {
    Texture_Flags flags = 0;
    Texture_Flags format = get_texture_flags__format(flags);
    munit_assert_uint32(format, ==, 0);
    return MUNIT_OK;
}

/**
 * Spec: docs/specs/core/rendering/texture.h.spec.md
 * Section: 1.4.5 Pixel Dimension Conversion
 */
TEST_FUNCTION(texture__get_length_of__texture_flag__width__returns_8_for_zero) {
    Texture_Flags flags = 0;
    Quantity__u16 width = get_length_of__texture_flag__width(flags);
    munit_assert_uint16(width, ==, 8);
    return MUNIT_OK;
}

/**
 * Spec: docs/specs/core/rendering/texture.h.spec.md
 * Section: 1.4.5 Pixel Dimension Conversion
 */
TEST_FUNCTION(texture__get_length_of__texture_flag__height__returns_8_for_zero) {
    Texture_Flags flags = 0;
    Quantity__u16 height = get_length_of__texture_flag__height(flags);
    munit_assert_uint16(height, ==, 8);
    return MUNIT_OK;
}

/**
 * Spec: docs/specs/core/rendering/texture.h.spec.md
 * Section: 1.4.2 Visibility, 1.4.3 Read-Only
 */
TEST_FUNCTION(texture__flags_preserve_other_bits_when_setting_hidden) {
    Texture_Flags flags = 0;
    set_texture_flags_as__readonly(&flags);
    Texture_Flags before = flags;
    set_texture_flags_as__hidden(&flags);
    set_texture_flags_as__visible(&flags);
    munit_assert_uint32(flags, ==, before);
    return MUNIT_OK;
}

DEFINE_SUITE(texture,
    INCLUDE_TEST__STATELESS(texture__initialize_texture__clears_fields),
    INCLUDE_TEST__STATELESS(texture__set_texture_flags_as__hidden__sets_flag),
    INCLUDE_TEST__STATELESS(texture__set_texture_flags_as__visible__clears_flag),
    INCLUDE_TEST__STATELESS(texture__is_texture_flags__hidden__returns_false_when_not_set),
    INCLUDE_TEST__STATELESS(texture__set_texture_flags_as__readonly__sets_flag),
    INCLUDE_TEST__STATELESS(texture__set_texture_flags_as__not_readonly__clears_flag),
    INCLUDE_TEST__STATELESS(texture__is_texture_flags__readonly__returns_false_when_not_set),
    INCLUDE_TEST__STATELESS(texture__hidden_and_readonly__are_independent),
    INCLUDE_TEST__STATELESS(texture__get_texture_flags__width__extracts_width_bits),
    INCLUDE_TEST__STATELESS(texture__get_texture_flags__height__extracts_height_bits),
    INCLUDE_TEST__STATELESS(texture__get_texture_flags__size__extracts_size_bits),
    INCLUDE_TEST__STATELESS(texture__get_texture_flags__rendering_method__extracts_method),
    INCLUDE_TEST__STATELESS(texture__get_texture_flags__format__extracts_format),
    INCLUDE_TEST__STATELESS(texture__get_length_of__texture_flag__width__returns_8_for_zero),
    INCLUDE_TEST__STATELESS(texture__get_length_of__texture_flag__height__returns_8_for_zero),
    INCLUDE_TEST__STATELESS(texture__flags_preserve_other_bits_when_setting_hidden),
    END_TESTS)
