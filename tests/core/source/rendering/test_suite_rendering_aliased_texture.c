#include <rendering/test_suite_rendering_aliased_texture.h>

#include <rendering/aliased_texture.c>

///
/// Spec: docs/specs/core/rendering/aliased_texture.h.spec.md
/// Section: 1.4.1 Initialization — initialize_aliased_texture
///
TEST_FUNCTION(aliased_texture__initialize__clears_state) {
    Aliased_Texture aliased_texture;
    memset(&aliased_texture, 0xFF, sizeof(aliased_texture));
    initialize_aliased_texture(&aliased_texture);
    munit_assert_false(is_aliased_texture__used(&aliased_texture));
    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/rendering/aliased_texture.h.spec.md
/// Section: 1.4.3 Texture Access — is_aliased_texture__used
///
TEST_FUNCTION(aliased_texture__is_aliased_texture__used__returns_false_after_init) {
    Aliased_Texture aliased_texture;
    initialize_aliased_texture(&aliased_texture);
    munit_assert_false(is_aliased_texture__used(&aliased_texture));
    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/rendering/aliased_texture.h.spec.md
/// Section: 1.5.2 Preconditions — is_aliased_texture__used (null-safe)
///
TEST_FUNCTION(aliased_texture__is_aliased_texture__used__null_safe) {
    munit_assert_false(is_aliased_texture__used(0));
    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/rendering/aliased_texture.h.spec.md
/// Section: 1.4.2 Name Management — set_c_str_of__aliased_texture
///
TEST_FUNCTION(aliased_texture__set_c_str__sets_name) {
    Aliased_Texture aliased_texture;
    initialize_aliased_texture(&aliased_texture);
    set_c_str_of__aliased_texture(&aliased_texture, "test_texture");
    munit_assert_true(is_aliased_texture__used(&aliased_texture));
    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/rendering/aliased_texture.h.spec.md
/// Section: 1.4.2 Name Management — is_c_str_matching__aliased_texture
///
TEST_FUNCTION(aliased_texture__is_c_str_matching__returns_true_for_match) {
    Aliased_Texture aliased_texture;
    initialize_aliased_texture(&aliased_texture);
    set_c_str_of__aliased_texture(&aliased_texture, "my_texture");
    munit_assert_true(
        is_c_str_matching__aliased_texture(&aliased_texture, "my_texture"));
    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/rendering/aliased_texture.h.spec.md
/// Section: 1.4.2 Name Management — is_c_str_matching__aliased_texture
///
TEST_FUNCTION(aliased_texture__is_c_str_matching__returns_false_for_mismatch) {
    Aliased_Texture aliased_texture;
    initialize_aliased_texture(&aliased_texture);
    set_c_str_of__aliased_texture(&aliased_texture, "my_texture");
    munit_assert_false(
        is_c_str_matching__aliased_texture(&aliased_texture, "other_texture"));
    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/rendering/aliased_texture.h.spec.md
/// Section: 1.4.2 Name Management — is_c_str_matching__aliased_texture
///
TEST_FUNCTION(aliased_texture__is_c_str_matching__returns_false_when_empty) {
    Aliased_Texture aliased_texture;
    initialize_aliased_texture(&aliased_texture);
    munit_assert_false(
        is_c_str_matching__aliased_texture(&aliased_texture, "anything"));
    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/rendering/aliased_texture.h.spec.md
/// Section: 1.4.3 Texture Access — give_texture_to__aliased_texture,
///          get_texture_from__aliased_texture
///
TEST_FUNCTION(aliased_texture__give_and_get_texture__roundtrips) {
    Aliased_Texture aliased_texture;
    initialize_aliased_texture(&aliased_texture);

    Texture texture;
    texture.p_PLATFORM_texture = 0;
    texture.texture_flags = 0x12345678;

    give_texture_to__aliased_texture(&aliased_texture, &texture);
    Texture retrieved = get_texture_from__aliased_texture(&aliased_texture);
    munit_assert_uint32(retrieved.texture_flags, ==, 0x12345678);
    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/rendering/aliased_texture.h.spec.md
/// Section: 1.4.2 Name Management — set_c_str_of__aliased_texture,
///          is_c_str_matching__aliased_texture
///
TEST_FUNCTION(aliased_texture__set_c_str__overwrites_previous_name) {
    Aliased_Texture aliased_texture;
    initialize_aliased_texture(&aliased_texture);
    set_c_str_of__aliased_texture(&aliased_texture, "first_name");
    munit_assert_true(
        is_c_str_matching__aliased_texture(&aliased_texture, "first_name"));

    set_c_str_of__aliased_texture(&aliased_texture, "second_name");
    munit_assert_false(
        is_c_str_matching__aliased_texture(&aliased_texture, "first_name"));
    munit_assert_true(
        is_c_str_matching__aliased_texture(&aliased_texture, "second_name"));
    return MUNIT_OK;
}

DEFINE_SUITE(aliased_texture,
    INCLUDE_TEST__STATELESS(aliased_texture__initialize__clears_state),
    INCLUDE_TEST__STATELESS(aliased_texture__is_aliased_texture__used__returns_false_after_init),
    INCLUDE_TEST__STATELESS(aliased_texture__is_aliased_texture__used__null_safe),
    INCLUDE_TEST__STATELESS(aliased_texture__set_c_str__sets_name),
    INCLUDE_TEST__STATELESS(aliased_texture__is_c_str_matching__returns_true_for_match),
    INCLUDE_TEST__STATELESS(aliased_texture__is_c_str_matching__returns_false_for_mismatch),
    INCLUDE_TEST__STATELESS(aliased_texture__is_c_str_matching__returns_false_when_empty),
    INCLUDE_TEST__STATELESS(aliased_texture__give_and_get_texture__roundtrips),
    INCLUDE_TEST__STATELESS(aliased_texture__set_c_str__overwrites_previous_name),
    END_TESTS)
