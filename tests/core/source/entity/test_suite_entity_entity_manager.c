#include <entity/test_suite_entity_entity_manager.h>

#include <entity/entity_manager.c>

TEST_FUNCTION(initialize_entity_manager__does_not_crash) {
    Entity_Manager entity_manager;
    memset(&entity_manager, 0, sizeof(entity_manager));

    initialize_entity_manager(&entity_manager);

    return MUNIT_OK;
}

TEST_FUNCTION(initialize_entity_manager__next_ptr_is_set) {
    Entity_Manager entity_manager;
    memset(&entity_manager, 0, sizeof(entity_manager));

    initialize_entity_manager(&entity_manager);

    munit_assert_ptr_not_null(entity_manager.p_ptr_entity__next_in_ptr_array);

    return MUNIT_OK;
}

TEST_FUNCTION(allocate_entity__returns_non_null) {
    Entity_Manager entity_manager;
    memset(&entity_manager, 0, sizeof(entity_manager));

    initialize_entity_manager(&entity_manager);

    Entity *p_entity = allocate_entity_in__entity_manager(
            NULL, NULL, &entity_manager, Entity_Kind__None);

    munit_assert_ptr_not_null(p_entity);

    return MUNIT_OK;
}

TEST_FUNCTION(allocate_entity__sets_kind) {
    Entity_Manager entity_manager;
    memset(&entity_manager, 0, sizeof(entity_manager));

    initialize_entity_manager(&entity_manager);

    Entity *p_entity = allocate_entity_in__entity_manager(
            NULL, NULL, &entity_manager, Entity_Kind__None);

    munit_assert_ptr_not_null(p_entity);
    munit_assert_int(get_kind_of__entity(p_entity), ==, Entity_Kind__None);

    return MUNIT_OK;
}

TEST_FUNCTION(allocate_entity__entity_is_allocated) {
    Entity_Manager entity_manager;
    memset(&entity_manager, 0, sizeof(entity_manager));

    initialize_entity_manager(&entity_manager);

    Entity *p_entity = allocate_entity_in__entity_manager(
            NULL, NULL, &entity_manager, Entity_Kind__None);

    munit_assert_ptr_not_null(p_entity);
    munit_assert_true(is_entity__allocated(p_entity));

    return MUNIT_OK;
}

TEST_FUNCTION(allocate_entity_with__uuid__preserves_uuid) {
    Entity_Manager entity_manager;
    memset(&entity_manager, 0, sizeof(entity_manager));

    initialize_entity_manager(&entity_manager);

    Identifier__u32 test_uuid = 12345;
    Entity *p_entity = allocate_entity_with__this_uuid_in__entity_manager(
            NULL, NULL, &entity_manager, Entity_Kind__None, test_uuid);

    munit_assert_ptr_not_null(p_entity);
    munit_assert_uint32(
            p_entity->_serialization_header.uuid, ==, test_uuid);

    return MUNIT_OK;
}

TEST_FUNCTION(release_entity__entity_is_deallocated) {
    Entity_Manager entity_manager;
    memset(&entity_manager, 0, sizeof(entity_manager));

    initialize_entity_manager(&entity_manager);

    Entity *p_entity = allocate_entity_in__entity_manager(
            NULL, NULL, &entity_manager, Entity_Kind__None);

    munit_assert_ptr_not_null(p_entity);
    munit_assert_true(is_entity__allocated(p_entity));

    release_entity_from__entity_manager(
            NULL, NULL, &entity_manager, p_entity);

    munit_assert_false(is_entity__allocated(p_entity));

    return MUNIT_OK;
}

TEST_FUNCTION(allocate_multiple_entities__returns_different_pointers) {
    Entity_Manager entity_manager;
    memset(&entity_manager, 0, sizeof(entity_manager));

    initialize_entity_manager(&entity_manager);

    Entity *p_entity_1 = allocate_entity_in__entity_manager(
            NULL, NULL, &entity_manager, Entity_Kind__None);
    Entity *p_entity_2 = allocate_entity_in__entity_manager(
            NULL, NULL, &entity_manager, Entity_Kind__None);

    munit_assert_ptr_not_null(p_entity_1);
    munit_assert_ptr_not_null(p_entity_2);
    munit_assert_ptr_not_equal(p_entity_1, p_entity_2);

    return MUNIT_OK;
}

TEST_FUNCTION(allocate_multiple_entities__have_different_uuids) {
    Entity_Manager entity_manager;
    memset(&entity_manager, 0, sizeof(entity_manager));

    initialize_entity_manager(&entity_manager);

    Entity *p_entity_1 = allocate_entity_in__entity_manager(
            NULL, NULL, &entity_manager, Entity_Kind__None);
    Entity *p_entity_2 = allocate_entity_in__entity_manager(
            NULL, NULL, &entity_manager, Entity_Kind__None);

    munit_assert_ptr_not_null(p_entity_1);
    munit_assert_ptr_not_null(p_entity_2);
    munit_assert_uint32(
            p_entity_1->_serialization_header.uuid, !=,
            p_entity_2->_serialization_header.uuid);

    return MUNIT_OK;
}

TEST_FUNCTION(get_p_entity_by__index__returns_allocated_entity) {
    Entity_Manager entity_manager;
    memset(&entity_manager, 0, sizeof(entity_manager));

    initialize_entity_manager(&entity_manager);

    Entity *p_entity = allocate_entity_in__entity_manager(
            NULL, NULL, &entity_manager, Entity_Kind__None);

    munit_assert_ptr_not_null(p_entity);

    Entity *p_found = get_p_entity_by__index_from__entity_manager(
            &entity_manager, 0);

    munit_assert_ptr_not_null(p_found);
    munit_assert_ptr_equal(p_found, p_entity);

    return MUNIT_OK;
}

TEST_FUNCTION(exhaust_entity_pool__returns_null) {
    Entity_Manager entity_manager;
    memset(&entity_manager, 0, sizeof(entity_manager));

    initialize_entity_manager(&entity_manager);

    for (Index__u32 i = 0; i < MAX_QUANTITY_OF__ENTITIES; i++) {
        Entity *p_entity = allocate_entity_in__entity_manager(
                NULL, NULL, &entity_manager, Entity_Kind__None);
        munit_assert_ptr_not_null(p_entity);
    }

    Entity *p_entity_overflow = allocate_entity_in__entity_manager(
            NULL, NULL, &entity_manager, Entity_Kind__None);

    munit_assert_ptr_null(p_entity_overflow);

    return MUNIT_OK;
}

TEST_FUNCTION(release_and_reallocate__succeeds) {
    Entity_Manager entity_manager;
    memset(&entity_manager, 0, sizeof(entity_manager));

    initialize_entity_manager(&entity_manager);

    Entity *p_entity = allocate_entity_in__entity_manager(
            NULL, NULL, &entity_manager, Entity_Kind__None);
    munit_assert_ptr_not_null(p_entity);

    release_entity_from__entity_manager(
            NULL, NULL, &entity_manager, p_entity);
    munit_assert_false(is_entity__allocated(p_entity));

    Entity *p_entity_new = allocate_entity_in__entity_manager(
            NULL, NULL, &entity_manager, Entity_Kind__None);
    munit_assert_ptr_not_null(p_entity_new);
    munit_assert_true(is_entity__allocated(p_entity_new));

    return MUNIT_OK;
}

TEST_FUNCTION(f_entity_initializer__default__does_not_crash) {
    Entity entity;
    memset(&entity, 0, sizeof(entity));

    initialize_entity(&entity, Entity_Kind__None);

    f_entity_initializer__default(NULL, NULL, &entity);

    return MUNIT_OK;
}

DEFINE_SUITE(entity_manager,
    INCLUDE_TEST__STATELESS(initialize_entity_manager__does_not_crash),
    INCLUDE_TEST__STATELESS(initialize_entity_manager__next_ptr_is_set),
    INCLUDE_TEST__STATELESS(allocate_entity__returns_non_null),
    INCLUDE_TEST__STATELESS(allocate_entity__sets_kind),
    INCLUDE_TEST__STATELESS(allocate_entity__entity_is_allocated),
    INCLUDE_TEST__STATELESS(allocate_entity_with__uuid__preserves_uuid),
    INCLUDE_TEST__STATELESS(release_entity__entity_is_deallocated),
    INCLUDE_TEST__STATELESS(allocate_multiple_entities__returns_different_pointers),
    INCLUDE_TEST__STATELESS(allocate_multiple_entities__have_different_uuids),
    INCLUDE_TEST__STATELESS(get_p_entity_by__index__returns_allocated_entity),
    INCLUDE_TEST__STATELESS(exhaust_entity_pool__returns_null),
    INCLUDE_TEST__STATELESS(release_and_reallocate__succeeds),
    INCLUDE_TEST__STATELESS(f_entity_initializer__default__does_not_crash),
    END_TESTS)
