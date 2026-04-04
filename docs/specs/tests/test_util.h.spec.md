# Specification: tests/test_util.h

## Overview

The live test utility macro header used by the active test tree. Provides
the declarative DSL for defining test functions, registering them into
suites, and composing suites into hierarchies. Includes diagnostic `printf`
output and a `test_log` utility not present in the template version.

## Dependencies

- `<munit.h>` (for `MunitSuite`, `MunitTest`, `MunitResult`,
  `MunitParameter`, `MunitTestOptions`, `MUNIT_TEST_OPTION_NONE`,
  `MUNIT_SUITE_OPTION_NONE`)
- `<stdio.h>` (for `printf`, `vprintf`)

## Include Guard

    #ifndef TEST_UTIL_H
    #define TEST_UTIL_H

## Types

### f_test_suite_includer

    typedef void (*f_test_suite_includer)(MunitSuite *test_suite);

## Macros

### Test Name Generation

| Macro | Expansion |
|-------|-----------|
| `TEST_NAME(name)` | `MunitTestFunc_##name` |
| `TEST_NAME__SETUP(name)` | `setup__MunitTestFunc_##name` |
| `TEST_NAME__CLEAN_UP(name)` | `clean_up__MunitTestFunc_##name` |

### Test Function Declaration

| Macro | Signature |
|-------|-----------|
| `TEST_FUNCTION(name)` | `MunitResult MunitTestFunc_<name>(const MunitParameter params[], void* user_data_or_fixture)` |
| `SETUP_TEST(name)` | `void* setup__MunitTestFunc_<name>(const MunitParameter params[], void* user_data)` |
| `CLEAN_UP_TEST(name)` | `void clean_up__MunitTestFunc_<name>(void* fixture)` |

### Test Registration

| Macro | Setup | Teardown | Options | Parameters |
|-------|-------|----------|---------|------------|
| `INCLUDE_TEST(name, opts, params)` | Yes | Yes | Custom | Custom |
| `INCLUDE_TEST__NO_PARAMETERS(name, opts)` | Yes | Yes | Custom | NULL |
| `INCLUDE_TEST__BASIC(name)` | Yes | Yes | NONE | NULL |
| `INCLUDE_TEST__STATELESS(name)` | NULL | NULL | NONE | NULL |

### Sentinel Values

| Macro | Expansion |
|-------|-----------|
| `END_TESTS` | `(MunitTest) { NULL, NULL, NULL, NULL, MUNIT_TEST_OPTION_NONE, NULL }` |
| `END_SUITES` | `(MunitSuite) { NULL, NULL, NULL, 0, MUNIT_SUITE_OPTION_NONE }` |

### Suite Declaration

| Macro | Expansion |
|-------|-----------|
| `DECLARE_SUITE(name)` | `void include_test_suite__##name(MunitSuite *test_suite);` |
| `INCLUDE_SUITE(name)` | `include_test_suite__##name` |

### Suite Definition

#### DEFINE_SUITE(name, ...)

Generates:
- `char *test_suite_<name>__prefix = "<name>";`
- `MunitTest test_suite_<name>__tests[] = { ..., END_TESTS };`
- `void include_test_suite__<name>(MunitSuite *test_suite)` which prints
  `"\t\tincluded suite: <name>\n"` and populates the suite with prefix,
  tests, iterations=1, options=NONE, suites=NULL.

#### INCLUDE_SUB_SUITES(name, count, ...)

Generates:
- `MunitSuite test_suite_<name>__sub_suites[count];`
- `void include_sub_suites_for__<name>(MunitSuite *test_suite)` which
  iterates `count` includers, printing `"\tincluding %d %p\n"` for each,
  breaking on NULL with `"\tBREAK\n"`, and sets `test_suite->suites`.

#### DEFINE_SUITE_WITH__SUB_SUITES(name, ...)

Same as `DEFINE_SUITE` but prints `"included MAIN suite: <name>\n"` and
calls `include_sub_suites_for__<name>(test_suite)`.

## Functions

### test_log

    static inline void test_log(const char *c_str__msg, ...);

Prints to stdout with ANSI formatting: `\033[37;1mTEST_LOG:\033[0m <msg>\n`.

## Preconditions

- `INCLUDE_SUB_SUITES` must appear before `DEFINE_SUITE_WITH__SUB_SUITES`
  for the same name.
- The `count` parameter must be >= the number of non-NULL entries.
- All macros must be used at file scope.
