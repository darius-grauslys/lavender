#include <world/test_suite_world_chunk.h>

#include <world/chunk.c>

///
/// Spec: docs/specs/core/world/chunk.h.spec.md
/// Section: 1.4.1 Initialization, 1.4.3 Tile Access (get_uuid__chunk)
///
TEST_FUNCTION(chunk__initialize_chunk__sets_uuid) {
    Chunk chunk;
    Identifier__u64 uuid = 12345;
    initialize_chunk(&chunk, uuid);
    munit_assert_uint64(get_uuid__chunk(&chunk), ==, uuid);
    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/world/chunk.h.spec.md
/// Section: 1.4.1 Initialization, 1.4.6 Flag Queries
///
TEST_FUNCTION(chunk__initialize_chunk__clears_flags) {
    Chunk chunk;
    initialize_chunk(&chunk, 1);
    munit_assert_false(is_chunk__active(&chunk));
    munit_assert_false(is_chunk__awaiting_serialization(&chunk));
    munit_assert_false(is_chunk__awaiting_deserialization(&chunk));
    munit_assert_false(is_chunk__updated(&chunk));
    munit_assert_false(is_chunk__visually_updated(&chunk));
    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/world/chunk.h.spec.md
/// Section: 1.4.5 Flag Management (set_chunk_as__active), 1.4.6 Flag Queries
///
TEST_FUNCTION(chunk__set_chunk_as__active) {
    Chunk chunk;
    initialize_chunk(&chunk, 1);
    set_chunk_as__active(&chunk);
    munit_assert_true(is_chunk__active(&chunk));
    munit_assert_false(is_chunk__inactive(&chunk));
    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/world/chunk.h.spec.md
/// Section: 1.4.5 Flag Management (set_chunk_as__inactive), 1.4.6 Flag Queries
///
TEST_FUNCTION(chunk__set_chunk_as__inactive) {
    Chunk chunk;
    initialize_chunk(&chunk, 1);
    set_chunk_as__active(&chunk);
    set_chunk_as__inactive(&chunk);
    munit_assert_false(is_chunk__active(&chunk));
    munit_assert_true(is_chunk__inactive(&chunk));
    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/world/chunk.h.spec.md
/// Section: 1.4.5 Flag Management (set_chunk_as__awaiting_serialization),
///          1.5.2 Serialization State Machine
///
TEST_FUNCTION(chunk__set_chunk_as__awaiting_serialization__clears_active_and_deserialization) {
    Chunk chunk;
    initialize_chunk(&chunk, 1);
    set_chunk_as__active(&chunk);
    set_chunk_as__awaiting_serialization(&chunk);
    munit_assert_true(is_chunk__awaiting_serialization(&chunk));
    munit_assert_false(is_chunk__active(&chunk));
    munit_assert_false(is_chunk__awaiting_deserialization(&chunk));
    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/world/chunk.h.spec.md
/// Section: 1.4.5 Flag Management (set_chunk_as__awaiting_deserialization),
///          1.5.2 Serialization State Machine
///
TEST_FUNCTION(chunk__set_chunk_as__awaiting_deserialization__clears_active_and_serialization) {
    Chunk chunk;
    initialize_chunk(&chunk, 1);
    set_chunk_as__active(&chunk);
    set_chunk_as__awaiting_deserialization(&chunk);
    munit_assert_true(is_chunk__awaiting_deserialization(&chunk));
    munit_assert_false(is_chunk__active(&chunk));
    munit_assert_false(is_chunk__awaiting_serialization(&chunk));
    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/world/chunk.h.spec.md
/// Section: 1.4.5 Flag Management (set_chunk_as__updated), 1.4.6 Flag Queries
///
TEST_FUNCTION(chunk__set_chunk_as__updated) {
    Chunk chunk;
    initialize_chunk(&chunk, 1);
    munit_assert_false(is_chunk__updated(&chunk));
    set_chunk_as__updated(&chunk);
    munit_assert_true(is_chunk__updated(&chunk));
    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/world/chunk.h.spec.md
/// Section: 1.4.5 Flag Management (set_chunk_as__visually_updated,
///          set_chunk_as__visually_committed), 1.4.6 Flag Queries
///
TEST_FUNCTION(chunk__set_chunk_as__visually_updated_and_committed) {
    Chunk chunk;
    initialize_chunk(&chunk, 1);
    munit_assert_false(is_chunk__visually_updated(&chunk));
    set_chunk_as__visually_updated(&chunk);
    munit_assert_true(is_chunk__visually_updated(&chunk));
    set_chunk_as__visually_committed(&chunk);
    munit_assert_false(is_chunk__visually_updated(&chunk));
    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/world/chunk.h.spec.md
/// Section: 1.4.3 Tile Access (get_p_tile_from__chunk)
///
TEST_FUNCTION(chunk__get_p_tile_from__chunk__null_chunk_returns_null) {
    Local_Tile_Vector__3u8 local_tile;
    local_tile.x__u8 = 0;
    local_tile.y__u8 = 0;
    local_tile.z__u8 = 0;
    Tile *p_tile = get_p_tile_from__chunk(0, local_tile);
    munit_assert_ptr_null(p_tile);
    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/world/chunk.h.spec.md
/// Section: 1.4.3 Tile Access (get_p_tile_from__chunk)
///
TEST_FUNCTION(chunk__get_p_tile_from__chunk__valid_access) {
    Chunk chunk;
    initialize_chunk(&chunk, 1);
    Local_Tile_Vector__3u8 local_tile;
    local_tile.x__u8 = 0;
    local_tile.y__u8 = 0;
    local_tile.z__u8 = 0;
    Tile *p_tile = get_p_tile_from__chunk(&chunk, local_tile);
    munit_assert_ptr_not_null(p_tile);
    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/world/chunk.h.spec.md
/// Section: 1.4.3 Tile Access (set_tile_of__chunk, get_p_tile_from__chunk)
///
TEST_FUNCTION(chunk__set_tile_of__chunk__and_read_back) {
    Chunk chunk;
    initialize_chunk(&chunk, 1);
    Tile tile;
    set_tile_kind_of__tile(&tile, Tile_Kind__None);
    Local_Tile_Vector__3u8 local_tile;
    local_tile.x__u8 = 3;
    local_tile.y__u8 = 4;
    local_tile.z__u8 = 0;
    set_tile_of__chunk(&chunk, local_tile, &tile);
    Tile *p_tile = get_p_tile_from__chunk(&chunk, local_tile);
    munit_assert_ptr_not_null(p_tile);
    munit_assert_int(get_tile_kind_from__tile(p_tile), ==, Tile_Kind__None);
    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/world/chunk.h.spec.md
/// Section: 1.4.5 Flag Management (clear_chunk_flags)
///
TEST_FUNCTION(chunk__clear_chunk_flags__clears_all) {
    Chunk chunk;
    initialize_chunk(&chunk, 1);
    set_chunk_as__active(&chunk);
    set_chunk_as__updated(&chunk);
    set_chunk_as__visually_updated(&chunk);
    clear_chunk_flags(&chunk);
    munit_assert_false(is_chunk__active(&chunk));
    munit_assert_false(is_chunk__updated(&chunk));
    munit_assert_false(is_chunk__visually_updated(&chunk));
    return MUNIT_OK;
}

DEFINE_SUITE(chunk,
    INCLUDE_TEST__STATELESS(chunk__initialize_chunk__sets_uuid),
    INCLUDE_TEST__STATELESS(chunk__initialize_chunk__clears_flags),
    INCLUDE_TEST__STATELESS(chunk__set_chunk_as__active),
    INCLUDE_TEST__STATELESS(chunk__set_chunk_as__inactive),
    INCLUDE_TEST__STATELESS(chunk__set_chunk_as__awaiting_serialization__clears_active_and_deserialization),
    INCLUDE_TEST__STATELESS(chunk__set_chunk_as__awaiting_deserialization__clears_active_and_serialization),
    INCLUDE_TEST__STATELESS(chunk__set_chunk_as__updated),
    INCLUDE_TEST__STATELESS(chunk__set_chunk_as__visually_updated_and_committed),
    INCLUDE_TEST__STATELESS(chunk__get_p_tile_from__chunk__null_chunk_returns_null),
    INCLUDE_TEST__STATELESS(chunk__get_p_tile_from__chunk__valid_access),
    INCLUDE_TEST__STATELESS(chunk__set_tile_of__chunk__and_read_back),
    INCLUDE_TEST__STATELESS(chunk__clear_chunk_flags__clears_all),
    END_TESTS)
