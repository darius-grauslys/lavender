# Specification: tests/templates/munit.h

## Overview

The µnit testing framework header (v0.4.1). Third-party library by Evan
Nemerson (MIT license). Copied into test trees by `update.sh`.

## Dependencies

- `<stdarg.h>`, `<stdlib.h>`, `<stdint.h>`, `<inttypes.h>`, `<string.h>`

## Types

### Integer Types

Maps `munit_int8_t` through `munit_uint64_t` to standard fixed-width types.
`munit_bool` maps to `bool`, `_Bool`, or `int`.

### Enumerations

| Enum | Values |
|------|--------|
| `MunitLogLevel` | `MUNIT_LOG_DEBUG`, `MUNIT_LOG_INFO`, `MUNIT_LOG_WARNING`, `MUNIT_LOG_ERROR` |
| `MunitResult` | `MUNIT_OK`, `MUNIT_FAIL`, `MUNIT_SKIP`, `MUNIT_ERROR` |
| `MunitTestOptions` | `MUNIT_TEST_OPTION_NONE`, `MUNIT_TEST_OPTION_SINGLE_ITERATION`, `MUNIT_TEST_OPTION_TODO` |
| `MunitSuiteOptions` | `MUNIT_SUITE_OPTION_NONE` |

### Structures

| Struct | Fields |
|--------|--------|
| `MunitParameterEnum` | `name`, `values` |
| `MunitParameter` | `name`, `value` |
| `MunitTest` | `name`, `test`, `setup`, `tear_down`, `options`, `parameters` |
| `MunitSuite` | `prefix`, `tests`, `suites`, `iterations`, `options` |
| `MunitArgument` | `name`, `parse_argument`, `write_help` |

### Function Pointer Types

| Type | Signature |
|------|-----------|
| `MunitTestFunc` | `MunitResult (*)(const MunitParameter[], void*)` |
| `MunitTestSetup` | `void* (*)(const MunitParameter[], void*)` |
| `MunitTestTearDown` | `void (*)(void*)` |

## Functions

### Logging

`munit_logf_ex`, `munit_logf`, `munit_log`, `munit_errorf_ex`,
`munit_errorf`, `munit_error`

### Assertions

Boolean: `munit_assert`, `munit_assert_true`, `munit_assert_false`

Typed: `munit_assert_char` through `munit_assert_ptr`, plus `int8`-`uint64`
variants.

Floating: `munit_assert_double_equal(a, b, precision)`

String/Memory: `munit_assert_string_equal`, `munit_assert_string_not_equal`,
`munit_assert_memory_equal`, `munit_assert_memory_not_equal`

Pointer: `munit_assert_ptr_equal`, `munit_assert_ptr_not_equal`,
`munit_assert_null`, `munit_assert_not_null`

### Memory

`munit_malloc_ex`, `munit_malloc`, `munit_new`, `munit_calloc`, `munit_newa`

### PRNG

`munit_rand_seed`, `munit_rand_uint32`, `munit_rand_int_range`,
`munit_rand_double`, `munit_rand_memory`

### Runner

`munit_suite_main`, `munit_suite_main_custom`, `munit_parameters_get`

## Assertion Aliases

When `MUNIT_ENABLE_ASSERT_ALIASES` is defined, provides `assert_true`,
`assert_int`, `assert_null`, etc. Also redefines `assert` to `munit_assert`.
