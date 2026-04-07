#include <rendering/font/test_suite_rendering_font_font_manager.h>

#include <rendering/font/font_manager.c>

/**
 * @spec    docs/specs/core/rendering/font/font_manager.h.spec.md
 * @section 1.4 Functions — initialize_font_manager
 *          "Initializes all font slots as deallocated."
 */
TEST_FUNCTION(font_manager__initialize__all_fonts_deallocated) {
    Font_Manager manager;
    initialize_font_manager(&manager);
    for (int i = 0; i < MAX_QUANTITY_OF__FONT; i++) {
        munit_assert_false(is_font__allocated(&manager.fonts[i]));
    }
    return MUNIT_OK;
}

/**
 * @spec    docs/specs/core/rendering/font/font_manager.h.spec.md
 * @section 1.4 Functions — allocate_font_from__font_manager
 *          "Allocates a font from the pool."
 */
TEST_FUNCTION(font_manager__allocate__returns_non_null) {
    Font_Manager manager;
    initialize_font_manager(&manager);
    Font *p_font = allocate_font_from__font_manager(&manager);
    munit_assert_ptr_not_null(p_font);
    munit_assert_true(is_font__allocated(p_font));
    return MUNIT_OK;
}

/**
 * @spec    docs/specs/core/rendering/font/font_manager.h.spec.md
 * @section 1.4 Functions — allocate_font_from__font_manager
 *          "Allocates a font from the pool."
 */
TEST_FUNCTION(font_manager__allocate__returns_different_fonts) {
    Font_Manager manager;
    initialize_font_manager(&manager);
    Font *p_font_1 = allocate_font_from__font_manager(&manager);
    Font *p_font_2 = allocate_font_from__font_manager(&manager);
    munit_assert_ptr_not_null(p_font_1);
    munit_assert_ptr_not_null(p_font_2);
    munit_assert_ptr_not_equal(p_font_1, p_font_2);
    return MUNIT_OK;
}

/**
 * @spec    docs/specs/core/rendering/font/font_manager.h.spec.md
 * @section 1.4 Functions — allocate_font_from__font_manager
 *          "Returns null if pool exhausted."
 */
TEST_FUNCTION(font_manager__allocate__returns_null_when_exhausted) {
    Font_Manager manager;
    initialize_font_manager(&manager);
    for (int i = 0; i < MAX_QUANTITY_OF__FONT; i++) {
        Font *p_font = allocate_font_from__font_manager(&manager);
        munit_assert_ptr_not_null(p_font);
    }
    Font *p_font_overflow = allocate_font_from__font_manager(&manager);
    munit_assert_ptr_null(p_font_overflow);
    return MUNIT_OK;
}

/**
 * @spec    docs/specs/core/rendering/font/font_manager.h.spec.md
 * @section 1.4 Functions — release_font_from__font_manager
 *          "Returns a font to the pool."
 */
TEST_FUNCTION(font_manager__release__allows_reallocation) {
    Font_Manager manager;
    initialize_font_manager(&manager);

    // Fill the pool
    Font *fonts[MAX_QUANTITY_OF__FONT];
    for (int i = 0; i < MAX_QUANTITY_OF__FONT; i++) {
        fonts[i] = allocate_font_from__font_manager(&manager);
        munit_assert_ptr_not_null(fonts[i]);
    }

    // Pool is full
    munit_assert_ptr_null(allocate_font_from__font_manager(&manager));

    // Release one
    release_font_from__font_manager(&manager, fonts[0]);
    munit_assert_false(is_font__allocated(fonts[0]));

    // Should be able to allocate again
    Font *p_font_new = allocate_font_from__font_manager(&manager);
    munit_assert_ptr_not_null(p_font_new);
    return MUNIT_OK;
}

/**
 * @spec    docs/specs/core/rendering/font/font_manager.h.spec.md
 * @section 1.4 Functions — release_font_from__font_manager
 *          "Returns a font to the pool."
 */
TEST_FUNCTION(font_manager__release__marks_font_as_deallocated) {
    Font_Manager manager;
    initialize_font_manager(&manager);
    Font *p_font = allocate_font_from__font_manager(&manager);
    munit_assert_true(is_font__allocated(p_font));
    release_font_from__font_manager(&manager, p_font);
    munit_assert_false(is_font__allocated(p_font));
    return MUNIT_OK;
}

DEFINE_SUITE(font_manager,
    INCLUDE_TEST__STATELESS(font_manager__initialize__all_fonts_deallocated),
    INCLUDE_TEST__STATELESS(font_manager__allocate__returns_non_null),
    INCLUDE_TEST__STATELESS(font_manager__allocate__returns_different_fonts),
    INCLUDE_TEST__STATELESS(font_manager__allocate__returns_null_when_exhausted),
    INCLUDE_TEST__STATELESS(font_manager__release__allows_reallocation),
    INCLUDE_TEST__STATELESS(font_manager__release__marks_font_as_deallocated),
    END_TESTS)
