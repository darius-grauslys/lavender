#include <audio/test_suite_audio_audio_effect.h>

#include <audio/audio_effect.c>

/**
 * Spec: docs/specs/core/audio/audio_effect.h.spec.md
 * Section: 1.4.1 Initialization
 */
TEST_FUNCTION(initialize_audio_effect__sets_all_fields) {
    Audio_Effect audio_effect;
    Timer__u32 timer;
    timer.remaining__u32 = 100;
    timer.start__u32 = 100;

    initialize_audio_effect(
            &audio_effect,
            (void*)0xDEADBEEF,
            Audio_Effect_Kind__None,
            AUDIO_FLAGS__NONE,
            timer);

    munit_assert_ptr_equal(audio_effect.p_audio_instance_handle, (void*)0xDEADBEEF);
    munit_assert_int(audio_effect.the_kind_of__audio_effect, ==, Audio_Effect_Kind__None);
    munit_assert_uint8(audio_effect.audio_flags__u8, ==, AUDIO_FLAGS__NONE);
    munit_assert_uint32(audio_effect.timer_for__audio.remaining__u32, ==, 100);
    munit_assert_uint32(audio_effect.timer_for__audio.start__u32, ==, 100);

    return MUNIT_OK;
}

/**
 * Spec: docs/specs/core/audio/audio_effect.h.spec.md
 * Section: 1.4.1 Initialization
 */
TEST_FUNCTION(initialize_audio_effect__with_active_flag) {
    Audio_Effect audio_effect;
    Timer__u32 timer;
    timer.remaining__u32 = 50;
    timer.start__u32 = 50;

    initialize_audio_effect(
            &audio_effect,
            (void*)0x1234,
            Audio_Effect_Kind__None,
            AUDIO_FLAG__IS_ACTIVE,
            timer);

    munit_assert_true(is_audio__active(&audio_effect));
    munit_assert_false(is_audio__released_on_completion(&audio_effect));
    munit_assert_false(is_audio__looping(&audio_effect));

    return MUNIT_OK;
}

/**
 * Spec: docs/specs/core/audio/audio_effect.h.spec.md
 * Section: 1.4.1 Initialization
 */
TEST_FUNCTION(initialize_audio_effect__with_looping_flag) {
    Audio_Effect audio_effect;
    Timer__u32 timer;
    timer.remaining__u32 = 200;
    timer.start__u32 = 200;

    initialize_audio_effect(
            &audio_effect,
            NULL,
            Audio_Effect_Kind__None,
            AUDIO_FLAG__IS_LOOPING,
            timer);

    munit_assert_false(is_audio__active(&audio_effect));
    munit_assert_false(is_audio__released_on_completion(&audio_effect));
    munit_assert_true(is_audio__looping(&audio_effect));

    return MUNIT_OK;
}

/**
 * Spec: docs/specs/core/audio/audio_effect.h.spec.md
 * Section: 1.4.1 Initialization
 */
TEST_FUNCTION(initialize_audio_effect__with_release_on_complete_flag) {
    Audio_Effect audio_effect;
    Timer__u32 timer;
    timer.remaining__u32 = 10;
    timer.start__u32 = 10;

    initialize_audio_effect(
            &audio_effect,
            NULL,
            Audio_Effect_Kind__None,
            AUDIO_FLAG__RELEASE_ON_COMPLETE,
            timer);

    munit_assert_false(is_audio__active(&audio_effect));
    munit_assert_true(is_audio__released_on_completion(&audio_effect));
    munit_assert_false(is_audio__looping(&audio_effect));

    return MUNIT_OK;
}

/**
 * Spec: docs/specs/core/audio/audio_effect.h.spec.md
 * Section: 1.4.1 Initialization
 */
TEST_FUNCTION(initialize_audio_effect__with_all_flags) {
    Audio_Effect audio_effect;
    Timer__u32 timer;
    timer.remaining__u32 = 300;
    timer.start__u32 = 300;

    Audio_Flags__u8 all_flags =
        AUDIO_FLAG__IS_ACTIVE
        | AUDIO_FLAG__RELEASE_ON_COMPLETE
        | AUDIO_FLAG__IS_LOOPING;

    initialize_audio_effect(
            &audio_effect,
            (void*)0xABCD,
            Audio_Effect_Kind__None,
            all_flags,
            timer);

    munit_assert_true(is_audio__active(&audio_effect));
    munit_assert_true(is_audio__released_on_completion(&audio_effect));
    munit_assert_true(is_audio__looping(&audio_effect));

    return MUNIT_OK;
}

/**
 * Spec: docs/specs/core/audio/audio_effect.h.spec.md
 * Section: 1.4.5 Flag Mutations (static inline)
 */
TEST_FUNCTION(set_audio_as__active__sets_flag) {
    Audio_Effect audio_effect;
    audio_effect.audio_flags__u8 = AUDIO_FLAGS__NONE;

    set_audio_as__active(&audio_effect);

    munit_assert_true(is_audio__active(&audio_effect));

    return MUNIT_OK;
}

/**
 * Spec: docs/specs/core/audio/audio_effect.h.spec.md
 * Section: 1.4.5 Flag Mutations (static inline)
 */
TEST_FUNCTION(set_audio_as__inactive__clears_flag) {
    Audio_Effect audio_effect;
    audio_effect.audio_flags__u8 = AUDIO_FLAG__IS_ACTIVE;

    munit_assert_true(is_audio__active(&audio_effect));

    set_audio_as__inactive(&audio_effect);

    munit_assert_false(is_audio__active(&audio_effect));

    return MUNIT_OK;
}

/**
 * Spec: docs/specs/core/audio/audio_effect.h.spec.md
 * Section: 1.4.5 Flag Mutations (static inline)
 */
TEST_FUNCTION(set_audio_as__inactive__preserves_other_flags) {
    Audio_Effect audio_effect;
    audio_effect.audio_flags__u8 =
        AUDIO_FLAG__IS_ACTIVE
        | AUDIO_FLAG__IS_LOOPING
        | AUDIO_FLAG__RELEASE_ON_COMPLETE;

    set_audio_as__inactive(&audio_effect);

    munit_assert_false(is_audio__active(&audio_effect));
    munit_assert_true(is_audio__looping(&audio_effect));
    munit_assert_true(is_audio__released_on_completion(&audio_effect));

    return MUNIT_OK;
}

/**
 * Spec: docs/specs/core/audio/audio_effect.h.spec.md
 * Section: 1.4.5 Flag Mutations (static inline)
 */
TEST_FUNCTION(set_audio_as__looping__sets_flag) {
    Audio_Effect audio_effect;
    audio_effect.audio_flags__u8 = AUDIO_FLAGS__NONE;

    set_audio_as__looping(&audio_effect);

    munit_assert_true(is_audio__looping(&audio_effect));

    return MUNIT_OK;
}

/**
 * Spec: docs/specs/core/audio/audio_effect.h.spec.md
 * Section: 1.4.5 Flag Mutations (static inline)
 */
TEST_FUNCTION(set_audio_as__not_looping__clears_flag) {
    Audio_Effect audio_effect;
    audio_effect.audio_flags__u8 = AUDIO_FLAG__IS_LOOPING;

    set_audio_as__not_looping(&audio_effect);

    munit_assert_false(is_audio__looping(&audio_effect));

    return MUNIT_OK;
}

/**
 * Spec: docs/specs/core/audio/audio_effect.h.spec.md
 * Section: 1.4.5 Flag Mutations (static inline)
 */
TEST_FUNCTION(set_audio_as__releasing_on_completion__sets_flag) {
    Audio_Effect audio_effect;
    audio_effect.audio_flags__u8 = AUDIO_FLAGS__NONE;

    set_audio_as__releasing_on_completion(&audio_effect);

    munit_assert_true(is_audio__released_on_completion(&audio_effect));

    return MUNIT_OK;
}

/**
 * Spec: docs/specs/core/audio/audio_effect.h.spec.md
 * Section: 1.4.5 Flag Mutations (static inline)
 */
TEST_FUNCTION(set_audio_as__not_releasing_on_completion__clears_flag) {
    Audio_Effect audio_effect;
    audio_effect.audio_flags__u8 = AUDIO_FLAG__RELEASE_ON_COMPLETE;

    set_audio_as__not_releasing_on_completion(&audio_effect);

    munit_assert_false(is_audio__released_on_completion(&audio_effect));

    return MUNIT_OK;
}

/**
 * Spec: docs/specs/core/audio/audio_effect.h.spec.md
 * Section: 1.4.2 Convenience Initialization (static inline)
 */
TEST_FUNCTION(set_audio_effect__preserves_handle_and_active_state) {
    Audio_Effect audio_effect;
    Timer__u32 timer;
    timer.remaining__u32 = 100;
    timer.start__u32 = 100;

    initialize_audio_effect(
            &audio_effect,
            (void*)0xBEEF,
            Audio_Effect_Kind__None,
            AUDIO_FLAG__IS_ACTIVE,
            timer);

    Timer__u32 new_timer;
    new_timer.remaining__u32 = 500;
    new_timer.start__u32 = 500;

    set_audio_effect(
            &audio_effect,
            Audio_Effect_Kind__None,
            AUDIO_FLAG__IS_LOOPING,
            new_timer);

    munit_assert_ptr_equal(audio_effect.p_audio_instance_handle, (void*)0xBEEF);
    munit_assert_true(is_audio__active(&audio_effect));
    munit_assert_true(is_audio__looping(&audio_effect));
    munit_assert_uint32(audio_effect.timer_for__audio.remaining__u32, ==, 500);

    return MUNIT_OK;
}

/**
 * Spec: docs/specs/core/audio/audio_effect.h.spec.md
 * Section: 1.4.2 Convenience Initialization (static inline)
 */
TEST_FUNCTION(set_audio_effect__preserves_inactive_state) {
    Audio_Effect audio_effect;
    Timer__u32 timer;
    timer.remaining__u32 = 100;
    timer.start__u32 = 100;

    initialize_audio_effect(
            &audio_effect,
            (void*)0xCAFE,
            Audio_Effect_Kind__None,
            AUDIO_FLAGS__NONE,
            timer);

    munit_assert_false(is_audio__active(&audio_effect));

    Timer__u32 new_timer;
    new_timer.remaining__u32 = 200;
    new_timer.start__u32 = 200;

    set_audio_effect(
            &audio_effect,
            Audio_Effect_Kind__None,
            AUDIO_FLAG__RELEASE_ON_COMPLETE,
            new_timer);

    munit_assert_false(is_audio__active(&audio_effect));
    munit_assert_true(is_audio__released_on_completion(&audio_effect));

    return MUNIT_OK;
}

/**
 * Spec: docs/specs/core/audio/audio_effect.h.spec.md
 * Section: 1.4.4 Flag Queries (static inline)
 */
TEST_FUNCTION(is_audio__active__returns_false_when_no_flags) {
    Audio_Effect audio_effect;
    audio_effect.audio_flags__u8 = AUDIO_FLAGS__NONE;

    munit_assert_false(is_audio__active(&audio_effect));

    return MUNIT_OK;
}

/**
 * Spec: docs/specs/core/audio/audio_effect.h.spec.md
 * Section: 1.4.4 Flag Queries (static inline)
 */
TEST_FUNCTION(is_audio__looping__returns_false_when_no_flags) {
    Audio_Effect audio_effect;
    audio_effect.audio_flags__u8 = AUDIO_FLAGS__NONE;

    munit_assert_false(is_audio__looping(&audio_effect));

    return MUNIT_OK;
}

/**
 * Spec: docs/specs/core/audio/audio_effect.h.spec.md
 * Section: 1.4.4 Flag Queries (static inline)
 */
TEST_FUNCTION(is_audio__released_on_completion__returns_false_when_no_flags) {
    Audio_Effect audio_effect;
    audio_effect.audio_flags__u8 = AUDIO_FLAGS__NONE;

    munit_assert_false(is_audio__released_on_completion(&audio_effect));

    return MUNIT_OK;
}

DEFINE_SUITE(audio_effect,
    INCLUDE_TEST__STATELESS(initialize_audio_effect__sets_all_fields),
    INCLUDE_TEST__STATELESS(initialize_audio_effect__with_active_flag),
    INCLUDE_TEST__STATELESS(initialize_audio_effect__with_looping_flag),
    INCLUDE_TEST__STATELESS(initialize_audio_effect__with_release_on_complete_flag),
    INCLUDE_TEST__STATELESS(initialize_audio_effect__with_all_flags),
    INCLUDE_TEST__STATELESS(set_audio_as__active__sets_flag),
    INCLUDE_TEST__STATELESS(set_audio_as__inactive__clears_flag),
    INCLUDE_TEST__STATELESS(set_audio_as__inactive__preserves_other_flags),
    INCLUDE_TEST__STATELESS(set_audio_as__looping__sets_flag),
    INCLUDE_TEST__STATELESS(set_audio_as__not_looping__clears_flag),
    INCLUDE_TEST__STATELESS(set_audio_as__releasing_on_completion__sets_flag),
    INCLUDE_TEST__STATELESS(set_audio_as__not_releasing_on_completion__clears_flag),
    INCLUDE_TEST__STATELESS(set_audio_effect__preserves_handle_and_active_state),
    INCLUDE_TEST__STATELESS(set_audio_effect__preserves_inactive_state),
    INCLUDE_TEST__STATELESS(is_audio__active__returns_false_when_no_flags),
    INCLUDE_TEST__STATELESS(is_audio__looping__returns_false_when_no_flags),
    INCLUDE_TEST__STATELESS(is_audio__released_on_completion__returns_false_when_no_flags),
    END_TESTS)
