#include "defines.h"
#include "defines_weak.h"
#include <inventory/item.h>

const Item _item_void = { 0 };

void initialize_item(
        Item *p_item,
        enum Item_Kind the_kind_of__item) {
    memset(p_item, 0, sizeof(Item));
    p_item->the_kind_of_item__this_item_is = 
        the_kind_of__item;
}

void initialize_item_as__empty(
        Item *p_item) {
    *p_item = _item_void;
}

Item get_item__empty() {
    return _item_void;
}

