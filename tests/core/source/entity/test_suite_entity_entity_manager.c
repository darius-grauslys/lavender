#include <entity/test_suite_entity_entity_manager.h>

#include <entity/entity_manager.c>

/**
 * Spec: docs/specs/core/entity/entity_manager.h.spec.md
 * Section: 1.4.1 Initialization
 *
 * Verifies that initialize_entity_manager does not crash when called
 * with a zeroed Entity_Manager instance.
 */
TEST_FUNCTION(initialize_entity_manager__does_not_crash) {
    Entity_Manager entity_manager;
    memset(&entity_manager, 0, sizeof(entity_manager));

    initialize_entity_manager(&entity_manager);

    return MUNIT_OK;
}

/**
 * Spec: docs/specs/core/entity/entity_manager.h.spec.md
 * Section: 1.4.1 Initialization
 *
 * Verifies that after initialization, p_ptr_entity__next_in_ptr_array
 * is set to a non-null value, indicating the pointer array is ready
 * for use.
 */
TEST_FUNCTION(initialize_entity_manager__next_ptr_is_set) {
    Entity_Manager entity_manager;
    memset(&entity_manager, 0, sizeof(entity_manager));

    initialize_entity_manager(&entity_manager);

    munit_assert_ptr_not_null(entity_manager.p_ptr_entity__next_in_ptr_array);

    return MUNIT_OK;
}

/**
 * Spec: docs/specs/core/entity/entity_manager.h.spec.md
 * Section: 1.4.4 Allocation
 *
 * Verifies that allocate_entity_in__entity_manager returns a non-null
 * pointer when the pool has available slots.
 */
TEST_FUNCTION(allocate_entity__returns_non_null) {
    Entity_Manager entity_manager;
    memset(&entity_manager, 0, sizeof(entity_manager));

    initialize_entity_manager(&entity_manager);

    Entity *p_entity = allocate_entity_in__entity_manager(
            NULL, NULL, &entity_manager, Entity_Kind__None);

    munit_assert_ptr_not_null(p_entity);

    return MUNIT_OK;
}

/**
 * Spec: docs/specs/core/entity/entity_manager.h.spec.md
 * Section: 1.4.4 Allocation
 *
 * Verifies that the allocated entity has its Entity_Kind set to the
 * kind that was requested at allocation time.
 */
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

/**
 * Spec: docs/specs/core/entity/entity_manager.h.spec.md
 * Section: 1.4.4 Allocation / 1.5.10 Postconditions
 *
 * Verifies that after allocation, is_entity__allocated returns true
 * for the returned entity pointer.
 */
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

/**
 * Spec: docs/specs/core/entity/entity_manager.h.spec.md
 * Section: 1.4.4 Allocation / 1.5.6 Deserialization Pattern
 *
 * Verifies that allocate_entity_with__this_uuid_in__entity_manager
 * preserves the caller-supplied UUID in the entity's serialization
 * header, as required for deserialization use cases.
 */
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

/**
 * Spec: docs/specs/core/entity/entity_manager.h.spec.md
 * Section: 1.4.5 Deallocation / 1.5.10 Postconditions
 *
 * Verifies that after release_entity_from__entity_manager is called,
 * is_entity__allocated returns false for the released entity.
 */
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

/**
 * Spec: docs/specs/core/entity/entity_manager.h.spec.md
 * Section: 1.4.4 Allocation
 *
 * Verifies that two successive allocations return distinct entity
 * pointers, confirming that each allocation draws from a different
 * pool slot.
 */
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

/**
 * Spec: docs/specs/core/entity/entity_manager.h.spec.md
 * Section: 1.4.4 Allocation
 *
 * Verifies that two successively allocated entities are assigned
 * distinct UUIDs, confirming the randomizer produces unique identifiers
 * per allocation.
 */
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

/**
 * Spec: docs/specs/core/entity/entity_manager.h.spec.md
 * Section: 1.4.6 Lookup (static inline)
 *
 * Verifies that get_p_entity_by__index_from__entity_manager returns
 * the correct entity pointer at index 0 after a single allocation.
 */
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

/**
 * Spec: docs/specs/core/entity/entity_manager.h.spec.md
 * Section: 1.5.11 Error Handling
 *
 * Verifies that once the entity pool is fully exhausted, a subsequent
 * allocation attempt returns null rather than overflowing the pool.
 */
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

/**
 * Spec: docs/specs/core/entity/entity_manager.h.spec.md
 * Section: 1.4.5 Deallocation / 1.4.4 Allocation
 *
 * Verifies that a slot released via release_entity_from__entity_manager
 * can be successfully reallocated, and that the newly allocated entity
 * reports as allocated.
 */
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

/**
 * Spec: docs/specs/core/entity/entity_manager.h.spec.md
 * Section: 1.4.3 Default Initializer
 *
 * Verifies that f_entity_initializer__default does not crash when
 * invoked with null Game and World pointers and a valid entity.
 */
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
