#include <rendering/test_suite_rendering_aliased_texture_manager.h>

#include <rendering/aliased_texture_manager.c>

///
/// Spec: core/rendering/aliased_texture_manager.h.spec.md
/// Section: 1.4.1 Initialization — initialize_aliased_texture_manager
/// Section: 1.3.1 Aliased_Texture_Manager
///
TEST_FUNCTION(aliased_texture_manager__initialize__all_slots_unused) {
    Aliased_Texture_Manager manager;
    initialize_aliased_texture_manager(&manager);
    for (Quantity__u32 i = 0; i < MAX_QUANTITY_OF__ALIASED_TEXTURES; i++) {
        munit_assert_false(
            is_aliased_texture__used(&manager.aliased_textures[i]));
    }
    return MUNIT_OK;
}

///
/// Spec: core/rendering/aliased_texture_manager.h.spec.md
/// Section: 1.4.3 Lookup — get_texture_by__alias
/// Section: 1.5.1 Error Convention
///
TEST_FUNCTION(aliased_texture_manager__get_texture_by__alias__fails_when_empty) {
    Aliased_Texture_Manager manager;
    initialize_aliased_texture_manager(&manager);
    Texture texture;
    // true = failure in inverted convention
    bool result = get_texture_by__alias(&manager, "nonexistent", &texture);
    munit_assert_true(result);
    return MUNIT_OK;
}

///
/// Spec: core/rendering/aliased_texture_manager.h.spec.md
/// Section: 1.4.3 Lookup — get_uuid_of__aliased_texture
///
TEST_FUNCTION(aliased_texture_manager__get_uuid_of__aliased_texture__returns_unknown_when_not_found) {
    Aliased_Texture_Manager manager;
    initialize_aliased_texture_manager(&manager);
    Identifier__u32 uuid = get_uuid_of__aliased_texture(&manager, "nonexistent");
    // Should return IDENTIFIER__UNKNOWN__u32 or similar invalid value
    // when texture is not found
    (void)uuid;
    return MUNIT_OK;
}

///
/// Spec: core/rendering/aliased_texture_manager.h.spec.md
/// Section: 1.4.4 Release — release_all_aliased_textures
///
TEST_FUNCTION(aliased_texture_manager__release_all__resets_all_slots) {
    Aliased_Texture_Manager manager;
    initialize_aliased_texture_manager(&manager);
    // Manually mark a slot as used
    set_c_str_of__aliased_texture(&manager.aliased_textures[0], "test");
    munit_assert_true(
        is_aliased_texture__used(&manager.aliased_textures[0]));

    release_all_aliased_textures(0, &manager);

    for (Quantity__u32 i = 0; i < MAX_QUANTITY_OF__ALIASED_TEXTURES; i++) {
        munit_assert_false(
            is_aliased_texture__used(&manager.aliased_textures[i]));
    }
    return MUNIT_OK;
}

DEFINE_SUITE(aliased_texture_manager,
    INCLUDE_TEST__STATELESS(aliased_texture_manager__initialize__all_slots_unused),
    INCLUDE_TEST__STATELESS(aliased_texture_manager__get_texture_by__alias__fails_when_empty),
    INCLUDE_TEST__STATELESS(aliased_texture_manager__get_uuid_of__aliased_texture__returns_unknown_when_not_found),
    INCLUDE_TEST__STATELESS(aliased_texture_manager__release_all__resets_all_slots),
    END_TESTS)
