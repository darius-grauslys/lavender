# System Overview: Test Utility Macros (test_util.h)

## Purpose

The `test_util.h` header provides a declarative macro DSL that wraps the µnit
testing framework's types (`MunitSuite`, `MunitTest`, `MunitTestFunc`, etc.)
into a consistent, concise interface for declaring test functions, registering
them into suites, and composing suites into hierarchies. It is the primary
interface that test authors interact with when writing and organizing tests.

Two copies exist:
- `tests/templates/test_util.h` — The template, copied into new test trees
  by `update.sh`. Does not include debug logging.
- `tests/test_util.h` — The live copy used by the active test tree. Includes
  `printf`-based debug logging in suite inclusion and a `test_log` helper.

## Architecture

### Macro Categories

    test_util.h
    ├── Test Name Generation
    │   ├── TEST_NAME(name)           -> MunitTestFunc_##name
    │   ├── TEST_NAME__SETUP(name)    -> setup__MunitTestFunc_##name
    │   └── TEST_NAME__CLEAN_UP(name) -> clean_up__MunitTestFunc_##name
    ├── Test Function Declaration
    │   ├── TEST_FUNCTION(name)
    │   ├── SETUP_TEST(name)
    │   └── CLEAN_UP_TEST(name)
    ├── Test Registration (MunitTest initializers)
    │   ├── INCLUDE_TEST(name, options, parameters)
    │   ├── INCLUDE_TEST__NO_PARAMETERS(name, options)
    │   ├── INCLUDE_TEST__BASIC(name)
    │   └── INCLUDE_TEST__STATELESS(name)
    ├── Suite Definition
    │   ├── DEFINE_SUITE(name, ...)
    │   └── DEFINE_SUITE_WITH__SUB_SUITES(name, ...)
    ├── Suite Composition
    │   ├── DECLARE_SUITE(name)
    │   ├── INCLUDE_SUITE(name)
    │   └── INCLUDE_SUB_SUITES(name, count, ...)
    ├── Sentinel Values
    │   ├── END_TESTS
    │   └── END_SUITES
    └── Utilities
        └── test_log(msg, ...)  [live copy only]

### Generated Symbol Naming

| Macro | Generated Symbol |
|-------|-----------------|
| `TEST_FUNCTION(foo)` | `MunitResult MunitTestFunc_foo(const MunitParameter params[], void* user_data_or_fixture)` |
| `SETUP_TEST(foo)` | `void* setup__MunitTestFunc_foo(const MunitParameter params[], void* user_data)` |
| `CLEAN_UP_TEST(foo)` | `void clean_up__MunitTestFunc_foo(void* fixture)` |
| `DEFINE_SUITE(bar, ...)` | `char *test_suite_bar__prefix`, `MunitTest test_suite_bar__tests[]`, `void include_test_suite__bar(MunitSuite*)` |
| `INCLUDE_SUB_SUITES(bar, N, ...)` | `MunitSuite test_suite_bar__sub_suites[N]`, `void include_sub_suites_for__bar(MunitSuite*)` |
| `DECLARE_SUITE(bar)` | `void include_test_suite__bar(MunitSuite *test_suite)` |
| `INCLUDE_SUITE(bar)` | `include_test_suite__bar` (bare function pointer) |

### Type Definitions

    typedef void (*f_test_suite_includer)(MunitSuite *test_suite);

Function pointer type for suite inclusion functions. Used by
`INCLUDE_SUB_SUITES` to iterate and invoke sub-suite includers.

## Differences Between Template and Live Copy

| Aspect | Template (`templates/test_util.h`) | Live (`tests/test_util.h`) |
|--------|-----------------------------------|---------------------------|
| Suite prefix format | `#name "_"` (trailing underscore) | `#name` (no trailing underscore) |
| Debug printf in DEFINE_SUITE | None | `printf("\t\tincluded suite: %s\n", ...)` |
| Debug printf in INCLUDE_SUB_SUITES | None | `printf("\tincluding %d %p\n", ...)` and `printf("\tBREAK\n")` |
| Debug printf in DEFINE_SUITE_WITH__SUB_SUITES | None | `printf("included MAIN suite: %s\n", ...)` |
| `test_log` function | Not present | Present (static inline) |
| `#include <stdio.h>` | Not present | Present |

## Integration with Code Generator

The `update_recursive.sh` script generates files that use these macros:

- **Generated headers** contain `DECLARE_SUITE(module_name)`.
- **Generated stub sources** contain `DEFINE_SUITE(module_name, END_TESTS)`.
- **Generated directory sources** contain `INCLUDE_SUB_SUITES(dir_name, count, ...)` and `DEFINE_SUITE_WITH__SUB_SUITES(dir_name, END_TESTS)`.
