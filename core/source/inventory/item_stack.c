#include "defines_weak.h"
#include "game.h"
#include "inventory/item_manager.h"
#include "numerics.h"
#include "serialization/serialization_header.h"
#include <inventory/item_stack.h>
#include <inventory/item.h>

void initialize_item_stack(
        Item_Stack *p_item_stack,
        Item item,
        Identifier__u16 identifier_for__item_stack,
        Quantity__u8 quantity_of__items,
        Quantity__u8 max_quantity_of__items) {
#ifndef NDEBUG
    if (!p_item_stack) {
        debug_abort("initialize_item_stack, p_item_stack is null.");
        return;
    }
#endif
    initialize_serialization_header(
            &p_item_stack->_serialization_header, 
            identifier_for__item_stack,
            sizeof(Item_Stack));
    p_item_stack->item = item;
    p_item_stack->quantity_of__items =
        quantity_of__items;
    p_item_stack->max_quantity_of__items =
        max_quantity_of__items;
}

void initialize_item_stack_as__empty(
        Item_Stack *p_item_stack,
        Identifier__u32 identifier_for__item_stack__u32) {
#ifndef NDEBUG
    if (!p_item_stack) {
        debug_abort("initialize_item_stack__as_allocated, p_item_stack is null.");
        return;
    }
#endif
    initialize_serialization_header(
            &p_item_stack->_serialization_header, 
            identifier_for__item_stack__u32,
            sizeof(Item_Stack));
    p_item_stack->item = get_item__empty();
    p_item_stack->quantity_of__items = 0;
    p_item_stack->max_quantity_of__items = 0;
}

void serialize_item_stack(
        PLATFORM_File_System_Context *p_PLATFORM_file_system_context,
        Serialization_Request *p_serialization_request,
        Item_Stack *p_item_stack) {

    void *p_file_handler =
        p_serialization_request
        ->p_file_handler;

    enum PLATFORM_Write_File_Error error = 
        PLATFORM_write_file(
                p_PLATFORM_file_system_context,
                (u8*)&p_item_stack->_serialization_header, 
                sizeof(Serialization_Header), 
                1, 
                p_file_handler);
    if (error) {
        debug_error("serialize_item_stack, error: %d", error);
        return;
    }

    struct {
        enum Item_Kind the_kind_of__item;
        Quantity__u8 quantity_of__items;
        Quantity__u8 max_quantity_of__items;
    } field;

    field.the_kind_of__item = 
        p_item_stack->item.the_kind_of_item__this_item_is;
    field.quantity_of__items =
        p_item_stack->quantity_of__items;
    field.max_quantity_of__items =
        p_item_stack->max_quantity_of__items;

    error = PLATFORM_write_file(
                p_PLATFORM_file_system_context,
                (u8*)&field, 
                sizeof(field), 
                1, 
                p_file_handler);
    if (error) {
        debug_error("serialize_item_stack, error: %d", error);
        return;
    }
}

void deserialize_item_stack(
        PLATFORM_File_System_Context *p_PLATFORM_file_system_context,
        Item_Manager *p_item_manager,
        Serialization_Request *p_serialization_request,
        Item_Stack *p_item_stack) {

    void *p_file_handler =
        p_serialization_request
        ->p_file_handler;

    Quantity__u32 length_of__read =
        sizeof(Serialization_Header);

    enum PLATFORM_Read_File_Error error = 
        PLATFORM_read_file(
                p_PLATFORM_file_system_context,
                (u8*)&p_item_stack->_serialization_header, 
                &length_of__read, 
                1, 
                p_file_handler);
    if (error) {
        debug_error("deserialize_item_stack, failed error: %d", error);
        return;
    }

    if (length_of__read
            != sizeof(Serialization_Header)) {
        debug_error("deserialize_item_stack, bad read length: %d/%d", 
                length_of__read,
                sizeof(Serialization_Header));
        return;
    }

    struct {
        enum Item_Kind the_kind_of__item;
        Quantity__u8 quantity_of__items;
        Quantity__u8 max_quantity_of__items;
    } field;

    Quantity__u32 length_of__read__expected =
        length_of__read =
        sizeof(field);

    error = PLATFORM_read_file(
                p_PLATFORM_file_system_context,
                (u8*)&field, 
                &length_of__read, 
                1, 
                p_file_handler);
    if (error) {
        debug_error("deserialize_item_stack, error: %d", error);
        return;
    }

    if (length_of__read
            != length_of__read__expected) {
        debug_error("deserialize_item_stack, bad read length: %d/%d", 
                length_of__read,
                length_of__read__expected);
        return;
    }

    p_item_stack->item =
        get_item_from__item_manager(
                p_item_manager,
                field.the_kind_of__item);
    p_item_stack->quantity_of__items =
        field.quantity_of__items;
    p_item_stack->max_quantity_of__items =
        field.max_quantity_of__items;
}

void set_item_stack(
        Item_Stack *p_item_stack,
        Item item,
        Quantity__u32 quantity_of__items,
        Quantity__u32 max_quantity_of__items) {
#ifndef NDEBUG
    if (!p_item_stack) {
        debug_abort("set_item_stack, p_item_stack is null.");
        return;
    }
#endif
    p_item_stack->item = item;
    p_item_stack->quantity_of__items =
        quantity_of__items;
    p_item_stack->max_quantity_of__items =
        max_quantity_of__items;
}

void merge_p_item_stacks(
        Item_Stack *p_item_stack__source,
        Item_Stack *p_item_stack__destination) {
#ifndef NDEBUG
    if (!p_item_stack__source) {
        debug_abort("merge_p_item_stacks, p_item_stack__source is null.");
        return;
    }
    if (!p_item_stack__destination) {
        debug_abort("merge_p_item_stacks, p_item_stack__destination is null.");
        return;
    }
#endif
    Quantity__u16 quantity_of__total_items =
        p_item_stack__destination->quantity_of__items
        + p_item_stack__source->quantity_of__items
        ;
    Quantity__u8 quantity_of__items_overflowed =
        (quantity_of__total_items
         > p_item_stack__destination->max_quantity_of__items)
        ? quantity_of__total_items 
            - p_item_stack__destination->max_quantity_of__items
        : 0
        ;

    p_item_stack__destination->quantity_of__items =
        add_u8__clamped(
                p_item_stack__destination->quantity_of__items, 
                p_item_stack__source->quantity_of__items, 
                p_item_stack__destination->max_quantity_of__items);

    p_item_stack__source->quantity_of__items =
        subtract_u8__no_overflow(
                p_item_stack__source->quantity_of__items, 
                p_item_stack__source->quantity_of__items
                - quantity_of__items_overflowed);

    if (p_item_stack__source->quantity_of__items
            == 0) {
        initialize_item_stack_as__empty(
                p_item_stack__source,
                p_item_stack__source->_serialization_header.uuid);
    }
}

bool resolve_item_stack__merge_or_swap(
        Item_Stack *p_item_stack__source,
        Item_Stack *p_item_stack__destination) {
#ifndef NDEBUG
    if (!p_item_stack__source) {
        debug_abort("resolve_item_stack__merge_or_swap, p_item_stack__source is null.");
        return false;
    }
    if (!p_item_stack__destination) {
        debug_abort("resolve_item_stack__merge_or_swap, p_item_stack__destination is null.");
        return false;
    }
#endif
    if (is_p_item_stacks_the_same__item_kind(
                p_item_stack__source, 
                p_item_stack__destination)) {
        merge_p_item_stacks(
                p_item_stack__source, 
                p_item_stack__destination);
        return false;
    }
    // different item_kinds, perform a swap.
    Item_Stack p_item_stack__tmp =
            *p_item_stack__source;

    *p_item_stack__source =
        *p_item_stack__destination;
    p_item_stack__source
        ->_serialization_header.uuid =
        p_item_stack__tmp
        ._serialization_header.uuid;

    p_item_stack__tmp
        ._serialization_header.uuid =
        p_item_stack__destination
        ->_serialization_header.uuid;

    *p_item_stack__destination =
        p_item_stack__tmp;
    p_item_stack__destination
        ->_serialization_header.uuid =
        p_item_stack__destination
        ->_serialization_header.uuid;

    return true;
}

Quantity__u32 remove_quantity_of_items_from__item_stack(
        Item_Stack *p_item_stack,
        Quantity__u8 quantity_of__items_to__remove) {
#ifndef NDEBUG
    if (!p_item_stack) {
        debug_abort("remove_quantity_of_items_from__item_stack, p_item_stack is null.");
        return quantity_of__items_to__remove;
    }
#endif
    Quantity__u32 quantity_of__items_in__item_stack =
        get_quantity_of__items_in__item_stack(
                p_item_stack);
    Quantity__u32 quantity_of__items_remaining_to__remove =
        (get_quantity_of__items_in__item_stack(
                p_item_stack)
            < quantity_of__items_to__remove)
        ? quantity_of__items_to__remove
            - quantity_of__items_in__item_stack
        : 0
        ;

    p_item_stack->quantity_of__items =
        subtract_u8__no_overflow(
                p_item_stack->quantity_of__items, 
                quantity_of__items_to__remove);

    if (p_item_stack->quantity_of__items == 0)
        p_item_stack->item = get_item__empty();

    return quantity_of__items_remaining_to__remove;
}
