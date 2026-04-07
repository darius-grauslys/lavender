#include <ui/test_suite_ui_ui_element.h>

#include <ui/ui_element.c>

///
/// Spec: core/ui/ui_element.h.spec.md
/// Section: 4.4.1 Initialization
///
TEST_FUNCTION(initialize_ui_element__sets_kind) {
    UI_Element ui_element;
    initialize_ui_element(
            &ui_element,
            0,
            0,
            0,
            UI_Element_Kind__Button,
            UI_FLAGS__BIT_IS_ENABLED);
    munit_assert_int(
            ui_element.the_kind_of_ui_element__this_is,
            ==,
            UI_Element_Kind__Button);
    return MUNIT_OK;
}

///
/// Spec: core/ui/ui_element.h.spec.md
/// Section: 4.4.1 Initialization
///
TEST_FUNCTION(initialize_ui_element__sets_flags) {
    UI_Element ui_element;
    initialize_ui_element(
            &ui_element,
            0,
            0,
            0,
            UI_Element_Kind__Button,
            UI_FLAGS__BIT_IS_ENABLED);
    munit_assert_true(is_ui_element__enabled(&ui_element));
    return MUNIT_OK;
}

///
/// Spec: core/ui/ui_element.h.spec.md
/// Section: 4.4.1 Initialization
///
TEST_FUNCTION(initialize_ui_element__sets_tree_pointers) {
    UI_Element parent;
    UI_Element child;
    UI_Element next;
    UI_Element ui_element;
    initialize_ui_element(
            &ui_element,
            &parent,
            &child,
            &next,
            UI_Element_Kind__Button,
            0);
    munit_assert_ptr_equal(get_parent_of__ui_element(&ui_element), &parent);
    munit_assert_ptr_equal(get_child_of__ui_element(&ui_element), &child);
    munit_assert_ptr_equal(get_next__ui_element(&ui_element), &next);
    return MUNIT_OK;
}

///
/// Spec: core/ui/ui_element.h.spec.md
/// Section: 4.4.1 Initialization
///
TEST_FUNCTION(initialize_ui_element__null_tree_pointers) {
    UI_Element ui_element;
    initialize_ui_element(
            &ui_element,
            0,
            0,
            0,
            UI_Element_Kind__Button,
            0);
    munit_assert_false(does_ui_element_have__parent(&ui_element));
    munit_assert_false(does_ui_element_have__child(&ui_element));
    munit_assert_false(does_ui_element_have__next(&ui_element));
    return MUNIT_OK;
}

///
/// Spec: core/ui/ui_element.h.spec.md
/// Section: 4.4.9 Kind Query
///
TEST_FUNCTION(is_ui_element_of__this_kind__returns_true_for_matching_kind) {
    UI_Element ui_element;
    initialize_ui_element(
            &ui_element,
            0,
            0,
            0,
            UI_Element_Kind__Slider,
            0);
    munit_assert_true(
            is_ui_element_of__this_kind(
                &ui_element,
                UI_Element_Kind__Slider));
    return MUNIT_OK;
}

///
/// Spec: core/ui/ui_element.h.spec.md
/// Section: 4.4.9 Kind Query
///
TEST_FUNCTION(is_ui_element_of__this_kind__returns_false_for_different_kind) {
    UI_Element ui_element;
    initialize_ui_element(
            &ui_element,
            0,
            0,
            0,
            UI_Element_Kind__Slider,
            0);
    munit_assert_false(
            is_ui_element_of__this_kind(
                &ui_element,
                UI_Element_Kind__Button));
    return MUNIT_OK;
}

///
/// Spec: core/ui/ui_element.h.spec.md
/// Section: 4.4.11 Flag Mutations
///
TEST_FUNCTION(set_ui_element_as__enabled__sets_flag) {
    UI_Element ui_element;
    initialize_ui_element(
            &ui_element,
            0, 0, 0,
            UI_Element_Kind__Button,
            0);
    munit_assert_false(is_ui_element__enabled(&ui_element));
    set_ui_element_as__enabled(&ui_element);
    munit_assert_true(is_ui_element__enabled(&ui_element));
    return MUNIT_OK;
}

///
/// Spec: core/ui/ui_element.h.spec.md
/// Section: 4.4.11 Flag Mutations
///
TEST_FUNCTION(set_ui_element_as__disabled__clears_flag) {
    UI_Element ui_element;
    initialize_ui_element(
            &ui_element,
            0, 0, 0,
            UI_Element_Kind__Button,
            UI_FLAGS__BIT_IS_ENABLED);
    munit_assert_true(is_ui_element__enabled(&ui_element));
    set_ui_element_as__disabled(&ui_element);
    munit_assert_false(is_ui_element__enabled(&ui_element));
    return MUNIT_OK;
}

///
/// Spec: core/ui/ui_element.h.spec.md
/// Section: 4.4.11 Flag Mutations
///
TEST_FUNCTION(set_ui_element_as__focused__sets_flag) {
    UI_Element ui_element;
    initialize_ui_element(
            &ui_element,
            0, 0, 0,
            UI_Element_Kind__Button,
            0);
    munit_assert_false(is_ui_element__focused(&ui_element));
    set_ui_element_as__focused(&ui_element);
    munit_assert_true(is_ui_element__focused(&ui_element));
    return MUNIT_OK;
}

///
/// Spec: core/ui/ui_element.h.spec.md
/// Section: 4.4.11 Flag Mutations
///
TEST_FUNCTION(set_ui_element_as__NOT_focused__clears_flag) {
    UI_Element ui_element;
    initialize_ui_element(
            &ui_element,
            0, 0, 0,
            UI_Element_Kind__Button,
            UI_FLAGS__BIT_IS_FOCUSED);
    set_ui_element_as__NOT_focused(&ui_element);
    munit_assert_false(is_ui_element__focused(&ui_element));
    return MUNIT_OK;
}

///
/// Spec: core/ui/ui_element.h.spec.md
/// Section: 4.4.11 Flag Mutations
///
TEST_FUNCTION(set_ui_element_as__being_held__sets_flag) {
    UI_Element ui_element;
    initialize_ui_element(
            &ui_element,
            0, 0, 0,
            UI_Element_Kind__Button,
            0);
    set_ui_element_as__being_held(&ui_element);
    munit_assert_true(is_ui_element__being_held(&ui_element));
    return MUNIT_OK;
}

///
/// Spec: core/ui/ui_element.h.spec.md
/// Section: 4.4.11 Flag Mutations
///
TEST_FUNCTION(set_ui_element_as__being_dragged__sets_flag) {
    UI_Element ui_element;
    initialize_ui_element(
            &ui_element,
            0, 0, 0,
            UI_Element_Kind__Draggable,
            0);
    set_ui_element_as__being_dragged(&ui_element);
    munit_assert_true(is_ui_element__being_dragged(&ui_element));
    return MUNIT_OK;
}

///
/// Spec: core/ui/ui_element.h.spec.md
/// Section: 4.4.11 Flag Mutations
///
TEST_FUNCTION(set_ui_element_as__dropped__clears_held_and_dragged) {
    UI_Element ui_element;
    initialize_ui_element(
            &ui_element,
            0, 0, 0,
            UI_Element_Kind__Draggable,
            0);
    set_ui_element_as__being_held(&ui_element);
    set_ui_element_as__being_dragged(&ui_element);
    munit_assert_true(is_ui_element__being_held(&ui_element));
    munit_assert_true(is_ui_element__being_dragged(&ui_element));
    set_ui_element_as__dropped(&ui_element);
    munit_assert_false(is_ui_element__being_held(&ui_element));
    munit_assert_false(is_ui_element__being_dragged(&ui_element));
    return MUNIT_OK;
}

///
/// Spec: core/ui/ui_element.h.spec.md
/// Section: 4.4.11 Flag Mutations
///
TEST_FUNCTION(set_ui_element_as__using_sprite__sets_flag) {
    UI_Element ui_element;
    initialize_ui_element(
            &ui_element,
            0, 0, 0,
            UI_Element_Kind__Button,
            0);
    set_ui_element_as__using_sprite(&ui_element);
    munit_assert_true(is_ui_element__using_sprite(&ui_element));
    munit_assert_false(is_ui_element__using_ui_tile_span(&ui_element));
    return MUNIT_OK;
}

///
/// Spec: core/ui/ui_element.h.spec.md
/// Section: 4.4.11 Flag Mutations
///
TEST_FUNCTION(set_ui_element_as__using_ui_tile_span__clears_flag) {
    UI_Element ui_element;
    initialize_ui_element(
            &ui_element,
            0, 0, 0,
            UI_Element_Kind__Button,
            UI_FLAGS__BIT_IS_USING__SPRITE_OR_UI_TILE_SPAN);
    set_ui_element_as__using_ui_tile_span(&ui_element);
    munit_assert_true(is_ui_element__using_ui_tile_span(&ui_element));
    munit_assert_false(is_ui_element__using_sprite(&ui_element));
    return MUNIT_OK;
}

///
/// Spec: core/ui/ui_element.h.spec.md
/// Section: 4.4.11 Flag Mutations
///
TEST_FUNCTION(set_ui_element_as__non_interactive__sets_flag) {
    UI_Element ui_element;
    initialize_ui_element(
            &ui_element,
            0, 0, 0,
            UI_Element_Kind__Button,
            0);
    set_ui_element_as__non_interactive(&ui_element);
    munit_assert_true(is_ui_element__non_interactive(&ui_element));
    return MUNIT_OK;
}

///
/// Spec: core/ui/ui_element.h.spec.md
/// Section: 4.4.11 Flag Mutations
///
TEST_FUNCTION(set_ui_element_as__interactive__clears_flag) {
    UI_Element ui_element;
    initialize_ui_element(
            &ui_element,
            0, 0, 0,
            UI_Element_Kind__Button,
            UI_FLAGS__BIT_IS_NON_INTERACTIVE);
    set_ui_element_as__interactive(&ui_element);
    munit_assert_false(is_ui_element__non_interactive(&ui_element));
    return MUNIT_OK;
}

///
/// Spec: core/ui/ui_element.h.spec.md
/// Section: 4.4.8 Linked List
///
TEST_FUNCTION(link_ui_element__sets_next_pointer) {
    UI_Element a;
    UI_Element b;
    initialize_ui_element(&a, 0, 0, 0, UI_Element_Kind__Button, 0);
    initialize_ui_element(&b, 0, 0, 0, UI_Element_Kind__Button, 0);
    link_ui_element_to__this_ui_element(&a, &b);
    munit_assert_ptr_equal(get_next__ui_element(&a), &b);
    return MUNIT_OK;
}

///
/// Spec: core/ui/ui_element.h.spec.md
/// Section: 4.4.8 Linked List
///
TEST_FUNCTION(link_ui_element__self_link_sets_null) {
    UI_Element a;
    initialize_ui_element(&a, 0, 0, 0, UI_Element_Kind__Button, 0);
    link_ui_element_to__this_ui_element(&a, &a);
    munit_assert_ptr_null(get_next__ui_element(&a));
    return MUNIT_OK;
}

///
/// Spec: core/ui/ui_element.h.spec.md
/// Section: 4.4.11 Flag Mutations
///
TEST_FUNCTION(set_ui_element_as__snapped_x_axis__sets_flag) {
    UI_Element ui_element;
    initialize_ui_element(
            &ui_element,
            0, 0, 0,
            UI_Element_Kind__Slider,
            0);
    set_ui_element_as__snapped_x_axis(&ui_element);
    munit_assert_true(is_ui_element__snapped_x_or_y_axis(&ui_element));
    return MUNIT_OK;
}

///
/// Spec: core/ui/ui_element.h.spec.md
/// Section: 4.4.11 Flag Mutations
///
TEST_FUNCTION(set_ui_element_as__snapped_y_axis__clears_flag) {
    UI_Element ui_element;
    initialize_ui_element(
            &ui_element,
            0, 0, 0,
            UI_Element_Kind__Slider,
            UI_FLAGS__BIT_IS_SNAPPED_X_OR_Y_AXIS);
    set_ui_element_as__snapped_y_axis(&ui_element);
    munit_assert_false(is_ui_element__snapped_x_or_y_axis(&ui_element));
    return MUNIT_OK;
}

///
/// Spec: core/ui/ui_element.h.spec.md
/// Section: 4.4.12 Handler Setters
///
TEST_FUNCTION(set_ui_element__compose_handler__also_sets_tile_span_mode) {
    UI_Element ui_element;
    initialize_ui_element(
            &ui_element,
            0, 0, 0,
            UI_Element_Kind__Button,
            UI_FLAGS__BIT_IS_USING__SPRITE_OR_UI_TILE_SPAN);
    munit_assert_true(is_ui_element__using_sprite(&ui_element));
    set_ui_element__compose_handler(
            &ui_element,
            m_ui_element__compose_handler__default);
    munit_assert_true(is_ui_element__using_ui_tile_span(&ui_element));
    return MUNIT_OK;
}

///
/// Spec: core/ui/ui_element.h.spec.md
/// Section: 4.4.13 Handler Queries
///
TEST_FUNCTION(does_ui_element_have__compose_handler__requires_tile_span_mode) {
    UI_Element ui_element;
    initialize_ui_element(
            &ui_element,
            0, 0, 0,
            UI_Element_Kind__Button,
            0);
    ui_element.m_ui_compose_handler =
        m_ui_element__compose_handler__default;
    set_ui_element_as__using_sprite(&ui_element);
    munit_assert_false(does_ui_element_have__compose_handler(&ui_element));
    set_ui_element_as__using_ui_tile_span(&ui_element);
    munit_assert_true(does_ui_element_have__compose_handler(&ui_element));
    return MUNIT_OK;
}

///
/// Spec: core/ui/ui_element.h.spec.md
/// Section: 4.4.6 Tree Management
///
TEST_FUNCTION(set_child_of__ui_element__sets_child_pointer) {
    UI_Element parent;
    UI_Element child;
    initialize_ui_element(&parent, 0, 0, 0, UI_Element_Kind__Button, 0);
    initialize_ui_element(&child, 0, 0, 0, UI_Element_Kind__Button, 0);
    set_child_of__ui_element(&parent, &child);
    munit_assert_ptr_equal(get_child_of__ui_element(&parent), &child);
    return MUNIT_OK;
}

///
/// Spec: core/ui/ui_element.h.spec.md
/// Section: 4.4.6 Tree Management
///
TEST_FUNCTION(set_parent_of__ui_element__sets_parent_pointer) {
    UI_Element parent;
    UI_Element child;
    initialize_ui_element(&parent, 0, 0, 0, UI_Element_Kind__Button, 0);
    initialize_ui_element(&child, 0, 0, 0, UI_Element_Kind__Button, 0);
    set_parent_of__ui_element(&child, &parent);
    munit_assert_ptr_equal(get_parent_of__ui_element(&child), &parent);
    return MUNIT_OK;
}

///
/// Spec: core/ui/ui_element.h.spec.md
/// Section: 4.4.8 Linked List
///
TEST_FUNCTION(iterate_to_next__ui_element__advances_and_returns_current) {
    UI_Element a;
    UI_Element b;
    initialize_ui_element(&a, 0, 0, 0, UI_Element_Kind__Button, 0);
    initialize_ui_element(&b, 0, 0, 0, UI_Element_Kind__Button, 0);
    link_ui_element_to__this_ui_element(&a, &b);
    UI_Element *p_current = &a;
    UI_Element *p_result = iterate_to_next__ui_element(&p_current);
    munit_assert_ptr_equal(p_result, &a);
    munit_assert_ptr_equal(p_current, &b);
    return MUNIT_OK;
}

///
/// Spec: core/ui/ui_element.h.spec.md
/// Section: 4.4.8 Linked List
///
TEST_FUNCTION(iterate_to_next__ui_element__null_safe) {
    UI_Element *p_current = 0;
    UI_Element *p_result = iterate_to_next__ui_element(&p_current);
    munit_assert_ptr_null(p_result);
    munit_assert_ptr_null(p_current);
    return MUNIT_OK;
}

///
/// Spec: core/ui/ui_element.h.spec.md
/// Section: 4.4.12 Handler Setters, 4.4.13 Handler Queries
///
TEST_FUNCTION(handler_setters_and_queries__clicked) {
    UI_Element ui_element;
    initialize_ui_element(
            &ui_element, 0, 0, 0,
            UI_Element_Kind__Button, 0);
    munit_assert_false(does_ui_element_have__clicked_handler(&ui_element));
    set_ui_element__clicked_handler(&ui_element,
            (m_UI_Clicked)0x1);
    munit_assert_true(does_ui_element_have__clicked_handler(&ui_element));
    return MUNIT_OK;
}

///
/// Spec: core/ui/ui_element.h.spec.md
/// Section: 4.4.12 Handler Setters, 4.4.13 Handler Queries
///
TEST_FUNCTION(handler_setters_and_queries__dragged) {
    UI_Element ui_element;
    initialize_ui_element(
            &ui_element, 0, 0, 0,
            UI_Element_Kind__Draggable, 0);
    munit_assert_false(does_ui_element_have__dragged_handler(&ui_element));
    set_ui_element__dragged_handler(&ui_element,
            (m_UI_Dragged)0x1);
    munit_assert_true(does_ui_element_have__dragged_handler(&ui_element));
    return MUNIT_OK;
}

///
/// Spec: core/ui/ui_element.h.spec.md
/// Section: 4.4.12 Handler Setters, 4.4.13 Handler Queries
///
TEST_FUNCTION(handler_setters_and_queries__dropped) {
    UI_Element ui_element;
    initialize_ui_element(
            &ui_element, 0, 0, 0,
            UI_Element_Kind__Draggable, 0);
    munit_assert_false(does_ui_element_have__dropped_handler(&ui_element));
    set_ui_element__dropped_handler(&ui_element,
            (m_UI_Dropped)0x1);
    munit_assert_true(does_ui_element_have__dropped_handler(&ui_element));
    return MUNIT_OK;
}

///
/// Spec: core/ui/ui_element.h.spec.md
/// Section: 4.4.12 Handler Setters, 4.4.13 Handler Queries
///
TEST_FUNCTION(handler_setters_and_queries__held) {
    UI_Element ui_element;
    initialize_ui_element(
            &ui_element, 0, 0, 0,
            UI_Element_Kind__Button, 0);
    munit_assert_false(does_ui_element_have__held_handler(&ui_element));
    set_ui_element__held_handler(&ui_element,
            (m_UI_Held)0x1);
    munit_assert_true(does_ui_element_have__held_handler(&ui_element));
    return MUNIT_OK;
}

///
/// Spec: core/ui/ui_element.h.spec.md
/// Section: 4.4.12 Handler Setters, 4.4.13 Handler Queries
///
TEST_FUNCTION(handler_setters_and_queries__typed) {
    UI_Element ui_element;
    initialize_ui_element(
            &ui_element, 0, 0, 0,
            UI_Element_Kind__Text_Box, 0);
    munit_assert_false(does_ui_element_have__typed_handler(&ui_element));
    set_ui_element__typed_handler(&ui_element,
            (m_UI_Typed)0x1);
    munit_assert_true(does_ui_element_have__typed_handler(&ui_element));
    return MUNIT_OK;
}

///
/// Spec: core/ui/ui_element.h.spec.md
/// Section: 4.4.12 Handler Setters, 4.4.13 Handler Queries
///
TEST_FUNCTION(handler_setters_and_queries__transformed) {
    UI_Element ui_element;
    initialize_ui_element(
            &ui_element, 0, 0, 0,
            UI_Element_Kind__Button, 0);
    munit_assert_false(
            does_ui_element_have__transformed_handler(&ui_element));
    set_ui_element__transformed_handler(&ui_element,
            (m_UI_Transformed)0x1);
    munit_assert_true(
            does_ui_element_have__transformed_handler(&ui_element));
    return MUNIT_OK;
}

///
/// Spec: core/ui/ui_element.h.spec.md
/// Section: 4.4.12 Handler Setters, 4.4.13 Handler Queries
///
TEST_FUNCTION(handler_setters_and_queries__dispose) {
    UI_Element ui_element;
    initialize_ui_element(
            &ui_element, 0, 0, 0,
            UI_Element_Kind__Button, 0);
    munit_assert_false(does_ui_element_have__dispose_handler(&ui_element));
    set_ui_element__dispose_handler(&ui_element,
            (m_UI_Dispose)0x1);
    munit_assert_true(does_ui_element_have__dispose_handler(&ui_element));
    return MUNIT_OK;
}

///
/// Spec: core/ui/ui_element.h.spec.md
/// Section: 4.4.12 Handler Setters, 4.4.13 Handler Queries
///
TEST_FUNCTION(handler_setters_and_queries__receive_drop) {
    UI_Element ui_element;
    initialize_ui_element(
            &ui_element, 0, 0, 0,
            UI_Element_Kind__Drop_Zone, 0);
    munit_assert_false(
            does_ui_element_have__receive_drop_handler(&ui_element));
    set_ui_element__receive_drop_handler(&ui_element,
            (m_UI_Receive_Drop)0x1);
    munit_assert_true(
            does_ui_element_have__receive_drop_handler(&ui_element));
    return MUNIT_OK;
}

///
/// Spec: core/ui/ui_element.h.spec.md
/// Section: 4.4.10 Flag Queries
///
TEST_FUNCTION(get_ui_element__flags__returns_current_flags) {
    UI_Element ui_element;
    initialize_ui_element(
            &ui_element, 0, 0, 0,
            UI_Element_Kind__Button,
            UI_FLAGS__BIT_IS_ENABLED);
    UI_Flags__u16 flags = get_ui_element__flags(&ui_element);
    munit_assert_uint16(flags & UI_FLAGS__BIT_IS_ENABLED, ==,
            UI_FLAGS__BIT_IS_ENABLED);
    return MUNIT_OK;
}

DEFINE_SUITE(ui_element,
    INCLUDE_TEST__STATELESS(initialize_ui_element__sets_kind),
    INCLUDE_TEST__STATELESS(initialize_ui_element__sets_flags),
    INCLUDE_TEST__STATELESS(initialize_ui_element__sets_tree_pointers),
    INCLUDE_TEST__STATELESS(initialize_ui_element__null_tree_pointers),
    INCLUDE_TEST__STATELESS(is_ui_element_of__this_kind__returns_true_for_matching_kind),
    INCLUDE_TEST__STATELESS(is_ui_element_of__this_kind__returns_false_for_different_kind),
    INCLUDE_TEST__STATELESS(set_ui_element_as__enabled__sets_flag),
    INCLUDE_TEST__STATELESS(set_ui_element_as__disabled__clears_flag),
    INCLUDE_TEST__STATELESS(set_ui_element_as__focused__sets_flag),
    INCLUDE_TEST__STATELESS(set_ui_element_as__NOT_focused__clears_flag),
    INCLUDE_TEST__STATELESS(set_ui_element_as__being_held__sets_flag),
    INCLUDE_TEST__STATELESS(set_ui_element_as__being_dragged__sets_flag),
    INCLUDE_TEST__STATELESS(set_ui_element_as__dropped__clears_held_and_dragged),
    INCLUDE_TEST__STATELESS(set_ui_element_as__using_sprite__sets_flag),
    INCLUDE_TEST__STATELESS(set_ui_element_as__using_ui_tile_span__clears_flag),
    INCLUDE_TEST__STATELESS(set_ui_element_as__non_interactive__sets_flag),
    INCLUDE_TEST__STATELESS(set_ui_element_as__interactive__clears_flag),
    INCLUDE_TEST__STATELESS(link_ui_element__sets_next_pointer),
    INCLUDE_TEST__STATELESS(link_ui_element__self_link_sets_null),
    INCLUDE_TEST__STATELESS(set_ui_element_as__snapped_x_axis__sets_flag),
    INCLUDE_TEST__STATELESS(set_ui_element_as__snapped_y_axis__clears_flag),
    INCLUDE_TEST__STATELESS(set_ui_element__compose_handler__also_sets_tile_span_mode),
    INCLUDE_TEST__STATELESS(does_ui_element_have__compose_handler__requires_tile_span_mode),
    INCLUDE_TEST__STATELESS(set_child_of__ui_element__sets_child_pointer),
    INCLUDE_TEST__STATELESS(set_parent_of__ui_element__sets_parent_pointer),
    INCLUDE_TEST__STATELESS(iterate_to_next__ui_element__advances_and_returns_current),
    INCLUDE_TEST__STATELESS(iterate_to_next__ui_element__null_safe),
    INCLUDE_TEST__STATELESS(handler_setters_and_queries__clicked),
    INCLUDE_TEST__STATELESS(handler_setters_and_queries__dragged),
    INCLUDE_TEST__STATELESS(handler_setters_and_queries__dropped),
    INCLUDE_TEST__STATELESS(handler_setters_and_queries__held),
    INCLUDE_TEST__STATELESS(handler_setters_and_queries__typed),
    INCLUDE_TEST__STATELESS(handler_setters_and_queries__transformed),
    INCLUDE_TEST__STATELESS(handler_setters_and_queries__dispose),
    INCLUDE_TEST__STATELESS(handler_setters_and_queries__receive_drop),
    INCLUDE_TEST__STATELESS(get_ui_element__flags__returns_current_flags),
    END_TESTS)
