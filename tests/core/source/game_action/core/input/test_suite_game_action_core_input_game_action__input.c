#include <game_action/core/input/test_suite_game_action_core_input_game_action__input.h>

#include <game_action/core/input/game_action__input.c>

/*
 * Spec: docs/specs/core/game_action/input/game_action__input.h.spec.md
 * Section: 1.4.1 Registration - register_game_action__input_for__server
 */
TEST(game_action__input, register_game_action__input_for__server) {
    FAIL("Not implemented");
}

/*
 * Spec: docs/specs/core/game_action/input/game_action__input.h.spec.md
 * Section: 1.4.1 Registration - register_game_action__input_for__client
 */
TEST(game_action__input, register_game_action__input_for__client) {
    FAIL("Not implemented");
}

/*
 * Spec: docs/specs/core/game_action/input/game_action__input.h.spec.md
 * Section: 1.4.1 Registration - register_game_action__input_for__offline
 */
TEST(game_action__input, register_game_action__input_for__offline) {
    FAIL("Not implemented");
}

/*
 * Spec: docs/specs/core/game_action/input/game_action__input.h.spec.md
 * Section: 1.4.2 Initialization - initialize_game_action_for__input
 */
TEST(game_action__input, initialize_game_action_for__input) {
    FAIL("Not implemented");
}

/*
 * Spec: docs/specs/core/game_action/input/game_action__input.h.spec.md
 * Section: 1.4.3 Dispatch - dispatch_game_action__input
 */
TEST(game_action__input, dispatch_game_action__input) {
    FAIL("Not implemented");
}

DEFINE_SUITE(game_action__input,
    ADD_TEST(game_action__input, register_game_action__input_for__server),
    ADD_TEST(game_action__input, register_game_action__input_for__client),
    ADD_TEST(game_action__input, register_game_action__input_for__offline),
    ADD_TEST(game_action__input, initialize_game_action_for__input),
    ADD_TEST(game_action__input, dispatch_game_action__input),
    END_TESTS)
