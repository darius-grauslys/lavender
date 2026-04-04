# Specification: tests/core/include/MAIN_TEST_SUITE__CORE_ANCIENTS_GAME.h

## Overview

Generated root test suite header. Aggregates all sub-suite header includes
and forward-declares the root suite inclusion function. Always regenerated.

## Includes

### Module Suite Headers

- `"test_suite_main.h"`
- `"test_suite_vectors.h"`
- `"test_suite_core_string.h"`
- `"test_suite_random.h"`
- `"test_suite_client.h"`
- `"test_suite_degree.h"`
- `"test_suite_game.h"`

### Directory Suite Headers

- `"input/MAIN_TEST_SUITE__CORE_INPUT.h"`
- `"rendering/MAIN_TEST_SUITE__CORE_RENDERING.h"`
- `"world/MAIN_TEST_SUITE__CORE_WORLD.h"`
- `"inventory/MAIN_TEST_SUITE__CORE_INVENTORY.h"`
- `"sort/MAIN_TEST_SUITE__CORE_SORT.h"`
- `"debug/MAIN_TEST_SUITE__CORE_DEBUG.h"`
- `"audio/MAIN_TEST_SUITE__CORE_AUDIO.h"`
- `"log/MAIN_TEST_SUITE__CORE_LOG.h"`
- `"serialization/MAIN_TEST_SUITE__CORE_SERIALIZATION.h"`
- `"game_action/MAIN_TEST_SUITE__CORE_GAME_ACTION.h"`
- `"entity/MAIN_TEST_SUITE__CORE_ENTITY.h"`
- `"ui/MAIN_TEST_SUITE__CORE_UI.h"`
- `"collisions/MAIN_TEST_SUITE__CORE_COLLISIONS.h"`
- `"util/MAIN_TEST_SUITE__CORE_UTIL.h"`
- `"multiplayer/MAIN_TEST_SUITE__CORE_MULTIPLAYER.h"`
- `"raycast/MAIN_TEST_SUITE__CORE_RAYCAST.h"`
- `"process/MAIN_TEST_SUITE__CORE_PROCESS.h"`
- `"scene/MAIN_TEST_SUITE__CORE_SCENE.h"`

### Framework

- `<test_util.h>`

## Declaration

    DECLARE_SUITE(CORE_ANCIENTS_GAME);

Expands to:

    void include_test_suite__CORE_ANCIENTS_GAME(MunitSuite *test_suite);
