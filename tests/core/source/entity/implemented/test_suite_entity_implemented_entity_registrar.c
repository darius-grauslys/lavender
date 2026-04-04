#include <entity/implemented/test_suite_entity_implemented_entity_registrar.h>

#include <entity/implemented/entity_registrar.c>

TEST_FUNCTION(register_entity__does_not_crash) {
    Entity_Manager entity_manager;
    memset(&entity_manager, 0, sizeof(entity_manager));

    initialize_entity_manager(&entity_manager);

    Entity_Functions functions;
    memset(&functions, 0, sizeof(functions));

    register_entity_into__entity_manager(
            &entity_manager,
            Entity_Kind__None,
            functions);

    return MUNIT_OK;
}

TEST_FUNCTION(sanitize_entity_functions__applies_registered_functions) {
    Entity_Manager entity_manager;
    memset(&entity_manager, 0, sizeof(entity_manager));

    initialize_entity_manager(&entity_manager);

    Entity_Functions functions;
    memset(&functions, 0, sizeof(functions));
    functions.m_entity_dispose_handler = m_entity_dispose_handler__default;
    functions.m_entity_enable_handler = m_entity_enable_handler__default;
    functions.m_entity_disable_handler = m_entity_disable_handler__default;

    register_entity_into__entity_manager(
            &entity_manager,
            Entity_Kind__None,
            functions);

    Entity entity;
    memset(&entity, 0, sizeof(entity));
    initialize_entity(&entity, Entity_Kind__None);

    sanitize_entity_functions(&entity_manager, &entity);

    munit_assert_ptr_equal(
            (void*)entity.entity_functions.m_entity_dispose_handler,
            (void*)m_entity_dispose_handler__default);
    munit_assert_ptr_equal(
            (void*)entity.entity_functions.m_entity_enable_handler,
            (void*)m_entity_enable_handler__default);
    munit_assert_ptr_equal(
            (void*)entity.entity_functions.m_entity_disable_handler,
            (void*)m_entity_disable_handler__default);

    return MUNIT_OK;
}

TEST_FUNCTION(set_entity_initializer__does_not_crash) {
    Entity_Manager entity_manager;
    memset(&entity_manager, 0, sizeof(entity_manager));

    initialize_entity_manager(&entity_manager);

    set_entity_initializer_in__entity_manager(
            &entity_manager,
            f_entity_initializer__default);

    return MUNIT_OK;
}

DEFINE_SUITE(entity_registrar,
    INCLUDE_TEST__STATELESS(register_entity__does_not_crash),
    INCLUDE_TEST__STATELESS(sanitize_entity_functions__applies_registered_functions),
    INCLUDE_TEST__STATELESS(set_entity_initializer__does_not_crash),
    END_TESTS)
