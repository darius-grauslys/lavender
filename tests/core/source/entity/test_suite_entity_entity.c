#include <entity/test_suite_entity_entity.h>

#include <entity/entity.c>

TEST_FUNCTION(initialize_entity__sets_kind) {
    Entity entity;
    memset(&entity, 0, sizeof(entity));

    initialize_entity(&entity, Entity_Kind__None);

    munit_assert_int(get_kind_of__entity(&entity), ==, Entity_Kind__None);

    return MUNIT_OK;
}

TEST_FUNCTION(initialize_entity__entity_is_not_enabled_by_default) {
    Entity entity;
    memset(&entity, 0, sizeof(entity));

    initialize_entity(&entity, Entity_Kind__None);

    munit_assert_false(is_entity__enabled(&entity));

    return MUNIT_OK;
}

TEST_FUNCTION(set_entity_as__enabled__makes_entity_enabled) {
    Entity entity;
    memset(&entity, 0, sizeof(entity));

    initialize_entity(&entity, Entity_Kind__None);
    set_entity_as__enabled(&entity);

    munit_assert_true(is_entity__enabled(&entity));

    return MUNIT_OK;
}

TEST_FUNCTION(set_entity_as__disabled__makes_entity_disabled) {
    Entity entity;
    memset(&entity, 0, sizeof(entity));

    initialize_entity(&entity, Entity_Kind__None);
    set_entity_as__enabled(&entity);
    munit_assert_true(is_entity__enabled(&entity));

    set_entity_as__disabled(&entity);
    munit_assert_false(is_entity__enabled(&entity));

    return MUNIT_OK;
}

TEST_FUNCTION(get_kind_of__entity__returns_correct_kind) {
    Entity entity;
    memset(&entity, 0, sizeof(entity));

    initialize_entity(&entity, Entity_Kind__None);

    munit_assert_int(get_kind_of__entity(&entity), ==, Entity_Kind__None);

    return MUNIT_OK;
}

TEST_FUNCTION(is_entity__allocated__returns_false_for_null) {
    munit_assert_false(is_entity__allocated(NULL));

    return MUNIT_OK;
}

TEST_FUNCTION(set_entity_as__enabled_then_disabled__roundtrip) {
    Entity entity;
    memset(&entity, 0, sizeof(entity));

    initialize_entity(&entity, Entity_Kind__None);

    munit_assert_false(is_entity__enabled(&entity));

    set_entity_as__enabled(&entity);
    munit_assert_true(is_entity__enabled(&entity));

    set_entity_as__disabled(&entity);
    munit_assert_false(is_entity__enabled(&entity));

    set_entity_as__enabled(&entity);
    munit_assert_true(is_entity__enabled(&entity));

    return MUNIT_OK;
}

TEST_FUNCTION(m_entity_enable_handler__default__enables_entity) {
    Entity entity;
    memset(&entity, 0, sizeof(entity));

    initialize_entity(&entity, Entity_Kind__None);
    munit_assert_false(is_entity__enabled(&entity));

    m_entity_enable_handler__default(&entity, NULL, NULL);
    munit_assert_true(is_entity__enabled(&entity));

    return MUNIT_OK;
}

TEST_FUNCTION(m_entity_disable_handler__default__disables_entity) {
    Entity entity;
    memset(&entity, 0, sizeof(entity));

    initialize_entity(&entity, Entity_Kind__None);
    set_entity_as__enabled(&entity);
    munit_assert_true(is_entity__enabled(&entity));

    m_entity_disable_handler__default(&entity, NULL, NULL);
    munit_assert_false(is_entity__enabled(&entity));

    return MUNIT_OK;
}

TEST_FUNCTION(m_entity_dispose_handler__default__does_not_crash) {
    Entity entity;
    memset(&entity, 0, sizeof(entity));

    initialize_entity(&entity, Entity_Kind__None);

    m_entity_dispose_handler__default(&entity, NULL, NULL);

    return MUNIT_OK;
}

DEFINE_SUITE(entity,
    INCLUDE_TEST__STATELESS(initialize_entity__sets_kind),
    INCLUDE_TEST__STATELESS(initialize_entity__entity_is_not_enabled_by_default),
    INCLUDE_TEST__STATELESS(set_entity_as__enabled__makes_entity_enabled),
    INCLUDE_TEST__STATELESS(set_entity_as__disabled__makes_entity_disabled),
    INCLUDE_TEST__STATELESS(get_kind_of__entity__returns_correct_kind),
    INCLUDE_TEST__STATELESS(is_entity__allocated__returns_false_for_null),
    INCLUDE_TEST__STATELESS(set_entity_as__enabled_then_disabled__roundtrip),
    INCLUDE_TEST__STATELESS(m_entity_enable_handler__default__enables_entity),
    INCLUDE_TEST__STATELESS(m_entity_disable_handler__default__disables_entity),
    INCLUDE_TEST__STATELESS(m_entity_dispose_handler__default__does_not_crash),
    END_TESTS)
