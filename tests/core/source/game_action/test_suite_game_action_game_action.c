#include <game_action/test_suite_game_action_game_action.h>

#include <game_action/game_action.c>

///
/// Spec:    docs/specs/core/game_action/game_action.h.spec.md
/// Section: 1.4.1. Initialization
///
TEST_FUNCTION(game_action__initialize_game_action__zeroes_struct) {
    Game_Action ga;
    memset(&ga, 0xFF, sizeof(ga));
    initialize_game_action(&ga);

    munit_assert_int(
            get_kind_of__game_action(&ga),
            ==,
            Game_Action_Kind__None);
    munit_assert_uint8(ga.game_action_flags, ==, 0);

    return MUNIT_OK;
}

///
/// Spec:    docs/specs/core/game_action/game_action.h.spec.md
/// Section: 1.4.2. Kind Accessors
///
TEST_FUNCTION(game_action__set_the_kind_of__game_action__sets_kind) {
    Game_Action ga;
    initialize_game_action(&ga);

    set_the_kind_of__game_action(&ga,
            Game_Action_Kind__Bad_Request);

    munit_assert_int(
            get_kind_of__game_action(&ga),
            ==,
            Game_Action_Kind__Bad_Request);

    return MUNIT_OK;
}

///
/// Spec:    docs/specs/core/game_action/game_action.h.spec.md
/// Section: 1.4.2. Kind Accessors
///
TEST_FUNCTION(game_action__get_kind_of__game_action__returns_correct_kind) {
    Game_Action ga;
    initialize_game_action(&ga);

    set_the_kind_of__game_action(&ga,
            Game_Action_Kind__TCP_Connect);

    munit_assert_int(
            get_kind_of__game_action(&ga),
            ==,
            Game_Action_Kind__TCP_Connect);

    set_the_kind_of__game_action(&ga,
            Game_Action_Kind__Entity__Spawn);

    munit_assert_int(
            get_kind_of__game_action(&ga),
            ==,
            Game_Action_Kind__Entity__Spawn);

    return MUNIT_OK;
}

///
/// Spec:    docs/specs/core/game_action/game_action.h.spec.md
/// Section: 1.4.4. Flag Accessors
///
TEST_FUNCTION(game_action__is_game_action__allocated__false_after_init) {
    Game_Action ga;
    initialize_game_action(&ga);

    munit_assert_false(is_game_action__allocated(&ga));

    return MUNIT_OK;
}

///
/// Spec:    docs/specs/core/game_action/game_action.h.spec.md
/// Section: 1.4.4. Flag Accessors
///
TEST_FUNCTION(game_action__is_game_action__allocated__null_safe) {
    munit_assert_false(is_game_action__allocated(0));

    return MUNIT_OK;
}

///
/// Spec:    docs/specs/core/game_action/game_action.h.spec.md
/// Section: 1.4.4. Flag Accessors
///
TEST_FUNCTION(game_action__set_game_action_as__allocated__sets_flag) {
    Game_Action ga;
    initialize_game_action(&ga);

    set_game_action_as__allocated(&ga);

    munit_assert_true(is_game_action__allocated(&ga));

    return MUNIT_OK;
}

///
/// Spec:    docs/specs/core/game_action/game_action.h.spec.md
/// Section: 1.4.4. Flag Accessors
///
TEST_FUNCTION(game_action__set_game_action_as__deallocated__clears_flag) {
    Game_Action ga;
    initialize_game_action(&ga);

    set_game_action_as__allocated(&ga);
    munit_assert_true(is_game_action__allocated(&ga));

    set_game_action_as__deallocated(&ga);
    munit_assert_false(is_game_action__allocated(&ga));

    return MUNIT_OK;
}

///
/// Spec:    docs/specs/core/game_action/game_action.h.spec.md
/// Section: 1.4.4. Flag Accessors
///
TEST_FUNCTION(game_action__set_game_action_as__inbound__sets_flag) {
    Game_Action ga;
    initialize_game_action(&ga);

    set_game_action_as__inbound(&ga);

    munit_assert_true(is_game_action__inbound(&ga));

    return MUNIT_OK;
}

///
/// Spec:    docs/specs/core/game_action/game_action.h.spec.md
/// Section: 1.4.4. Flag Accessors
///
TEST_FUNCTION(game_action__set_game_action_as__outbound__clears_flag) {
    Game_Action ga;
    initialize_game_action(&ga);

    set_game_action_as__inbound(&ga);
    munit_assert_true(is_game_action__inbound(&ga));

    set_game_action_as__outbound(&ga);
    munit_assert_false(is_game_action__inbound(&ga));

    return MUNIT_OK;
}

///
/// Spec:    docs/specs/core/game_action/game_action.h.spec.md
/// Section: 1.4.4. Flag Accessors
///
TEST_FUNCTION(game_action__set_game_action_as__local__sets_flag) {
    Game_Action ga;
    initialize_game_action(&ga);

    set_game_action_as__local(&ga);

    munit_assert_true(is_game_action__local(&ga));

    return MUNIT_OK;
}

///
/// Spec:    docs/specs/core/game_action/game_action.h.spec.md
/// Section: 1.4.4. Flag Accessors
///
TEST_FUNCTION(game_action__set_game_action_as__NOT_local__clears_flag) {
    Game_Action ga;
    initialize_game_action(&ga);

    set_game_action_as__local(&ga);
    munit_assert_true(is_game_action__local(&ga));

    set_game_action_as__NOT_local(&ga);
    munit_assert_false(is_game_action__local(&ga));

    return MUNIT_OK;
}

///
/// Spec:    docs/specs/core/game_action/game_action.h.spec.md
/// Section: 1.4.4. Flag Accessors
///
TEST_FUNCTION(game_action__set_game_action_as__broadcasted__sets_flag) {
    Game_Action ga;
    initialize_game_action(&ga);

    set_game_action_as__broadcasted(&ga);

    munit_assert_true(is_game_action__broadcasted(&ga));

    return MUNIT_OK;
}

///
/// Spec:    docs/specs/core/game_action/game_action.h.spec.md
/// Section: 1.4.4. Flag Accessors
///
TEST_FUNCTION(game_action__set_game_action_as__NOT_broadcasted__clears_flag) {
    Game_Action ga;
    initialize_game_action(&ga);

    set_game_action_as__broadcasted(&ga);
    munit_assert_true(is_game_action__broadcasted(&ga));

    set_game_action_as__NOT_broadcasted(&ga);
    munit_assert_false(is_game_action__broadcasted(&ga));

    return MUNIT_OK;
}

///
/// Spec:    docs/specs/core/game_action/game_action.h.spec.md
/// Section: 1.4.4. Flag Accessors
///
TEST_FUNCTION(game_action__set_game_action_as__bad_request__sets_flag) {
    Game_Action ga;
    initialize_game_action(&ga);

    set_game_action_as__bad_request(&ga);

    munit_assert_true(is_game_action__bad_request(&ga));

    return MUNIT_OK;
}

///
/// Spec:    docs/specs/core/game_action/game_action.h.spec.md
/// Section: 1.4.4. Flag Accessors
///
TEST_FUNCTION(game_action__set_game_action_as__NOT_bad_request__clears_flag) {
    Game_Action ga;
    initialize_game_action(&ga);

    set_game_action_as__bad_request(&ga);
    munit_assert_true(is_game_action__bad_request(&ga));

    set_game_action_as__NOT_bad_request(&ga);
    munit_assert_false(is_game_action__bad_request(&ga));

    return MUNIT_OK;
}

///
/// Spec:    docs/specs/core/game_action/game_action.h.spec.md
/// Section: 1.4.4. Flag Accessors
///
TEST_FUNCTION(game_action__flags_are_independent) {
    Game_Action ga;
    initialize_game_action(&ga);

    set_game_action_as__allocated(&ga);
    set_game_action_as__local(&ga);
    set_game_action_as__broadcasted(&ga);

    munit_assert_true(is_game_action__allocated(&ga));
    munit_assert_true(is_game_action__local(&ga));
    munit_assert_true(is_game_action__broadcasted(&ga));
    munit_assert_false(is_game_action__inbound(&ga));
    munit_assert_false(is_game_action__bad_request(&ga));

    set_game_action_as__NOT_local(&ga);

    munit_assert_true(is_game_action__allocated(&ga));
    munit_assert_false(is_game_action__local(&ga));
    munit_assert_true(is_game_action__broadcasted(&ga));

    return MUNIT_OK;
}

///
/// Spec:    docs/specs/core/game_action/game_action.h.spec.md
/// Section: 1.4.3. UUID Accessors
///
TEST_FUNCTION(game_action__get_client_uuid__returns_correct_uuid) {
    Game_Action ga;
    initialize_game_action(&ga);

    ga.uuid_of__client__u32 = 42;

    munit_assert_uint32(
            get_client_uuid_from__game_action(&ga),
            ==,
            42);

    return MUNIT_OK;
}

///
/// Spec:    docs/specs/core/game_action/game_action.h.spec.md
/// Section: 1.4.3. UUID Accessors
///
TEST_FUNCTION(game_action__get_response_uuid__returns_correct_uuid) {
    Game_Action ga;
    initialize_game_action(&ga);

    ga.uuid_of__game_action__responding_to = 99;

    munit_assert_uint32(
            get_response_uuid_from__game_action(&ga),
            ==,
            99);

    return MUNIT_OK;
}

DEFINE_SUITE(game_action,
    INCLUDE_TEST__STATELESS(game_action__initialize_game_action__zeroes_struct),
    INCLUDE_TEST__STATELESS(game_action__set_the_kind_of__game_action__sets_kind),
    INCLUDE_TEST__STATELESS(game_action__get_kind_of__game_action__returns_correct_kind),
    INCLUDE_TEST__STATELESS(game_action__is_game_action__allocated__false_after_init),
    INCLUDE_TEST__STATELESS(game_action__is_game_action__allocated__null_safe),
    INCLUDE_TEST__STATELESS(game_action__set_game_action_as__allocated__sets_flag),
    INCLUDE_TEST__STATELESS(game_action__set_game_action_as__deallocated__clears_flag),
    INCLUDE_TEST__STATELESS(game_action__set_game_action_as__inbound__sets_flag),
    INCLUDE_TEST__STATELESS(game_action__set_game_action_as__outbound__clears_flag),
    INCLUDE_TEST__STATELESS(game_action__set_game_action_as__local__sets_flag),
    INCLUDE_TEST__STATELESS(game_action__set_game_action_as__NOT_local__clears_flag),
    INCLUDE_TEST__STATELESS(game_action__set_game_action_as__broadcasted__sets_flag),
    INCLUDE_TEST__STATELESS(game_action__set_game_action_as__NOT_broadcasted__clears_flag),
    INCLUDE_TEST__STATELESS(game_action__set_game_action_as__bad_request__sets_flag),
    INCLUDE_TEST__STATELESS(game_action__set_game_action_as__NOT_bad_request__clears_flag),
    INCLUDE_TEST__STATELESS(game_action__flags_are_independent),
    INCLUDE_TEST__STATELESS(game_action__get_client_uuid__returns_correct_uuid),
    INCLUDE_TEST__STATELESS(game_action__get_response_uuid__returns_correct_uuid),
    END_TESTS)
