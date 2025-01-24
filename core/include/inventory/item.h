#ifndef ITEM_H
#define ITEM_H

#include "defines_weak.h"
#include <defines.h>

void initialize_item(
        Item *p_item,
        enum Item_Kind the_kind_of__item);

void initialize_item_as__empty(
        Item *p_item);

Item get_item__empty();

static inline
Item_Kind get_item_kind_of__item(
        Item *p_item) {
    return p_item->the_kind_of_item__this_item_is;
}

static inline
bool is_p_item__empty(
        Item *p_item) {
    return p_item->the_kind_of_item__this_item_is
        == Item_Kind__None;
}

#endif
