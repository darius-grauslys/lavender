#include <ui/test_suite_ui_ui_tile_span.h>

#include <ui/ui_tile_span.c>

///
/// Spec:   docs/specs/core/ui/ui_tile_span.h.spec.md
/// Section: 21.4 Functions — initialize_ui_tile_span_as__empty
///
TEST_FUNCTION(initialize_ui_tile_span_as__empty__all_tiles_none) {
    UI_Tile_Span span;
    initialize_ui_tile_span_as__empty(&span);
    for (int i = 0; i < 4; i++) {
        munit_assert_int(
                span.ui_tile__corners[i].the_kind_of__ui_tile,
                ==,
                UI_Tile_Kind__None);
        munit_assert_int(
                span.ui_tile__edges[i].the_kind_of__ui_tile,
                ==,
                UI_Tile_Kind__None);
    }
    munit_assert_int(
            span.ui_tile__fill.the_kind_of__ui_tile,
            ==,
            UI_Tile_Kind__None);
    return MUNIT_OK;
}

///
/// Spec:   docs/specs/core/ui/ui_tile_span.h.spec.md
/// Section: 21.4 Functions — initialize_ui_tile_span
///
TEST_FUNCTION(initialize_ui_tile_span__sets_corners_edges_fill) {
    UI_Tile_Span span;
    UI_Tile corners[4];
    UI_Tile edges[4];
    UI_Tile fill;
    for (int i = 0; i < 4; i++) {
        initialize_ui_tile(&corners[i], (UI_Tile_Kind)(i + 1), 0);
        initialize_ui_tile(&edges[i], (UI_Tile_Kind)(i + 10), 0);
    }
    initialize_ui_tile(&fill, (UI_Tile_Kind)99, 0);
    initialize_ui_tile_span(&span, corners, edges, fill);
    for (int i = 0; i < 4; i++) {
        munit_assert_int(
                span.ui_tile__corners[i].the_kind_of__ui_tile,
                ==,
                i + 1);
        munit_assert_int(
                span.ui_tile__edges[i].the_kind_of__ui_tile,
                ==,
                i + 10);
    }
    munit_assert_int(
            span.ui_tile__fill.the_kind_of__ui_tile,
            ==,
            99);
    return MUNIT_OK;
}

///
/// Spec:    docs/specs/core/ui/ui_tile_span.h.spec.md
/// Section: 21.5.1 9-Slice Sampling — Corner positions
///
TEST_FUNCTION(get_ui_tile_of__ui_tile_span__returns_corner_top_left) {
    UI_Tile_Span span;
    UI_Tile corners[4];
    UI_Tile edges[4];
    UI_Tile fill;
    for (int i = 0; i < 4; i++) {
        initialize_ui_tile(&corners[i], (UI_Tile_Kind)(i + 1), 0);
        initialize_ui_tile(&edges[i], (UI_Tile_Kind)(i + 10), 0);
    }
    initialize_ui_tile(&fill, (UI_Tile_Kind)99, 0);
    initialize_ui_tile_span(&span, corners, edges, fill);
    const UI_Tile *p_tile =
        get_ui_tile_of__ui_tile_span(&span, 4, 4, 0, 0);
    munit_assert_not_null(p_tile);
    munit_assert_int(
            p_tile->the_kind_of__ui_tile,
            ==,
            span.ui_tile__corner__top_left.the_kind_of__ui_tile);
    return MUNIT_OK;
}

///
/// Spec:    docs/specs/core/ui/ui_tile_span.h.spec.md
/// Section: 21.5.1 9-Slice Sampling — Corner positions
///
TEST_FUNCTION(get_ui_tile_of__ui_tile_span__returns_corner_top_right) {
    UI_Tile_Span span;
    UI_Tile corners[4];
    UI_Tile edges[4];
    UI_Tile fill;
    for (int i = 0; i < 4; i++) {
        initialize_ui_tile(&corners[i], (UI_Tile_Kind)(i + 1), 0);
        initialize_ui_tile(&edges[i], (UI_Tile_Kind)(i + 10), 0);
    }
    initialize_ui_tile(&fill, (UI_Tile_Kind)99, 0);
    initialize_ui_tile_span(&span, corners, edges, fill);
    const UI_Tile *p_tile =
        get_ui_tile_of__ui_tile_span(&span, 4, 4, 3, 0);
    munit_assert_not_null(p_tile);
    munit_assert_int(
            p_tile->the_kind_of__ui_tile,
            ==,
            span.ui_tile__corner__top_right.the_kind_of__ui_tile);
    return MUNIT_OK;
}

///
/// Spec:    docs/specs/core/ui/ui_tile_span.h.spec.md
/// Section: 21.5.1 9-Slice Sampling — Corner positions
///
TEST_FUNCTION(get_ui_tile_of__ui_tile_span__returns_corner_bottom_left) {
    UI_Tile_Span span;
    UI_Tile corners[4];
    UI_Tile edges[4];
    UI_Tile fill;
    for (int i = 0; i < 4; i++) {
        initialize_ui_tile(&corners[i], (UI_Tile_Kind)(i + 1), 0);
        initialize_ui_tile(&edges[i], (UI_Tile_Kind)(i + 10), 0);
    }
    initialize_ui_tile(&fill, (UI_Tile_Kind)99, 0);
    initialize_ui_tile_span(&span, corners, edges, fill);
    const UI_Tile *p_tile =
        get_ui_tile_of__ui_tile_span(&span, 4, 4, 0, 3);
    munit_assert_not_null(p_tile);
    munit_assert_int(
            p_tile->the_kind_of__ui_tile,
            ==,
            span.ui_tile__corner__bottom_left.the_kind_of__ui_tile);
    return MUNIT_OK;
}

///
/// Spec:    docs/specs/core/ui/ui_tile_span.h.spec.md
/// Section: 21.5.1 9-Slice Sampling — Corner positions
///
TEST_FUNCTION(get_ui_tile_of__ui_tile_span__returns_corner_bottom_right) {
    UI_Tile_Span span;
    UI_Tile corners[4];
    UI_Tile edges[4];
    UI_Tile fill;
    for (int i = 0; i < 4; i++) {
        initialize_ui_tile(&corners[i], (UI_Tile_Kind)(i + 1), 0);
        initialize_ui_tile(&edges[i], (UI_Tile_Kind)(i + 10), 0);
    }
    initialize_ui_tile(&fill, (UI_Tile_Kind)99, 0);
    initialize_ui_tile_span(&span, corners, edges, fill);
    const UI_Tile *p_tile =
        get_ui_tile_of__ui_tile_span(&span, 4, 4, 3, 3);
    munit_assert_not_null(p_tile);
    munit_assert_int(
            p_tile->the_kind_of__ui_tile,
            ==,
            span.ui_tile__corner__bottom_right.the_kind_of__ui_tile);
    return MUNIT_OK;
}

///
/// Spec:    docs/specs/core/ui/ui_tile_span.h.spec.md
/// Section: 21.5.1 9-Slice Sampling — Border positions
///
TEST_FUNCTION(get_ui_tile_of__ui_tile_span__returns_edge_top) {
    UI_Tile_Span span;
    UI_Tile corners[4];
    UI_Tile edges[4];
    UI_Tile fill;
    for (int i = 0; i < 4; i++) {
        initialize_ui_tile(&corners[i], (UI_Tile_Kind)(i + 1), 0);
        initialize_ui_tile(&edges[i], (UI_Tile_Kind)(i + 10), 0);
    }
    initialize_ui_tile(&fill, (UI_Tile_Kind)99, 0);
    initialize_ui_tile_span(&span, corners, edges, fill);
    const UI_Tile *p_tile =
        get_ui_tile_of__ui_tile_span(&span, 4, 4, 1, 0);
    munit_assert_not_null(p_tile);
    munit_assert_int(
            p_tile->the_kind_of__ui_tile,
            ==,
            span.ui_tile__edge__top.the_kind_of__ui_tile);
    return MUNIT_OK;
}

///
/// Spec:    docs/specs/core/ui/ui_tile_span.h.spec.md
/// Section: 21.5.1 9-Slice Sampling — Border positions
///
TEST_FUNCTION(get_ui_tile_of__ui_tile_span__returns_edge_bottom) {
    UI_Tile_Span span;
    UI_Tile corners[4];
    UI_Tile edges[4];
    UI_Tile fill;
    for (int i = 0; i < 4; i++) {
        initialize_ui_tile(&corners[i], (UI_Tile_Kind)(i + 1), 0);
        initialize_ui_tile(&edges[i], (UI_Tile_Kind)(i + 10), 0);
    }
    initialize_ui_tile(&fill, (UI_Tile_Kind)99, 0);
    initialize_ui_tile_span(&span, corners, edges, fill);
    const UI_Tile *p_tile =
        get_ui_tile_of__ui_tile_span(&span, 4, 4, 2, 3);
    munit_assert_not_null(p_tile);
    munit_assert_int(
            p_tile->the_kind_of__ui_tile,
            ==,
            span.ui_tile__edge__bottom.the_kind_of__ui_tile);
    return MUNIT_OK;
}

///
/// Spec:    docs/specs/core/ui/ui_tile_span.h.spec.md
/// Section: 21.5.1 9-Slice Sampling — Border positions
///
TEST_FUNCTION(get_ui_tile_of__ui_tile_span__returns_edge_left) {
    UI_Tile_Span span;
    UI_Tile corners[4];
    UI_Tile edges[4];
    UI_Tile fill;
    for (int i = 0; i < 4; i++) {
        initialize_ui_tile(&corners[i], (UI_Tile_Kind)(i + 1), 0);
        initialize_ui_tile(&edges[i], (UI_Tile_Kind)(i + 10), 0);
    }
    initialize_ui_tile(&fill, (UI_Tile_Kind)99, 0);
    initialize_ui_tile_span(&span, corners, edges, fill);
    const UI_Tile *p_tile =
        get_ui_tile_of__ui_tile_span(&span, 4, 4, 0, 2);
    munit_assert_not_null(p_tile);
    munit_assert_int(
            p_tile->the_kind_of__ui_tile,
            ==,
            span.ui_tile__edge__left.the_kind_of__ui_tile);
    return MUNIT_OK;
}

///
/// Spec:    docs/specs/core/ui/ui_tile_span.h.spec.md
/// Section: 21.5.1 9-Slice Sampling — Border positions
///
TEST_FUNCTION(get_ui_tile_of__ui_tile_span__returns_edge_right) {
    UI_Tile_Span span;
    UI_Tile corners[4];
    UI_Tile edges[4];
    UI_Tile fill;
    for (int i = 0; i < 4; i++) {
        initialize_ui_tile(&corners[i], (UI_Tile_Kind)(i + 1), 0);
        initialize_ui_tile(&edges[i], (UI_Tile_Kind)(i + 10), 0);
    }
    initialize_ui_tile(&fill, (UI_Tile_Kind)99, 0);
    initialize_ui_tile_span(&span, corners, edges, fill);
    const UI_Tile *p_tile =
        get_ui_tile_of__ui_tile_span(&span, 4, 4, 3, 1);
    munit_assert_not_null(p_tile);
    munit_assert_int(
            p_tile->the_kind_of__ui_tile,
            ==,
            span.ui_tile__edge__right.the_kind_of__ui_tile);
    return MUNIT_OK;
}

///
/// Spec:    docs/specs/core/ui/ui_tile_span.h.spec.md
/// Section: 21.5.1 9-Slice Sampling — Interior positions
///
TEST_FUNCTION(get_ui_tile_of__ui_tile_span__returns_fill_for_interior) {
    UI_Tile_Span span;
    UI_Tile corners[4];
    UI_Tile edges[4];
    UI_Tile fill;
    for (int i = 0; i < 4; i++) {
        initialize_ui_tile(&corners[i], (UI_Tile_Kind)(i + 1), 0);
        initialize_ui_tile(&edges[i], (UI_Tile_Kind)(i + 10), 0);
    }
    initialize_ui_tile(&fill, (UI_Tile_Kind)99, 0);
    initialize_ui_tile_span(&span, corners, edges, fill);
    const UI_Tile *p_tile =
        get_ui_tile_of__ui_tile_span(&span, 4, 4, 1, 1);
    munit_assert_not_null(p_tile);
    munit_assert_int(
            p_tile->the_kind_of__ui_tile,
            ==,
            99);
    return MUNIT_OK;
}

///
/// Spec:   docs/specs/core/ui/ui_tile_span.h.spec.md
/// Section: 21.4 Functions — initialize_ui_tile_span_as__empty (size field)
///
TEST_FUNCTION(initialize_ui_tile_span_as__empty__sets_size_to_zero) {
    UI_Tile_Span span;
    initialize_ui_tile_span_as__empty(&span);
    munit_assert_int(
            span.size_of__ui_tile_in__8x8_tiles__u8,
            ==,
            0);
    return MUNIT_OK;
}

///
/// Spec:    docs/specs/core/ui/ui_tile_span.h.spec.md
/// Section: 21.5.2 9-Slice Sampling (16x16) — Corner positions
///
TEST_FUNCTION(get_ui_tile_of__ui_tile_span__16x16__returns_corner_top_left) {
    UI_Tile_Span span;
    UI_Tile corners[4];
    UI_Tile edges[4];
    UI_Tile fill;
    for (int i = 0; i < 4; i++) {
        initialize_ui_tile(&corners[i], (UI_Tile_Kind)(i + 1), 0);
        initialize_ui_tile(&edges[i], (UI_Tile_Kind)(i + 10), 0);
    }
    initialize_ui_tile(&fill, (UI_Tile_Kind)99, 0);
    initialize_ui_tile_span(&span, corners, edges, fill);
    span.size_of__ui_tile_in__8x8_tiles__u8 = 2;
    const UI_Tile *p_tile_00 =
        get_ui_tile_of__ui_tile_span(&span, 8, 8, 0, 0);
    munit_assert_not_null(p_tile_00);
    munit_assert_int(
            p_tile_00->the_kind_of__ui_tile,
            ==,
            span.ui_tile__corner__top_left.the_kind_of__ui_tile);
    const UI_Tile *p_tile_11 =
        get_ui_tile_of__ui_tile_span(&span, 8, 8, 1, 1);
    munit_assert_not_null(p_tile_11);
    munit_assert_int(
            p_tile_11->the_kind_of__ui_tile,
            ==,
            span.ui_tile__corner__top_left.the_kind_of__ui_tile);
    return MUNIT_OK;
}

///
/// Spec:    docs/specs/core/ui/ui_tile_span.h.spec.md
/// Section: 21.5.2 9-Slice Sampling (16x16) — Corner positions
///
TEST_FUNCTION(get_ui_tile_of__ui_tile_span__16x16__returns_corner_bottom_right) {
    UI_Tile_Span span;
    UI_Tile corners[4];
    UI_Tile edges[4];
    UI_Tile fill;
    for (int i = 0; i < 4; i++) {
        initialize_ui_tile(&corners[i], (UI_Tile_Kind)(i + 1), 0);
        initialize_ui_tile(&edges[i], (UI_Tile_Kind)(i + 10), 0);
    }
    initialize_ui_tile(&fill, (UI_Tile_Kind)99, 0);
    initialize_ui_tile_span(&span, corners, edges, fill);
    span.size_of__ui_tile_in__8x8_tiles__u8 = 2;
    const UI_Tile *p_tile_66 =
        get_ui_tile_of__ui_tile_span(&span, 8, 8, 6, 6);
    munit_assert_not_null(p_tile_66);
    munit_assert_int(
            p_tile_66->the_kind_of__ui_tile,
            ==,
            span.ui_tile__corner__bottom_right.the_kind_of__ui_tile);
    const UI_Tile *p_tile_77 =
        get_ui_tile_of__ui_tile_span(&span, 8, 8, 7, 7);
    munit_assert_not_null(p_tile_77);
    munit_assert_int(
            p_tile_77->the_kind_of__ui_tile,
            ==,
            span.ui_tile__corner__bottom_right.the_kind_of__ui_tile);
    return MUNIT_OK;
}

///
/// Spec:    docs/specs/core/ui/ui_tile_span.h.spec.md
/// Section: 21.5.2 9-Slice Sampling (16x16) — Border positions
///
TEST_FUNCTION(get_ui_tile_of__ui_tile_span__16x16__returns_edge_top) {
    UI_Tile_Span span;
    UI_Tile corners[4];
    UI_Tile edges[4];
    UI_Tile fill;
    for (int i = 0; i < 4; i++) {
        initialize_ui_tile(&corners[i], (UI_Tile_Kind)(i + 1), 0);
        initialize_ui_tile(&edges[i], (UI_Tile_Kind)(i + 10), 0);
    }
    initialize_ui_tile(&fill, (UI_Tile_Kind)99, 0);
    initialize_ui_tile_span(&span, corners, edges, fill);
    span.size_of__ui_tile_in__8x8_tiles__u8 = 2;
    const UI_Tile *p_tile =
        get_ui_tile_of__ui_tile_span(&span, 8, 8, 3, 0);
    munit_assert_not_null(p_tile);
    munit_assert_int(
            p_tile->the_kind_of__ui_tile,
            ==,
            span.ui_tile__edge__top.the_kind_of__ui_tile);
    return MUNIT_OK;
}

///
/// Spec:    docs/specs/core/ui/ui_tile_span.h.spec.md
/// Section: 21.5.2 9-Slice Sampling (16x16) — Border positions
///
TEST_FUNCTION(get_ui_tile_of__ui_tile_span__16x16__returns_edge_left) {
    UI_Tile_Span span;
    UI_Tile corners[4];
    UI_Tile edges[4];
    UI_Tile fill;
    for (int i = 0; i < 4; i++) {
        initialize_ui_tile(&corners[i], (UI_Tile_Kind)(i + 1), 0);
        initialize_ui_tile(&edges[i], (UI_Tile_Kind)(i + 10), 0);
    }
    initialize_ui_tile(&fill, (UI_Tile_Kind)99, 0);
    initialize_ui_tile_span(&span, corners, edges, fill);
    span.size_of__ui_tile_in__8x8_tiles__u8 = 2;
    const UI_Tile *p_tile =
        get_ui_tile_of__ui_tile_span(&span, 8, 8, 0, 3);
    munit_assert_not_null(p_tile);
    munit_assert_int(
            p_tile->the_kind_of__ui_tile,
            ==,
            span.ui_tile__edge__left.the_kind_of__ui_tile);
    return MUNIT_OK;
}

///
/// Spec:    docs/specs/core/ui/ui_tile_span.h.spec.md
/// Section: 21.5.2 9-Slice Sampling (16x16) — Interior positions
///
TEST_FUNCTION(get_ui_tile_of__ui_tile_span__16x16__returns_fill_for_interior) {
    UI_Tile_Span span;
    UI_Tile corners[4];
    UI_Tile edges[4];
    UI_Tile fill;
    for (int i = 0; i < 4; i++) {
        initialize_ui_tile(&corners[i], (UI_Tile_Kind)(i + 1), 0);
        initialize_ui_tile(&edges[i], (UI_Tile_Kind)(i + 10), 0);
    }
    initialize_ui_tile(&fill, (UI_Tile_Kind)99, 0);
    initialize_ui_tile_span(&span, corners, edges, fill);
    span.size_of__ui_tile_in__8x8_tiles__u8 = 2;
    const UI_Tile *p_tile =
        get_ui_tile_of__ui_tile_span(&span, 8, 8, 3, 3);
    munit_assert_not_null(p_tile);
    munit_assert_int(
            p_tile->the_kind_of__ui_tile,
            ==,
            99);
    return MUNIT_OK;
}

DEFINE_SUITE(ui_tile_span,
    INCLUDE_TEST__STATELESS(initialize_ui_tile_span_as__empty__all_tiles_none),
    INCLUDE_TEST__STATELESS(initialize_ui_tile_span__sets_corners_edges_fill),
    INCLUDE_TEST__STATELESS(get_ui_tile_of__ui_tile_span__returns_corner_top_left),
    INCLUDE_TEST__STATELESS(get_ui_tile_of__ui_tile_span__returns_corner_top_right),
    INCLUDE_TEST__STATELESS(get_ui_tile_of__ui_tile_span__returns_corner_bottom_left),
    INCLUDE_TEST__STATELESS(get_ui_tile_of__ui_tile_span__returns_corner_bottom_right),
    INCLUDE_TEST__STATELESS(get_ui_tile_of__ui_tile_span__returns_edge_top),
    INCLUDE_TEST__STATELESS(get_ui_tile_of__ui_tile_span__returns_edge_bottom),
    INCLUDE_TEST__STATELESS(get_ui_tile_of__ui_tile_span__returns_edge_left),
    INCLUDE_TEST__STATELESS(get_ui_tile_of__ui_tile_span__returns_edge_right),
    INCLUDE_TEST__STATELESS(get_ui_tile_of__ui_tile_span__returns_fill_for_interior),
    INCLUDE_TEST__STATELESS(initialize_ui_tile_span_as__empty__sets_size_to_zero),
    INCLUDE_TEST__STATELESS(get_ui_tile_of__ui_tile_span__16x16__returns_corner_top_left),
    INCLUDE_TEST__STATELESS(get_ui_tile_of__ui_tile_span__16x16__returns_corner_bottom_right),
    INCLUDE_TEST__STATELESS(get_ui_tile_of__ui_tile_span__16x16__returns_edge_top),
    INCLUDE_TEST__STATELESS(get_ui_tile_of__ui_tile_span__16x16__returns_edge_left),
    INCLUDE_TEST__STATELESS(get_ui_tile_of__ui_tile_span__16x16__returns_fill_for_interior),
    END_TESTS)
