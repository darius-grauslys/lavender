#include <ui/test_suite_ui_ui_context.h>

#include <ui/ui_context.c>

TEST_FUNCTION(initialize_ui_context__clears_all_managers) {
    UI_Context ui_context;
    initialize_ui_context(&ui_context);
    for (int i = 0; i < MAX_QUANTITY_OF__UI_MANAGERS; i++) {
        munit_assert_ptr_null(
                ui_context.ui_managers[i].pM_ui_element_pool);
        munit_assert_ptr_null(
                ui_context.ui_managers[i].pM_ptr_array_of__ui_elements);
    }
    return MUNIT_OK;
}

DEFINE_SUITE(ui_context,
    INCLUDE_TEST__STATELESS(initialize_ui_context__clears_all_managers),
    END_TESTS)
