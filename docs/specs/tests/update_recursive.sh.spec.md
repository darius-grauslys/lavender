# Specification: tests/update_recursive.sh

## Overview

Recursive worker script for test code generation. Scans one directory level,
generates test suite headers/sources, and recurses into subdirectories.

## Dependencies

- Tools: `bash` 4+, `find`, `realpath`, `sed`, `printf`, `test`, `mkdir`

## Arguments

| # | Name | Description |
|---|------|-------------|
| 1 | `search_base_dir` | Root of source tree being scanned |
| 2 | `search_suffix` | Relative path from root (empty for top level) |
| 3 | `output_base_dir__include` | Test include output root |
| 4 | `output_base_dir__source` | Test source output root |
| 5 | `tree_name` | Uppercased tree identifier (e.g., `CORE`) |
| 6 | `exclusion_string` | `find -not -wholename` pattern |

## Naming

| Input | Output |
|-------|--------|
| Top level, tree=CORE | `CORE_ANCIENTS_GAME` / `MAIN_TEST_SUITE__CORE_ANCIENTS_GAME` |
| Subdir `world`, tree=CORE | `CORE_WORLD` / `MAIN_TEST_SUITE__CORE_WORLD` |
| File `game.c` | Suite name: `game`, files: `test_suite_game.{h,c}` |
| File `world/chunk.c` | Suite name: `chunk`, files: `test_suite_world_chunk.{h,c}` |

## Scanning

- Modules: `find $search_path -maxdepth 1 -type f -iname "*.c"`
- Subdirs: `find $search_path -mindepth 1 -maxdepth 1 -type d -not -wholename "$exclusion_string"`

## Generated Files

### Per Directory (always regenerated)

- Header: includes all module and subdir headers, then `DECLARE_SUITE`.
- Source: `INCLUDE_SUB_SUITES` + `DEFINE_SUITE_WITH__SUB_SUITES`.
- Count placeholder `__COUNT` replaced via `sed` after scanning.

### Per Module (only if missing)

- Header: `#include <test_util.h>` + `DECLARE_SUITE(module_name)`.
- Source: `#include` header, `#include` original `.c`, `#warning`,
  `DEFINE_SUITE(module_name, END_TESTS)`.

## Recursion

For each subdirectory, invokes itself with appended search suffix.
