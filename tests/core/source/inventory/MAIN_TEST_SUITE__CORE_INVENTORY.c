#include <inventory/MAIN_TEST_SUITE__CORE_INVENTORY.h>

INCLUDE_SUB_SUITES(CORE_INVENTORY, 9,
INCLUDE_SUITE(item_stack_manager),
INCLUDE_SUITE(container),
INCLUDE_SUITE(inventory_manager),
INCLUDE_SUITE(item_stack_allocation_specifier),
INCLUDE_SUITE(item_stack),
INCLUDE_SUITE(item_manager),
INCLUDE_SUITE(inventory),
INCLUDE_SUITE(item),NULL);

DEFINE_SUITE_WITH__SUB_SUITES(CORE_INVENTORY, END_TESTS);

