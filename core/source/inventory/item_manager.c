#include "inventory/item_manager.h"
#include "defines_weak.h"
#include "inventory/item.h"

void initialize_item_manager(
        Item_Manager *p_item_manager) {
    for (Index__u32 index_of__item_template = 0;
            index_of__item_template
            < (u16)Item_Kind__Unknown;
            index_of__item_template++) {
        p_item_manager->item_templates[index_of__item_template] =
            get_item__empty();
    }
}

Item get_item_from__item_manager(
        Item_Manager *p_item_manager,
        enum Item_Kind the_kind_of__item) {
#ifndef NDEBUG
    if (the_kind_of__item >= Item_Kind__Unknown) {
        debug_error("get_item_from__item_manager, out of bounds: %d",
                the_kind_of__item);
        return get_item__empty();
    }
#endif
    return p_item_manager->item_templates[the_kind_of__item];
}

void register_core_items_into__item_manager(
        Item_Manager *p_item_manager) {
    debug_abort("register_core_items_into__item_manager, impl");
}
